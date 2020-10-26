import logging
import sqlite3

import bs4
import requests
from bs4 import BeautifulSoup, Tag
from lxml import html

DOCUMENT_BASE_DIR = "aws-cdk-ts.docset/Contents/Resources/Documents"
TOC_FILE = f"{DOCUMENT_BASE_DIR}/api/toc.html"


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


db = sqlite3.connect("aws-cdk-ts.docset/Contents/Resources/docSet.dsidx")

db.execute("DELETE FROM searchIndex")

toc_content = open(TOC_FILE, "r").read()
tree = html.fromstring(toc_content)

module_sections = tree.xpath("//div[@id='toc']/ul/li")
for module_section in module_sections:
    # There should be only one link directly under this "li" tag
    module_link = module_section.xpath("a")[0]
    module_path = "api/" + module_link.attrib["href"]
    logger.info(f"Parsing {module_path}")
    module_title = module_link.attrib["title"]
    output_path = f"api/{module_title}_all.html"
    name = module_link.attrib["title"]
    entry_type = "Module"

    soup = BeautifulSoup(
        open(f"{DOCUMENT_BASE_DIR}/{module_path}", "r").read(), "html.parser"
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
        entry_path = f"{DOCUMENT_BASE_DIR}/api/{entry_file}"

        entry_soup = BeautifulSoup(open(entry_path, "r").read(), "html.parser")
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

    output_file = open(f"{DOCUMENT_BASE_DIR}/{output_path}", "w")
    output_file.write(str(soup))
    output_file.close()

    logger.info(f"Wrote to {DOCUMENT_BASE_DIR}/api/{module_title}_all.html")


# entry_links = tree.xpath("//div[@id='toc']/ul/li/ul/li/a")
# for entry_link in entry_links:
#     # import IPython; IPython.embed()
#     # 1/0
#     # print(entry_link.text_content())
#     if "href" not in entry_link.attrib:
#         continue
#     entry_url = entry_link.attrib["href"]
#     entry_file = entry_url.split("#")[0]
#     entry_content = open(f"{DOCUMENT_BASE_DIR}/api/{entry_file}", "r").read()
#     title_element = html.fromstring(entry_content).xpath("//h1/text()")[0]
#     if title_element.startswith("Class"):
#         entry_type = "Class"
#     elif title_element.startswith("Interface"):
#         entry_type = "Interface"
#     elif title_element.startswith("Enum"):
#         entry_type = "Enum"
#     else:
#         print(title_element)
#         raise RuntimeError

#     name = entry_link.text
#     path = "api/" + entry_url
#     print(path)
#     # entry_type = "Module"
#     sql = "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)"
#     db.execute(sql, (name, entry_type, path))

db.commit()
