#!/usr/bin/env python3
"""Deterministic, standard-library SVG illustrations for KEUM Fibonacci concepts."""
from __future__ import annotations
import argparse, math
from pathlib import Path
from xml.etree import ElementTree as ET

PHI=(1+math.sqrt(5))/2
B=2*math.log(PHI)/math.pi
NS="http://www.w3.org/2000/svg"
def fib(n):
    if not isinstance(n,int) or n<0:raise ValueError("n must be a nonnegative integer")
    a,b=0,1
    for _ in range(n):a,b=b,a+b
    return a
def golden_point(theta,a=1):
    r=a*math.exp(B*theta)
    return r*math.cos(theta),r*math.sin(theta)
def root(title):
    svg=ET.Element("svg",xmlns=NS,viewBox="0 0 900 900")
    ET.SubElement(svg,"rect",width="900",height="900",fill="#0c2d27")
    ET.SubElement(svg,"text",x="450",y="52",fill="#e5c36c",font_size="27",text_anchor="middle").text=title
    return svg
def line(svg,x1,y1,x2,y2,stroke="#d9b95f",width=2):
    ET.SubElement(svg,"line",x1=str(x1),y1=str(y1),x2=str(x2),y2=str(y2),stroke=stroke,stroke_width=str(width))
def text(svg,x,y,value):
    ET.SubElement(svg,"text",x=str(x),y=str(y),fill="#e5c36c",font_size="20",text_anchor="middle").text=str(value)
def spiral_svg():
    svg=root("Golden logarithmic spiral")
    theta_max=5*math.pi
    radius_max=math.exp(B*theta_max)
    scale=350/radius_max
    pts=[]
    for i in range(1201):
        t=theta_max*i/1200
        x,y=golden_point(t)
        pts.append(f"{450+x*scale:.3f},{450-y*scale:.3f}")
    ET.SubElement(svg,"polyline",points=" ".join(pts),fill="none",stroke="#f0ce77",stroke_width="4")
    text(svg,450,835,"r(theta) = a exp(2 ln(phi) theta / pi)")
    return svg
def phyllotaxis_svg(n=450):
    svg=root("Golden-angle phyllotaxis — idealized")
    alpha=2*math.pi/PHI**2
    for k in range(n):
        theta=k*alpha
        r=14*math.sqrt(k)
        x,y=450+r*math.cos(theta),465+r*math.sin(theta)
        ET.SubElement(svg,"circle",cx=f"{x:.3f}",cy=f"{y:.3f}",r="3.4",fill="#e4bd68")
    text(svg,450,850,"theta(n)=n*2pi/phi^2; r(n)=c*sqrt(n)")
    return svg
def tiles_svg():
    svg=root("Fibonacci quarter-circle construction")
    # Deterministic outward square placement: adjacent square starts at
    # the current bounding-box side, rotating through four directions.
    squares=[(0,0,1),(1,0,1)]
    for k in range(2,9):
        s=fib(k+1)
        minx=min(x for x,y,z in squares);maxx=max(x+z for x,y,z in squares)
        miny=min(y for x,y,z in squares);maxy=max(y+z for x,y,z in squares)
        side=(k-2)%4
        if side==0: xy=(minx,maxy)
        elif side==1: xy=(minx-s,miny)
        elif side==2: xy=(minx,miny-s)
        else: xy=(maxx,miny)
        squares.append((*xy,s))
    minx=min(x for x,y,z in squares);maxx=max(x+z for x,y,z in squares)
    miny=min(y for x,y,z in squares);maxy=max(y+z for x,y,z in squares)
    scale=min(710/(maxx-minx),710/(maxy-miny))
    offx=450-(minx+maxx)*scale/2
    offy=455-(miny+maxy)*scale/2
    for i,(x,y,s) in enumerate(squares):
        xx=offx+x*scale;yy=offy+y*scale;ss=s*scale
        ET.SubElement(svg,"rect",x=f"{xx:.2f}",y=f"{yy:.2f}",width=f"{ss:.2f}",height=f"{ss:.2f}",fill="none",stroke="#d4b46a",stroke_width="1.5")
        if ss>20:text(svg,xx+ss/2,yy+ss/2,s)
        # An illustrative quarter-circle in each tile; unlike the exact
        # logarithmic spiral, this is a piecewise circular construction.
        cx,cy=[(xx,yy),(xx+ss,yy),(xx+ss,yy+ss),(xx,yy+ss)][i%4]
        a0=[0,90,180,270][i%4]
        pts=[]
        for j in range(41):
            a=math.radians(a0+j*90/40)
            pts.append(f"{cx+ss*math.cos(a):.3f},{cy+ss*math.sin(a):.3f}")
        ET.SubElement(svg,"polyline",points=" ".join(pts),fill="none",stroke="#f0cf80",stroke_width="2.5")
    text(svg,450,850,"Quarter-circle study; not an exact logarithmic spiral")
    return svg
def stages_svg():
    svg=root("Symbolic stages — attributed to Vedana Miller")
    labels=["Intention","Action","Result","Accumulation","Expansion","Multiplication"]
    for i,lbl in enumerate(labels):
        angle=-math.pi/2+2*math.pi*i/len(labels)
        x=450+275*math.cos(angle);y=470+275*math.sin(angle)
        ET.SubElement(svg,"circle",cx=f"{x:.3f}",cy=f"{y:.3f}",r="64",fill="none",stroke="#e5c36c",stroke_width="2")
        text(svg,x,y+6,lbl)
    text(svg,450,835,"Symbolic model only — no demonstrated financial effect")
    return svg
PRESETS={"golden-spiral":spiral_svg,"phyllotaxis":phyllotaxis_svg,"fibonacci-tiles":tiles_svg,"symbolic-stages":stages_svg}
def generate(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    for name,fn in PRESETS.items():
        (output/(name+".svg")).write_bytes(ET.tostring(fn(),encoding="utf-8",xml_declaration=True))
    return len(PRESETS)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",default="build/fibonacci_svg")
    a=p.parse_args();print("generated",generate(a.output),"SVG diagrams")
