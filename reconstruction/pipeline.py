#!/usr/bin/env python3
"""KEUM source-image geometry candidate extraction and auditable QA.

Uses OpenCV for image primitives, not OCR. All detections are UNVERIFIED
candidates; never infer scientific validity or exact diagram reconstruction.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re
from pathlib import Path
import cv2
import numpy as np

VERSION = 'keum.reconstruction.v1'

def list_sources(root: Path):
    paths = sorted((p for p in root.iterdir() if p.suffix.lower() in ('.jpg','.jpeg','.png','.webp')), key=lambda p: (int(re.search(r'\d+',p.stem).group()) if re.search(r'\d+',p.stem) else 10**10,p.name))
    if not paths: raise ValueError(f'No raster source images in {root}')
    return paths

def normalize(image, max_side=1100):
    h,w=image.shape[:2]; scale=min(1.,max_side/max(h,w))
    return cv2.resize(image,(max(1,round(w*scale)),max(1,round(h*scale))),interpolation=cv2.INTER_AREA) if scale<1 else image.copy(),scale

def detect(image, max_lines=140, max_circles=50):
    h,w=image.shape[:2]
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gray=cv2.createCLAHE(clipLimit=2.,tileGridSize=(8,8)).apply(gray)
    blur=cv2.GaussianBlur(gray,(5,5),0)
    edges=cv2.Canny(blur,60,150,L2gradient=True)
    length=max(20,round(min(h,w)*.075))
    raw=cv2.HoughLinesP(edges,1,np.pi/180,threshold=max(35,round(min(h,w)*.065)),minLineLength=length,maxLineGap=10)
    lines=[]
    if raw is not None:
        for x1,y1,x2,y2 in raw.reshape(-1,4):
            length=float(math.hypot(x2-x1,y2-y1))
            lines.append({'xyxy':[int(x1),int(y1),int(x2),int(y2)],'length_px':round(length,2),'status':'candidate'})
    lines.sort(key=lambda x:-x['length_px']);lines=lines[:max_lines]
    # HoughCircles is intentionally bounded to avoid false detections and huge runtimes.
    small=cv2.resize(blur,(round(w*.5),round(h*.5)))
    circles_raw=cv2.HoughCircles(small,cv2.HOUGH_GRADIENT,dp=1.5,minDist=max(12,round(min(h,w)*.025)),param1=130,param2=37,minRadius=max(8,round(min(h,w)*.015)),maxRadius=round(min(h,w)*.48))
    circles=[]
    if circles_raw is not None:
        for x,y,r in circles_raw[0][:max_circles]:
            circles.append({'cx':round(float(x)*2,2),'cy':round(float(y)*2,2),'r':round(float(r)*2,2),'status':'candidate'})
    # contour polygons for editing; do not pretend these are meaningful nodes.
    contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    shapes=[]
    for contour in contours:
        perimeter=cv2.arcLength(contour,True)
        if perimeter<min(h,w)*.09:continue
        poly=cv2.approxPolyDP(contour,.012*perimeter,True).reshape(-1,2)
        if 3<=len(poly)<=20:
            area=abs(cv2.contourArea(poly.astype(np.float32)))
            if area>=40:shapes.append({'vertices':poly.astype(int).tolist(),'area_px2':round(area,1),'status':'candidate'})
    shapes.sort(key=lambda x:-x['area_px2'])
    return {'lines':lines,'circles':circles,'polygons':shapes[:60]},edges

def candidate_svg(primitives,w,h):
    import xml.etree.ElementTree as ET
    ns='http://www.w3.org/2000/svg'
    ET.register_namespace('',ns)
    root=ET.Element('{%s}svg'%ns,{'viewBox':f'0 0 {w} {h}','width':str(w),'height':str(h)})
    ET.SubElement(root,'{%s}title'%ns).text='KEUM unverified geometry candidates'
    for i,obj in enumerate(primitives['lines']):
        x1,y1,x2,y2=obj['xyxy'];ET.SubElement(root,'{%s}line'%ns,{'id':f'line-{i}','x1':str(x1),'y1':str(y1),'x2':str(x2),'y2':str(y2),'stroke':'#15b7ff','stroke-width':'1.5','opacity':'.75'})
    for i,obj in enumerate(primitives['circles']):
        ET.SubElement(root,'{%s}circle'%ns,{'id':f'circle-{i}','cx':str(obj['cx']),'cy':str(obj['cy']),'r':str(obj['r']),'fill':'none','stroke':'#ffc74d','stroke-width':'1.5','opacity':'.75'})
    for i,obj in enumerate(primitives['polygons']):
        ET.SubElement(root,'{%s}polygon'%ns,{'id':f'polygon-{i}','points':' '.join(f'{x},{y}' for x,y in obj['vertices']),'fill':'none','stroke':'#c98aff','stroke-width':'1','opacity':'.55'})
    return ET.tostring(root,encoding='unicode')

def mask_metrics(reference_edges,rendered_mask,tolerance_px=3):
    """Edge agreement only, not scientific/semantic reconstruction accuracy."""
    a=(reference_edges>0).astype(np.uint8);b=(rendered_mask>0).astype(np.uint8)
    if not np.any(a) or not np.any(b):return {'precision':None,'recall':None,'f1':None,'reason':'empty edge set'}
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*tolerance_px+1,2*tolerance_px+1))
    dil_a=cv2.dilate(a,kernel);dil_b=cv2.dilate(b,kernel)
    precision=float(np.count_nonzero(b & dil_a)/np.count_nonzero(b))
    recall=float(np.count_nonzero(a & dil_b)/np.count_nonzero(a))
    return {'precision':round(precision,4),'recall':round(recall,4),'f1':round(2*precision*recall/(precision+recall),4) if precision+recall else 0.,'tolerance_px':tolerance_px,'meaning':'low-level edge overlap only'}

def render_mask(primitives,h,w):
    mask=np.zeros((h,w),np.uint8)
    for obj in primitives['lines']:
        cv2.line(mask,tuple(obj['xyxy'][:2]),tuple(obj['xyxy'][2:]),255,1,cv2.LINE_8)
    for obj in primitives['circles']:
        cv2.circle(mask,(round(obj['cx']),round(obj['cy'])),round(obj['r']),255,1)
    for obj in primitives['polygons']:
        cv2.polylines(mask,[np.array(obj['vertices'],np.int32)],True,255,1)
    return mask

def process(source:Path,out:Path,image_id:int,max_side=1100):
    img=cv2.imread(str(source),cv2.IMREAD_COLOR)
    if img is None:raise ValueError(f'Unreadable image: {source}')
    original_h,original_w=img.shape[:2]
    img,scale=normalize(img,max_side)
    h,w=img.shape[:2]
    primitives,edges=detect(img)
    mask=render_mask(primitives,h,w)
    metrics=mask_metrics(edges,mask)
    overlay=cv2.addWeighted(img,.75,cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR),.25,0)
    # Separate candidate layers: orange circles, cyan lines, magenta polygons.
    for item in primitives['circles']:
        cv2.circle(overlay,(round(item['cx']),round(item['cy'])),round(item['r']),(0,190,255),2)
    for item in primitives['lines']:
        cv2.line(overlay,tuple(item['xyxy'][:2]),tuple(item['xyxy'][2:]),(255,220,20),2)
    for item in primitives['polygons']:
        cv2.polylines(overlay,[np.array(item['vertices'],np.int32)],True,(255,90,220),1)
    out.mkdir(parents=True,exist_ok=True)
    cv2.imwrite(str(out/'overlay.jpg'),overlay,[cv2.IMWRITE_JPEG_QUALITY,84])
    cv2.imwrite(str(out/'edges.png'),edges)
    (out/'candidates.svg').write_text(candidate_svg(primitives,w,h),encoding='utf-8')
    source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
    record={'schema':VERSION,'image_id':image_id,'source_filename':source.name,'sha256':source_sha,
            'original_size':[original_w,original_h],'analysis_size':[w,h],'scale':scale,
            'status':'unverified-candidates','manual_review':False,
            'source_concept_ids':[], 'transcription_verified':False,
            'counts':{k:len(v) for k,v in primitives.items()},'edge_metrics':metrics,
            'geometry':primitives,'notes':'Automatic Hough/contour candidates, not exact vectorization or verified concept topology'}
    (out/'candidates.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    return {k:record[k] for k in ('image_id','source_filename','sha256','original_size','analysis_size','status','counts','edge_metrics')}

def run(source_dir:Path,output_dir:Path,max_side=1100,limit=None):
    sources=list_sources(source_dir)
    if limit is not None:sources=sources[:limit]
    output_dir.mkdir(parents=True,exist_ok=True)
    records=[]
    for i,path in enumerate(sources,1):
        records.append(process(path,output_dir/f'image_{i:02d}',i,max_side))
    manifest={'schema':VERSION,'count':len(records),'verified_count':0,'records':records,
              'limitations':['automated candidate extraction','not exact 49-diagram reconstruction','no OCR','no primary-source interpretation']}
    (output_dir/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# KEUM 49-image geometric candidate QA','',f'Processed: {len(records)}; manually verified: 0.','',
           '| # | Source | Lines | Circles | Polygons | Edge F1* |','|---:|---|---:|---:|---:|---:|']
    for r in records:
        m=r['edge_metrics'];counts=r['counts'];lines.append(f"| {r['image_id']} | {r['source_filename']} | {counts['lines']} | {counts['circles']} | {counts['polygons']} | {m['f1']} |")
    lines+=['','*F1 is low-level edge overlap against the same raster image; **not** exact diagram reconstruction accuracy.','',
            'Each image folder contains overlay.jpg, edges.png, candidates.svg and candidates.json. Review and correct candidates manually before claiming source fidelity.']
    (output_dir/'QA_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--sources',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('build/reconstruction'))
    p.add_argument('--max-side',type=int,default=1100)
    p.add_argument('--limit',type=int)
    a=p.parse_args()
    if a.max_side<200:raise SystemExit('--max-side must be >= 200')
    result=run(a.sources,a.output,a.max_side,a.limit)
    print('processed',result['count'],'images; verified',result['verified_count'])

if __name__=='__main__':main()