"""Migrate maverick markdown files to notion database
"""
# %%
import re
import os
import moment
import yaml
import io
from pathlib import Path
from notion.client import NotionClient
from notion.block import PageBlock
from md2notion.upload import upload

token_v2 = 'aacad74d75d148ad206428bee9604b4162ec5edb8ecc5a5a071321a03084fc729dffddf257962a3160fc9176f9026f3693808ef9289258a55b2c4cd62e57857e430b4e5096237b2f1f9ccf2817a5'
db_url = 'https://www.notion.so/alandecode/09902966e4f74e85a516d537e3dac192?v=dc58a92ced1f41d6a1274bb7c4de239f'

# %%
files = []
walker = os.walk('/Users/didi/OneDrive/博客/PandaWiki')
for path, _, filelist in walker:
  for file in filelist:
    if not file.endswith('.md'):
      continue
    files.append(os.path.abspath(os.path.join(path, file)))

# %% Load content
def safe_read(path):
  with open(path, 'r', encoding='utf-8') as f:
    return f.read()
contents = {path: safe_read(path) for path in files}

# %% Build notion cv
client = NotionClient(token_v2=token_v2)
cv = client.get_collection_view(db_url)

# %%
class Metadata(dict):
  """Metadata
  文章以及页面的元数据
  """

  def __init__(self, fr):
    dict.__init__({})
    self["title"] = str(fr.get("title", ""))
    self["slug"] = str(fr.get("slug", self["title"]))
    self["date"] = moment.date(str(fr.get("date", "")))
    self["layout"] = str(fr.get("layout", "post"))
    self["status"] = str(fr.get("status", "publish"))
    self["author"] = str(fr.get("author", ""))
    self["banner"] = str(fr.get("banner", ""))
    self["excerpt"] = str(fr.get("excerpt", ""))
    self["path"] = ""
    self["showfull"] = bool(fr.get("showfull", False))
    self["comment"] = bool(fr.get("comment", True))

    # 解析包含的 tag（无序）
    self["tags"] = fr.get("tags", []) or []

    # 解析包含的类别（有序）
    self["categories"] = fr.get("categories", []) or []
    if len(self["categories"]) == 0:
      self["categories"].append('Default')

def convertImagePath(imagePath, mdFilePath):
  return Path(mdFilePath).parent / Path(imagePath)

# %% 上传所有内容到 Notion
for i, (path, content) in enumerate(contents.items()):
  print(f'\n{i+1}/{len(contents)} {path}')

  # Load metadate and markdown string
  r = re.compile(r'---([\s\S]*?)---')
  m = r.match(content)
  meta = Metadata(yaml.safe_load(m.group(1)))
  text = content[len(m.group(0)):]

  # Write text to a tmp file
  mdFile = io.StringIO(text)
  mdFile.__dict__['name'] = path

  # Add to notion database
  row = cv.collection.add_row()
  row.status = meta['status']
  row.title = meta['title']
  row.slug = meta['slug']
  row.summary = meta['excerpt']
  row.date = meta['date'].date
  tags = set(meta['tags']) | set(meta['categories'])
  tags.add('Migrated')
  tags = [item for item in list(tags) if type(item) is str]
  row.tags = tags
  row.type = meta['layout']

  upload(mdFile, row, imagePathFunc=convertImagePath)
