#!/usr/bin/env python3
"""Source-aware, interpretive SVG studies of four Babbitt plates.
These are vector diagrams derived from visible composition, not pixel-perfect tracings.
Standard library only.
"""
from __future__ import annotations
import argparse,math
from pathlib import Path
from xml.etree import ElementTree as ET

NS="http://www.w3.org/2000/svg"
def tag(root,name,**attrs):return ET.SubElement(root,name,{k.replace("_","-"):str(v) for k,v in attrs.items()})
def base(title):
    s=ET.Element("svg",xmlns=NS,viewBox="0 0 1000 1300",width="1000",height="1300")
    tag(s,"rect",width="1000",height="1300",fill="#f4e8c9")
    tag(s,"text",x="500",y="68",text_anchor="middle",font_size="27",fill="#2c261d").text=title
    return s
def line(s,x1,y1,x2,y2,color="#564b39",w=2):
    tag(s,"line",x1=x1,y1=y1,x2=x2,y2=y2,stroke=color,stroke_width=w)
def circle(s,x,y,r,color="#564b39",w=2):
    tag(s,"circle",cx=x,cy=y,r=r,fill="none",stroke=color,stroke_width=w)
def label(s,x,y,t,size=17):
    tag(s,"text",x=x,y=y,fill="#3e3527",font_size=size,text_anchor="middle").text=t
def polygon(s,pts,color="#564b39",w=2):
    tag(s,"polygon",points=" ".join(f"{x:.3f},{y:.3f}" for x,y in pts),fill="none",stroke=color,stroke_width=w)
def unity():
    s=base("Babbitt · Unity · interpretive geometry")
    for k,(cx,n) in enumerate([(175,3),(500,6),(825,6)]):
        cy=450;radius=125
        polygon(s,[(cx+radius*math.cos(2*math.pi*i/n-math.pi/2),cy+radius*math.sin(2*math.pi*i/n-math.pi/2)) for i in range(n)])
        if k==2:
            for j in range(6):
                a=2*math.pi*j/6
                circle(s,cx+85*math.cos(a),cy+85*math.sin(a),31,"#8a775b")
        label(s,cx,635,["Triangle / C3","Hexagon / C6","Snow crystal / D6"][k])
    for k in range(3):
        cx=250+250*k;cy=930
        for j in range(12):
            a=2*math.pi*j/12
            line(s,cx,cy,cx+(80+18*k)*math.cos(a),cy+(80+18*k)*math.sin(a),"#887253",1.4)
        circle(s,cx,cy,80+18*k)
    label(s,500,1180,"Illustrative redraw — not exact source tracing")
    return s
def curves():
    s=base("Babbitt · Gradation of Direction · interpretive curves")
    for idx,mode in enumerate(["Parabola","Line of Beauty","Line of Grace"]):
        x0=110+idx*290;pts=[]
        for i in range(201):
            t=i/200
            if idx==0:x=x0+220*t;y=450-180*(2*t-1)**2
            elif idx==1:x=x0+110+60*math.sin(2*math.pi*t);y=250+400*t
            else:
                angle=6*math.pi*t;radius=8+100*t
                x=x0+110+radius*math.cos(angle);y=470+radius*math.sin(angle)
            pts.append(f"{x:.2f},{y:.2f}")
        tag(s,"polyline",points=" ".join(pts),fill="none",stroke="#534c3d",stroke_width="3")
        label(s,x0+110,760,mode)
    for k in range(9):
        r=22+16*k
        pts=[]
        for j in range(180):
            t=2*math.pi*j/179
            rad=r*(1+0.09*math.sin(5*t))
            pts.append(f"{500+rad*math.cos(t):.2f},{1010+rad*math.sin(t):.2f}")
        tag(s,"polyline",points=" ".join(pts),fill="none",stroke="#917b57",stroke_width="1.4")
    label(s,500,1220,"Fig. 48–52 motifs · modern parametric reconstruction")
    return s
def solar():
    s=base("Babbitt · Sun–Earth Ether Diagram · historical interpretation")
    tag(s,"path",d="M180 250 Q500 120 820 250",stroke="#7b6a4e",fill="none",stroke_width="4")
    label(s,500,185,"SEGMENT OF THE SUN")
    circle(s,500,890,260);line(s,240,890,760,890)
    label(s,500,900,"THE EARTH")
    for x in [275,380,500,620,725]:
        tag(s,"path",d=f"M{x} 270 Q{x+(500-x)*.45} 540 {500+(x-500)*.12:.2f} 660 Q{500+(x-500)*.45:.2f} 750 {x} 840",stroke="#7b6550",fill="none",stroke_width="2")
    for k in range(6):
        a=math.pi*k/5
        x=500+255*math.cos(a);y=890-255*math.sin(a)
        tag(s,"path",d=f"M{x:.2f} {y:.2f} Q{500+160*math.cos(a):.2f} {780-200*math.sin(a):.2f} 500 660",stroke="#b19a72",fill="none",stroke_width="1.2")
    label(s,500,1210,"Historical ether claims are not established solar physics")
    return s
def corona():
    s=base("Babbitt · Solar Corona / Eclipse · interpretive engraving")
    for cx in [285,715]:
        cy=570
        for j in range(180):
            a=2*math.pi*j/180
            extent=155+45*abs(math.sin(5*a))+30*abs(math.sin(11*a))
            line(s,cx+105*math.cos(a),cy+105*math.sin(a),cx+extent*math.cos(a),cy+extent*math.sin(a),"#9c8867",1)
        tag(s,"circle",cx=cx,cy=cy,r=105,fill="#302a25")
    label(s,285,850,"Eclipse 1858 (historical figure)")
    label(s,715,850,"Eclipse 1860 (historical figure)")
    label(s,500,1130,"Modern schematic, not quantitative coronal observation")
    return s
PRESETS={"unity":unity,"curves":curves,"solar-ether":solar,"corona":corona}
def generate(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    for name,fn in PRESETS.items():
        path=output/(name+".svg")
        path.write_bytes(ET.tostring(fn(),encoding="utf-8",xml_declaration=True))
    return len(PRESETS)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",default="build/babbitt_svg")
    a=p.parse_args();print("generated",generate(a.output),"SVG studies")
