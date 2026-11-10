#!/usr/bin/env python3
"""KEUM procedural vector atlas. Standard library only; deterministic SVG output."""
import argparse, math, html, json
from pathlib import Path
from xml.etree import ElementTree as ET
TAU=2*math.pi
PRESETS=('kathara','merkaba','lotus','reuche','crystal','clock','axiotonal','cosmology')
class SVG:
 def __init__(self,size=1000,theme='manuscript',labels=True):
  self.size=size; self.labels=labels; self.theme=theme
  self.fg='#253044' if theme=='manuscript' else '#d8e6ff'; self.bg='#faf9f5' if theme=='manuscript' else '#081121'; self.accent='#a15d38' if theme=='manuscript' else '#64d6d0'; self.muted='#89919b' if theme=='manuscript' else '#587398'
  self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{size}" height="{size}" viewBox="-500 -500 1000 1000" role="img">',f'<rect x="-500" y="-500" width="1000" height="1000" fill="{self.bg}"/>']
 def add(self,s):self.parts.append(s)
 def line(self,a,b,color=None,width=1.3,dash=None,opacity=1):self.add(f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}" stroke="{color or self.fg}" stroke-width="{width}" opacity="{opacity}" '+(f'stroke-dasharray="{dash}" ' if dash else '')+'/>')
 def circle(self,x,y,r,color=None,width=1.4,fill='none',opacity=1):self.add(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" stroke="{color or self.fg}" stroke-width="{width}" fill="{fill}" opacity="{opacity}"/>')
 def path(self,pts,color=None,width=1.3,close=False,opacity=1):
  if not pts:return
  d='M '+' L '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+(' Z' if close else '')
  self.add(f'<path d="{d}" fill="none" stroke="{color or self.fg}" stroke-width="{width}" opacity="{opacity}"/>')
 def text(self,x,y,t,size=13,color=None):
  if self.labels:self.add(f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" fill="{color or self.fg}">{html.escape(str(t))}</text>')
 def finish(self,title,meta):
  self.parts.insert(1,f'<title>{html.escape(title)}</title><desc>{html.escape(json.dumps(meta,ensure_ascii=False))}</desc>')
  self.text(0,-460,title,22);self.text(0,466,'KEUM VECTOR ENGINE · SYMBOLIC / NON-EMPIRICAL',11,self.muted)
  return '\n'.join(self.parts+['</svg>'])
def polar(r,a,c=(0,0)):return(c[0]+r*math.cos(a),c[1]+r*math.sin(a))
def ring(s,n,r,phase=-math.pi/2,nums=False,c=(0,0),node=10):
 pts=[polar(r,phase+TAU*i/n,c) for i in range(n)]
 for i,(x,y) in enumerate(pts):s.circle(x,y,node,fill=s.bg);s.text(x,y+4,i+1,10) if nums else None
 return pts
def axes(s,r=390):s.line((-r,0),(r,0),s.muted,.8,'6,6');s.line((0,-r),(0,r),s.muted,.8,'6,6')
def kathara(s,complexity):
 axes(s); pts=[(-140,315),(0,335),(-130,235),(130,235),(0,165),(-145,65),(145,65),(0,-35),(-145,-140),(145,-140),(0,-230),(0,-335)]
 edges=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3),(2,4),(3,4),(2,5),(3,6),(4,5),(4,6),(5,6),(5,7),(6,7),(5,8),(6,9),(7,8),(7,9),(8,9),(8,10),(9,10),(10,11),(8,11),(9,11)]
 if complexity>1:edges +=[(i,j) for i in range(12) for j in range(i+2,12) if (i+j)%3==0]
 for i,j in edges:s.line(pts[i],pts[j],width=1.2 if (i,j) in edges[:25] else .6,opacity=.8)
 for i,(x,y) in enumerate(pts):s.circle(x,y,16,s.accent,1.7,fill=s.bg);s.text(x,y+4,i+1,12)
 s.text(0,400,'12-CENTER KATHARA / GRAPH MODEL',13)
def merkaba(s,complexity):
 axes(s);s.circle(0,0,360,s.muted)
 for r in [140,235,315]:
  for shift in (0,math.pi):
   pts=[polar(r,-math.pi/2+shift+TAU*i/3) for i in range(3)];s.path(pts,s.accent if shift else s.fg,2.3,True)
  if complexity>1:s.circle(0,0,r,s.muted,.7)
 for i in range(12):
  a=TAU*i/12;s.line(polar(90,a),polar(330,a),s.muted,.7,opacity=.7)
 s.text(0,405,'PCM ↻ / PKA ↺ · COUNTER-ROTATION',13)
def lotus(s,complexity):
 axes(s); n=24 if complexity>=2 else 12
 for i in range(n):
  a=TAU*i/n; c=polar(190,a)
  s.circle(*c,190,s.accent if i%2 else s.fg,.85,opacity=.7)
 for r in [95,190,380]:s.circle(0,0,r,s.muted,1)
 ring(s,12,310,nums=True,node=11);s.text(0,425,f'{n} LOTUS ARCS / INTERSECTING CIRCLES',13)
