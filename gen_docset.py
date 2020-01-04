import requests
import sqlite3
from lxml import html

DOCUMENT_BASE_DIR = "aws-cdk.docset/Contents/Resources/Documents"
TOC_FILE = f"{DOCUMENT_BASE_DIR}/api/toc.html"


db = sqlite3.connect("aws-cdk.docset/Contents/Resources/docSet.dsidx")

toc_content = open(TOC_FILE, "r").read()
tree = html.fromstring(toc_content)

module_links = tree.xpath("//div[@id='toc']/ul/li/a")
for module_link in module_links:
    path = "api/" + module_link.attrib["href"]
    name = module_link.attrib["title"]
    entry_type = "Module"
    sql = "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)"
    db.execute(sql, (name, entry_type, path))

entry_links = tree.xpath("//div[@id='toc']/ul/li/ul/li/a")
for entry_link in entry_links:
    # import IPython; IPython.embed()
    # 1/0
    # print(entry_link.text_content())
    if "href" not in entry_link.attrib:
        continue
    entry_url = entry_link.attrib["href"]
    entry_file = entry_url.split("#")[0]
    entry_content = open(f"{DOCUMENT_BASE_DIR}/api/{entry_file}", "r").read()
    title_element = html.fromstring(entry_content).xpath("//h1/text()")[0]
    if title_element.startswith("Class"):
        entry_type = "Class"
    elif title_element.startswith("Interface"):
        entry_type = "Interface"
    elif title_element.startswith("Enum"):
        entry_type = "Enum"
    else:
        print(title_element)
        raise RuntimeError

    name = entry_link.text
    path = "api/" + entry_url
    print(path)
    # entry_type = "Module"
    sql = "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)"
    db.execute(sql, (name, entry_type, path))

db.commit()