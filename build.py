import zipfile,re,json,pathlib
root=pathlib.Path('/mnt/data/KEUM_VR')
items={}
with zipfile.ZipFile('/mnt/data/Kathara_Registry_Markdown_49_images.zip') as z:
 for name in z.namelist():
  if not name.endswith('.md') or name in ('README.md','Связи.md','Методология.md','Источники_и_литература.md','Изображения_41-49.md'): continue
  s=z.read(name).decode('utf-8')
  for line in s.splitlines():
   cells=[x.strip() for x in line.split('|')]
   if len(cells)>=7 and cells[1].isdigit():
    i=int(cells[1]);items[i]={'id':i,'name':cells[2],'description':cells[3],'source':cells[4],'category':name.removesuffix('.md').replace('_',' ')}
(root/'data/catalog.json').write_text(json.dumps([items[k] for k in sorted(items)],ensure_ascii=False,indent=2))
print(len(items),list(items.items())[-1])