"""Source-aware mathematical geometry overrides for selected KEUM concepts.

Every override is a documented *interpretive* geometric construction, not a
claim that its parameters were recovered exactly from the original diagrams.
Other concepts retain their generic family representation.
"""
from __future__ import annotations
import math

TAU=2*math.pi
OVERRIDES={
 3:("density-matrix",15),
 4:("density-shells",5),
 21:("kathara",12),
 22:("kathara-signets",12),
 28:("lotus-arcs",24),
 35:("lotus-arcs",12),
 41:("double-tetrahedron",8),
 43:("double-tetrahedron",8),
 123:("hova",1),
 124:("hova",2),
 125:("hova",3),
 126:("hova",4),
 127:("hova",5),
 171:("double-tetrahedron",8),
 195:("lotus-arcs",6),
 279:("lotus-arcs",24),
 281:("lotus-points",24),
 284:("density-shells",5),
 321:("fire-letter-grid",144),
}

def available():
    return {k:{"construction":v[0],"parameter":v[1]} for k,v in OVERRIDES.items()}

def _round(x):return round(float(x),6)

def specialize(model):
    cid=model["id"]
    if cid not in OVERRIDES:return model
    kind,count=OVERRIDES[cid]
    t=model["time"]
    phase=model["parameters"]["phase"]+.1*t
    nodes=[];edges=[]
    def node(name,x,y,z=0,role="symbol"):
        nodes.append({"id":str(name),"position":[_round(x),_round(y),_round(z)],"role":role})
    def edge(a,b,role="connection"):
        edges.append({"source":str(a),"target":str(b),"role":role})
    def ring(prefix,n,r,z=0,offset=0):
        for i in range(n):
            a=TAU*i/n+offset
            node(f"{prefix}{i}",r*math.cos(a),r*math.sin(a),z)
            if i:edge(f"{prefix}{i-1}",f"{prefix}{i}","ring")
        edge(f"{prefix}{n-1}",f"{prefix}0","ring")
    if kind in ("density-matrix","density-shells","hova"):
        levels=5 if kind!="hova" else 1
        for k in range(levels):
            density=count if kind=="hova" else k+1
            ring(f"d{density}_",3 if kind=="density-matrix" else 12,1.0+.65*density,z=.35*density)
            if kind=="density-matrix":
                for i in range(3):node(f"label{density}_{i}",-.5+i*.5,0,density,"dimension-label")
        if kind=="density-matrix":
            # Explicit 15 unique dimension-label nodes, not 15 physical dimensions.
            assert sum(n["role"]=="dimension-label" for n in nodes)==15
    elif kind in ("kathara","kathara-signets"):
        pts=[(0,-4.5),(0,-3.3),(-2,-2.4),(2,-2.4),(0,-1.3),(-2,0),(2,0),(0,1.1),(-2,2.3),(2,2.3),(0,3.5),(0,4.6)]
        for i,(x,y) in enumerate(pts):node(f"K{i+1}",x,y,role="signet")
        pairs=[(1,2),(2,3),(2,4),(3,4),(3,5),(4,5),(3,6),(4,7),(5,6),(5,7),(6,7),(6,8),(7,8),(6,9),(7,10),(8,9),(8,10),(9,10),(9,11),(10,11),(11,12),(9,12),(10,12)]
        for a,b in pairs:edge(f"K{a}",f"K{b}")
    elif kind in ("lotus-arcs","lotus-points"):
        node("axis_top",0,0,2,"axis");node("axis_bottom",0,0,-2,"axis")
        for i in range(count):
            a=TAU*i/count+phase
            for j in range(9):
                u=math.pi*j/8
                x=2*math.sin(u)*math.cos(a);y=2*math.sin(u)*math.sin(a);z=2*math.cos(u)
                node(f"p{i}_{j}",x,y,z,"lotus")
                if j:edge(f"p{i}_{j-1}",f"p{i}_{j}","petal")
            edge("axis_top",f"p{i}_0","axis")
            edge("axis_bottom",f"p{i}_8","axis")
    elif kind=="double-tetrahedron":
        for side,sgn in (("PCM",1),("PKA",-1)):
            a0=sgn*phase
            node(f"{side}A",0,0,sgn*3,"apex")
            for i in range(3):
                a=a0+TAU*i/3
                node(f"{side}{i}",3*math.cos(a),3*math.sin(a),-sgn,"vertex")
                edge(f"{side}A",f"{side}{i}","tetrahedron")
                edge(f"{side}{i}",f"{side}{(i+1)%3}","tetrahedron")
    elif kind=="fire-letter-grid":
        for i in range(12):
            for j in range(12):
                node(f"F{i+1}_{j+1}",i-5.5,j-5.5,0,"code")
                if i:edge(f"F{i}_{j+1}",f"F{i+1}_{j+1}","adjacent")
                if j:edge(f"F{i+1}_{j}",f"F{i+1}_{j+1}","adjacent")
    model={**model,"nodes":nodes,"edges":edges,
           "geometry_status":"interpretive-specific-construction",
           "construction":kind,
           "source_fidelity":"not measured; verify against original diagrams"}
    model["invariants"]={"node_count":len(nodes),"edge_count":len(edges),
                         "finite_coordinates":True}
    return model