def reuche(s,complexity):
 axes(s); ring(s,12,300,nums=True)
 for i in range(12):
  a=TAU*i/12; pts=[polar(22+t*2.8,a+(.015 if i%2 else -.015)*t) for t in range(105)]
  s.path(pts,s.accent if i%2 else s.fg,1.4)
  s.circle(*polar(300,a),23,s.muted,.8)
 for r in [100,210,320]:s.circle(0,0,r,s.muted,.7)
 s.text(0,420,'REUCHE · 12 RADIAL VORTEX CHANNELS',13)
def crystal(s,complexity):
 axes(s); levels=5 if complexity>=2 else 3
 for j in range(levels):
  y=(j-(levels-1)/2)*135; pts=[polar(110,a,(0,y)) for a in [TAU*i/12 for i in range(12)]]
  s.path(pts,s.fg,1.1,True)
  for i in range(12):
   s.line(pts[i],pts[(i+5)%12],s.muted,.55,opacity=.55)
   s.circle(*pts[i],5,s.accent,fill=s.bg)
  if j:s.line((0,y-135),(0,y),s.accent,2)
 s.text(0,420,f'{levels} DENSITY LAYERS · CRYSTAL LIGHT GRID',13)
def clock(s,complexity):
 axes(s)
 for r in [90,165,250,345]:s.circle(0,0,r,s.muted,1)
 for i in range(48):
  a=-math.pi/2+TAU*i/48;s.line(polar(334 if i%4 else 322,a),polar(350,a),width=1.2 if i%4==0 else .6)
  if i%4==0:s.text(*polar(372,a),i//4+1,11)
 for i in range(12):
  a=-math.pi/2+TAU*i/12;s.line(polar(90,a),polar(250,a),s.accent,1)
 ring(s,12,165,nums=True,node=12);s.text(0,435,'12 PHASES · 48 ANGULAR MARKERS',13)
def axiotonal(s,complexity):
 axes(s);s.circle(0,0,350,s.muted)
 for i in range(12):
  a=TAU*i/12;pts=[polar(350*math.sin(math.pi*j/120),a) for j in range(121)]
  s.line(polar(350,a),polar(350,a+math.pi),s.accent if i%2 else s.fg,.9,opacity=.65)
  for j in range(1,5):s.circle(*polar(350*j/5,a),4,s.accent,fill=s.bg)
 for lat in [-240,-140,0,140,240]:
  rx=math.sqrt(max(0,350**2-lat**2));s.add(f'<ellipse cx="0" cy="{lat}" rx="{rx:.2f}" ry="{rx*.22:.2f}" stroke="{s.muted}" stroke-width=".9" fill="none"/>')
 s.text(0,420,'12 AXIOTONAL / 12 MERIDIAN · SPHERE',13)
def cosmology(s,complexity):
 axes(s)
 for k in range(5,0,-1):
  r=65*k;s.circle(0,0,r,s.accent if k%2 else s.fg,1.4);s.text(0,-r+17,f'D{k}',11)
 for i in range(15):
  a=-math.pi/2+TAU*i/15;s.line(polar(50,a),polar(325,a),s.muted,.6,opacity=.6)
  s.circle(*polar(340,a),8,s.accent,fill=s.bg)
 s.text(0,420,'15 SYMBOLIC DIMENSIONS / 5 DENSITIES',13)
DRAW=dict(zip(PRESETS,[kathara,merkaba,lotus,reuche,crystal,clock,axiotonal,cosmology]))
def generate(preset='kathara',size=1000,theme='manuscript',complexity=2,labels=True):
 if preset not in DRAW:raise ValueError(f'Unknown preset {preset}')
 s=SVG(size,theme,labels);DRAW[preset](s,complexity)
 return s.finish(preset.upper(),{'preset':preset,'size':size,'theme':theme,'complexity':complexity,'symbolic':True})
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--preset',choices=(*PRESETS,'all'),default='all');ap.add_argument('--size',type=int,default=1000);ap.add_argument('--theme',choices=('manuscript','dark'),default='manuscript');ap.add_argument('--complexity',type=int,choices=(1,2,3),default=2);ap.add_argument('--no-labels',action='store_true');ap.add_argument('--output',default='examples');a=ap.parse_args()
 out=Path(a.output);presets=PRESETS if a.preset=='all' else [a.preset]
 if len(presets)>1 or out.suffix.lower()!='.svg':out.mkdir(parents=True,exist_ok=True)
 for p in presets:
  target=out/f'{p}.svg' if out.is_dir() else out;target.write_text(generate(p,a.size,a.theme,a.complexity,not a.no_labels),encoding='utf-8');ET.parse(target);print(target)
if __name__=='__main__':main()