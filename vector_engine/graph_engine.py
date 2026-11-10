#!/usr/bin/env python3
"""Deterministic shared graph schema -> editable SVG, 3D glTF/GLB, JSON.
All geometry is a formal symbolic reconstruction, not physical evidence.
"""
import argparse, json, math, html, struct, base64
from pathlib import Path
from xml.etree import ElementTree as ET
TAU=2*math.pi
CATEGORIES={'kathara':21,'merkaba':41,'lotus':28,'reuche':31,'crystal':25,'clock':73,'axiotonal':263,'cosmology':3,'hova':123,'flame':201,'vortex':258,'shield':23}
COLORS=['#69c8ed','#f3a96c','#c6a2ed','#8de0b2','#f2d280']
def node(id,x,y,z=0,kind='signet',entity_id=None,label=None,group='base'):
 return dict(id=str(id),position=[round(x,5),round(y,5),round(z,5)],kind=kind,entity_id=entity_id,label=label or str(id),group=group)
def edge(a,b,kind='connection',weight=1,group='base'):
 return dict(source=str(a),target=str(b),kind=kind,weight=weight,group=group)
def graph(preset='kathara',complexity=2,seed=0):
 if preset not in CATEGORIES:raise ValueError(preset)
 nodes=[];edges=[];annotations=[]
 def add(n):nodes.append(n)
 def link(a,b,kind='connection',weight=1,group='base'):edges.append(edge(a,b,kind,weight,group))
 def ring(prefix,count,r,y=0,phase=-math.pi/2,kind='signet',eid=None,group='base'):
  ids=[]
  for i in range(count):
   a=phase+TAU*i/count;id=f'{prefix}{i+1}';add(node(id,r*math.cos(a),r*math.sin(a),y,kind,eid or CATEGORIES[preset],str(i+1),group));ids.append(id)
  for i in range(count):link(ids[i],ids[(i+1)%count],'ring',.65,group)
  return ids
 if preset=='kathara':
  pts=[(0,-4.5),(0,-3.3),(-2,-2.4),(2,-2.4),(0,-1.3),(-2,0),(2,0),(0,1.1),(-2,2.3),(2,2.3),(0,3.5),(0,4.6)]
  for i,(x,y) in enumerate(pts,1):add(node(f'K{i}',x,y,kind='signet',entity_id=21,label=str(i)))
  pairs=[(1,2),(2,3),(2,4),(3,4),(3,5),(4,5),(3,6),(4,7),(5,6),(5,7),(6,7),(6,8),(7,8),(6,9),(7,10),(8,9),(8,10),(9,10),(9,11),(10,11),(11,12),(9,12),(10,12),(3,7),(4,6)]
  if complexity>1:pairs +=[(i,j) for i in range(1,13) for j in range(i+2,13) if (i+j)%5==0]
  for a,b in sorted(set(pairs)):link(f'K{a}',f'K{b}')
 elif preset in ('merkaba','vortex'):
  for side,sign in [('PCM',1),('PKA',-1)]:
   for i in range(3):
    a=TAU*i/3;add(node(f'{side}{i}',3.7*math.cos(a),3.7*math.sin(a),sign*1.5,'vertex',41,side,'PCM' if sign==1 else 'PKA'))
   add(node(f'{side}T',0,0,-sign*4,'apex',41,side,side))
   for i in range(3):link(f'{side}{i}',f'{side}{(i+1)%3}','frame',1,side);link(f'{side}{i}',f'{side}T','frame',1,side)
  ring('V',12,4.8,kind='vortex',eid=258,group='vortex')
 elif preset in ('lotus','reuche','axiotonal','clock'):
  n=24 if preset in ('lotus','reuche') else 12
  ids=ring('L',n,4.1,kind='lotus' if preset=='lotus' else 'vortex',eid=CATEGORIES[preset])
  add(node('C',0,0,kind='core',entity_id=CATEGORIES[preset],label='0'))
  for i,id in enumerate(ids):link('C',id,'radial',.7)
  if complexity>1:
   for i in range(n):link(ids[i],ids[(i+n//3)%n],'chord',.4)
 elif preset in ('crystal','shield','hova','flame','cosmology'):
  levels=5 if preset!='crystal' else 3
  for l in range(levels):
   ids=ring(f'D{l+1}_',12,1.25+(.35*l),y=(l-(levels-1)/2)*1.7,kind='density',eid=CATEGORIES[preset],group=f'D{l+1}')
   if l:
    for i in range(12):link(f'D{l}_{i+1}',ids[i],'interlayer',.6,'cross')
   if complexity>1:
    for i in range(12):link(ids[i],ids[(i+5)%12],'chord',.3,f'D{l+1}')
 return {'schema':'keum.graph.v1','preset':preset,'seed':seed,'complexity':complexity,'units':'normalized','source_status':'symbolic reconstruction','nodes':nodes,'edges':edges,'annotations':annotations,'metadata':{'entity_id':CATEGORIES[preset],'source_images':'1–49 (conceptual mapping; not exact digitization)','coordinate_system':'right-handed; z-up','license_note':'Original geometry generated from formal rules'}}
def validate(g):
 assert g.get('schema')=='keum.graph.v1'
 ids=[n['id'] for n in g['nodes']];assert len(ids)==len(set(ids))
 for n in g['nodes']:
  assert len(n['position'])==3 and all(math.isfinite(v) and abs(v)<1e6 for v in n['position'])
 for e in g['edges']:assert e['source'] in ids and e['target'] in ids and e['source']!=e['target']
 return True
def svg(g,size=1200,theme='manuscript',labels=True,projection='xy'):
 validate(g);fg='#24324a' if theme=='manuscript' else '#c9e6ff';bg='#fbfaf6' if theme=='manuscript' else '#071222'; accent='#bd704b' if theme=='manuscript' else '#5ce0cc'; muted='#71839a'
 positions={n['id']:n['position'] for n in g['nodes']};axes={'xy':(0,1),'xz':(0,2),'yz':(1,2)};ix,iy=axes[projection]
 points=[(p[ix],p[iy]) for p in positions.values()];ext=max([abs(v) for p in points for v in p]+[1]);scale=445/ext
 def xy(p):return round(p[ix]*scale,3),round(-p[iy]*scale,3)
 out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="-500 -500 1000 1000">',f'<title>KEUM {html.escape(g["preset"])}</title>',f'<desc>{html.escape(json.dumps({"schema":g["schema"],"symbolic":True,"nodes":len(g["nodes"]),"edges":len(g["edges"])},ensure_ascii=False))}</desc>',f'<rect x="-500" y="-500" width="1000" height="1000" fill="{bg}"/>','<g id="edges">']
 for i,e in enumerate(g['edges']):
  x1,y1=xy(positions[e['source']]);x2,y2=xy(positions[e['target']]);dash=' stroke-dasharray="5 4"' if e['kind']=='interlayer' else ''
  out.append(f'<line id="edge-{i}" data-kind="{html.escape(e["kind"])}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{muted if e["kind"]=="chord" else fg}" stroke-width="{1.7*e["weight"]:.2f}" opacity=".74"{dash}/>')
 out.append('</g><g id="nodes">')
 for n in g['nodes']:
  x,y=xy(n['position']);id=html.escape(n['id'],quote=True);lab=html.escape(str(n['label']));out.append(f'<g id="node-{id}" data-entity-id="{n.get("entity_id") or ""}" data-kind="{html.escape(n["kind"])}"><circle cx="{x}" cy="{y}" r="10" fill="{bg}" stroke="{accent}" stroke-width="2"/>')
  if labels:out.append(f'<text x="{x}" y="{y+3.4}" text-anchor="middle" font-family="sans-serif" font-size="9" fill="{fg}">{lab}</text>')
  out.append('</g>')
 out.extend(['</g>',f'<text x="0" y="-467" text-anchor="middle" font-family="sans-serif" font-size="22" fill="{fg}">KEUM · {html.escape(g["preset"].upper())}</text>',f'<text x="0" y="480" text-anchor="middle" font-family="sans-serif" font-size="11" fill="{muted}">SYMBOLIC MODEL · NOT EMPIRICAL PHYSICS</text>','</svg>']);return '\n'.join(out)
def gltf(g):
 """Portable glTF 2.0 LINE segments, one buffer embedded as base64."""
 validate(g);lookup={n['id']:n['position'] for n in g['nodes']};vertices=[];colors=[]
 for e in g['edges']:
  for id in [e['source'],e['target']]:
   x,y,z=lookup[id];vertices.extend((x,y,z));colors.extend((.45,.78,.95))
 if not vertices:vertices=[0.,0.,0.];colors=[.45,.78,.95]
 count=len(vertices)//3;pos=struct.pack('<%sf'%len(vertices),*vertices);col=struct.pack('<%sf'%len(colors),*colors);data=pos+col
 return {'asset':{'version':'2.0','generator':'KEUM Graph Engine v2'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0,'name':g['preset']}],'meshes':[{'primitives':[{'attributes':{'POSITION':0,'COLOR_0':1},'mode':1,'material':0}]}],'materials':[{'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':0,'roughnessFactor':1}}],'buffers':[{'uri':'data:application/octet-stream;base64,'+base64.b64encode(data).decode(),'byteLength':len(data)}],'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':len(pos),'target':34962},{'buffer':0,'byteOffset':len(pos),'byteLength':len(col),'target':34962}],'accessors':[{'bufferView':0,'componentType':5126,'count':count,'type':'VEC3','min':[min(vertices[i::3]) for i in range(3)],'max':[max(vertices[i::3]) for i in range(3)]},{'bufferView':1,'componentType':5126,'count':count,'type':'VEC3'}],'extras':{'symbolic':True,'entity_id':g['metadata']['entity_id']}}
def main():
 p=argparse.ArgumentParser();p.add_argument('--preset',choices=tuple(CATEGORIES)+('all',),default='all');p.add_argument('--output',default='graph_exports');p.add_argument('--complexity',type=int,choices=[1,2,3],default=2);p.add_argument('--theme',choices=['manuscript','dark'],default='manuscript');p.add_argument('--seed',type=int,default=0);a=p.parse_args();d=Path(a.output);d.mkdir(parents=True,exist_ok=True)
 for preset in CATEGORIES if a.preset=='all' else [a.preset]:
  g=graph(preset,a.complexity,a.seed);validate(g);(d/f'{preset}.json').write_text(json.dumps(g,ensure_ascii=False,indent=2));(d/f'{preset}.gltf').write_text(json.dumps(gltf(g)));(d/f'{preset}.svg').write_text(svg(g,theme=a.theme));ET.parse(d/f'{preset}.svg');print(preset,len(g['nodes']),len(g['edges']))
if __name__=='__main__':main()