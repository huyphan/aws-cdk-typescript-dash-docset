import logging
import sqlite3
import string
from collections import defaultdict

import bs4
import requests
from bs4 import BeautifulSoup, Tag
from lxml import html

SOURCE_DOCUMENT_BASE_DIR = "tmp/cdk/api/latest/typescript/"
TOC_FILE = f"{SOURCE_DOCUMENT_BASE_DIR}/api/toc.html"
API_TOC_FILE = "tmp/aws-construct-library.html"
DESTINATION_DOCUMENT_BASE_DIR = "aws-cdk-ts.docset/Contents/Resources/Documents"
DOCSET_DATABASE = "aws-cdk-ts.docset/Contents/Resources/docSet.dsidx"


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


db = sqlite3.connect(DOCSET_DATABASE, isolation_level=None)
db.isolation_level = None

db.execute("DELETE FROM searchIndex")
db.execute("VACUUM")


# The TS docs does not have a clear distinction between Constructs, Class, Interface, etc. 
# So we get that information from the main API doc
toc_content = open(API_TOC_FILE, "r").read()
tree = html.fromstring(toc_content)

module_map = defaultdict(dict)

module_sections = tree.xpath("//div[@id='docsNav']//div[@class='navGroup']")
for module_section in module_sections:
    module_title = module_section.xpath(
        "h3[contains(@class, 'navGroupCategoryTitle')]"
    )[0].text
    module_title = "".join(filter(lambda x: x in string.printable, module_title))
    entries = module_section.xpath(".//a[@class='navItem']")
    for entry in entries:
        if entry.text in ["Welcome", "Overview"]:
            continue
        entry_type_text = (
            entry.getparent().getparent().getparent().xpath("./h4")[0].text
        )
        if entry_type_text in ["CloudFormation Resources", "Constructs"]:
            entry_type = "Component"
        elif entry_type_text in ["Classes"]:
            entry_type = "Class"
        elif entry_type_text in ["Structs"]:
            entry_type = "Struct"
        elif entry_type_text in ["Enums"]:
            entry_type = "Enum"
        elif entry_type_text in ["Interfaces", "CloudFormation Property Types"]:
            entry_type = "Interface"
        else:
            raise Exception(f"Not recognize entry type for '{entry_type_text}'")

        module_map[module_title][entry.text] = entry_type

toc_content = open(TOC_FILE, "r").read()
tree = html.fromstring(toc_content)

module_sections = tree.xpath("//div[@id='toc']/ul/li")
for module_section in module_sections:
    # There should be only one link directly under this "li" tag
    module_link = module_section.xpath("a")[0]
    module_path = "api/" + module_link.attrib["href"]
    logger.info(f"Parsing {module_path}")
    module_title = module_link.attrib["title"]
    output_path = f"api/{module_title}.html"
    name = module_link.attrib["title"]
    entry_type = "Module"

    soup = BeautifulSoup(
        open(f"{SOURCE_DOCUMENT_BASE_DIR}/{module_path}", "r").read(), "html.parser"
    )
    # Remove the annoying header
    soup.find("header").decompose()

    article_tag = soup.find("article")
    article_parent = article_tag.parent

    sql = "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)"
    db.execute(sql, (name, entry_type, output_path))

    # Find entry links
    entries = module_section.xpath("ul/li/a")
    for entry in entries:
        entry_url = entry.attrib.get("href")
        if not entry_url:
            continue

        entry_title = entry.attrib.get("title")
        entry_file = entry_url.split("#")[0]
        entry_path = f"{SOURCE_DOCUMENT_BASE_DIR}/api/{entry_file}"

        entry_soup = BeautifulSoup(open(entry_path, "r").read(), "html.parser")
        try:
            entry_type = module_map[module_title][entry_title]
        except KeyError:
            entry_type = entry_soup.title.text.split()[0]
        entry_article_tag = entry_soup.find("article")
        entry_id = entry_article_tag.attrs["data-uid"]
        anchor_tag = soup.new_tag(
            "a",
            attrs={
                "name": f"//apple_ref/cpp/{entry_type}/{entry_title}",
                "class": "dashAnchor",
                "id": entry_id
            },
        )

        article_parent.insert(len(list(article_parent.children)), anchor_tag)
        article_parent.insert(len(list(article_parent.children)), entry_article_tag)

        for link in article_parent.findAll('a'):
            if link.get('href') and '#' in link.get('href'):
                link['href'] = "#" + link['href'].split('#')[-1]

        sql = "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)"
        db.execute(sql, (entry_title, entry_type, output_path + "#" + entry_id))

    output_file = open(f"{DESTINATION_DOCUMENT_BASE_DIR}/{output_path}", "w")
    output_file.write(str(soup))
    output_file.close()

    logger.info(f"Wrote to {DESTINATION_DOCUMENT_BASE_DIR}/{output_path}")

db.commit()
