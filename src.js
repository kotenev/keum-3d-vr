import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {VRButton} from 'three/addons/webxr/VRButton.js';
import {createConcaveEarth} from './concave_earth.js';
const scene=new THREE.Scene();scene.background=new THREE.Color(0x050916);scene.fog=new THREE.FogExp2(0x050916,.012);
const camera=new THREE.PerspectiveCamera(55,innerWidth/innerHeight,.05,400);camera.position.set(20,13,24);
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.xr.enabled=true;document.querySelector('#view').appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.target.set(0,0,0);controls.maxDistance=100;controls.minDistance=2;
scene.add(new THREE.AmbientLight(0xaccbff,.8));const light=new THREE.PointLight(0x7bcaff,100,100);light.position.set(7,12,8);scene.add(light);
const state={speed:1,coupling:.6,breath:.35,projection:.22,phase:0,paused:false,axes:false};
const layers={kathara:{name:'Kathara · 12 центров',color:0x66dcff},merkaba:{name:'PCM/PKA · встречные поля',color:0xffa65c},lotus:{name:'Lotus · 24 дуги',color:0xe8a5ff},density:{name:'15D · уровни плотности',color:0x80e6a1},grid:{name:'Crystal Light Grids',color:0xe7db84},flow:{name:'Потоки · динамика',color:0x7ef8eb},cosmos:{name:'Eckasha · оболочки',color:0x8a96ff}};
const root=new THREE.Group();scene.add(root);const objects=[];const animated=[];
// Symbolic inward-facing terrestrial shell enclosing a star globe.
const concaveEarth=createConcaveEarth(scene,{radius:29,starRadius:17,starCount:1000});
let earthView=false;
function line(points,color,opacity=.65,parent=root){const g=new THREE.BufferGeometry().setFromPoints(points);const m=new THREE.LineBasicMaterial({color,transparent:true,opacity,depthWrite:false});const o=new THREE.Line(g,m);parent.add(o);return o}
function circle(radius,y,color,opacity=.35,parent=root,orientation='horizontal'){let pts=[];for(let i=0;i<=160;i++){let a=2*Math.PI*i/160;pts.push(orientation==='horizontal'?new THREE.Vector3(radius*Math.cos(a),y,radius*Math.sin(a)):new THREE.Vector3(radius*Math.cos(a),radius*Math.sin(a),y))}return line(pts,color,opacity,parent)}
function sphere(x,y,z,r,color,opacity=1,parent=root){let m=new THREE.Mesh(new THREE.SphereGeometry(r,12,10),new THREE.MeshBasicMaterial({color,transparent:opacity<1,opacity,depthWrite:opacity===1}));m.position.set(x,y,z);parent.add(m);return m}
function attach(o,layer,id,title){o.userData={layer,id,title};objects.push(o);return o}
function makeLayer(key){layers[key].group=new THREE.Group();root.add(layers[key].group);return layers[key].group}
const K=makeLayer('kathara'),M=makeLayer('merkaba'),L=makeLayer('lotus'),D=makeLayer('density'),G=makeLayer('grid'),F=makeLayer('flow'),C=makeLayer('cosmos');
// KATHARA: twelve signets; a conventional graph embedding preserving visual symmetry.
const pts=[[-0,-5.3,0],[0,-3.8,0],[-2.6,-2.7,0],[2.6,-2.7,0],[0,-1.6,0],[-2.6,0,0],[2.6,0,0],[0,1.4,0],[-2.6,2.7,0],[2.6,2.7,0],[0,4,0],[0,5.3,0]].map(p=>new THREE.Vector3(...p));
const edges=[[0,1],[1,2],[1,3],[2,3],[2,4],[3,4],[2,5],[3,6],[4,5],[4,6],[5,6],[5,7],[6,7],[5,8],[6,9],[7,8],[7,9],[8,9],[8,10],[9,10],[10,11],[8,11],[9,11],[2,6],[3,5],[5,9],[6,8],[1,4],[4,7],[7,10]];
for(let [a,b] of edges)line([pts[a],pts[b]],0x66dcff,.45,K);
pts.forEach((p,i)=>{let o=sphere(p.x,p.y,p.z,.19,0x7de4ff,1,K);attach(o,'kathara',21,'Kathara Signet '+(i+1));});
// DENSITY: five triplets, each shell at fixed radial coordinate.
const densityGroups=[];const densityColors=[0x5ad0ff,0x6be8ba,0xf3cf7c,0xd5a0f6,0xff9cbd];
for(let d=0;d<5;d++){const r=6.6+d*1.45;const group=new THREE.Group();D.add(group);densityGroups.push(group);const wire=new THREE.Mesh(new THREE.SphereGeometry(r,24,16),new THREE.MeshBasicMaterial({color:densityColors[d],transparent:true,opacity:.035,wireframe:true,depthWrite:false}));group.add(wire);for(let i=0;i<3;i++){const theta=(i+1)*Math.PI/4;const ringpts=[];for(let j=0;j<=120;j++){const a=j*2*Math.PI/120;ringpts.push(new THREE.Vector3(r*Math.sin(theta)*Math.cos(a),r*Math.cos(theta),r*Math.sin(theta)*Math.sin(a)))}line(ringpts,densityColors[d],.13,group)}attach(sphere(r,0,0,.12,densityColors[d],1,group),'density',3,`Density ${d+1} · D${3*d+1}–D${3*d+3}`)}
// MERKABA: two tetrahedra rotating with opposite angular velocity, phase is controlled by simulation.
function tetra(sign,color,parent){const g=new THREE.Group();parent.add(g);let p=[];for(let i=0;i<3;i++){let a=i*2*Math.PI/3;p.push(new THREE.Vector3(5.4*Math.cos(a),-sign*3.1,5.4*Math.sin(a)))}p.push(new THREE.Vector3(0,sign*6.3,0));for(let i=0;i<3;i++)for(let j=i+1;j<4;j++)line([p[i],p[j]],color,.8,g);let mesh=new THREE.Mesh(new THREE.TetrahedronGeometry(5.3),new THREE.MeshBasicMaterial({color,transparent:true,opacity:.065,side:THREE.DoubleSide,depthWrite:false}));g.add(mesh);return g}
const pcm=tetra(1,0xffac62,M),pka=tetra(-1,0x79c9ff,M);attach(sphere(0,0,0,.31,0xffdf9c,1,M),'merkaba',171,'Double Bi-Veca Merkaba');
// LOTUS: 24 meridian petals, each ellipse runs from axial origin through its own radial maximum.
for(let i=0;i<24;i++){let a=i*2*Math.PI/24;let pp=[];for(let j=0;j<=72;j++){let t=j*Math.PI/72;let radius=5.5*Math.sin(t);pp.push(new THREE.Vector3(radius*Math.cos(a),6.4*Math.cos(t),radius*Math.sin(a)))}line(pp,i%2?0xd0a6ff:0xff91d4,.5,L)}
for(let i=0;i<12;i++){let a=i*2*Math.PI/12;attach(sphere(5.5*Math.cos(a),0,5.5*Math.sin(a),.12,0xeabaff,1,L),'lotus',281,`Lotus Point ${i+1}`)}
// LIGHT GRIDS: 3 nested lat-long networks and 24 longitudinal strands.
for(let k=0;k<3;k++){let r=3.2+k*.65;let group=new THREE.Group();G.add(group);for(let j=1;j<6;j++){let th=j*Math.PI/6;let pp=[];for(let n=0;n<=100;n++){let a=n*2*Math.PI/100;pp.push(new THREE.Vector3(r*Math.sin(th)*Math.cos(a),r*Math.cos(th),r*Math.sin(th)*Math.sin(a)))}line(pp,[0xe6e2a0,0x80c6f8,0xe6a2d9][k],.35,group)}for(let j=0;j<24;j++){let a=j*2*Math.PI/24,pp=[];for(let n=0;n<=60;n++){let t=n*Math.PI/60;pp.push(new THREE.Vector3(r*Math.sin(t)*Math.cos(a),r*Math.cos(t),r*Math.sin(t)*Math.sin(a)))}line(pp,[0xe6e2a0,0x80c6f8,0xe6a2d9][k],.24,group)}attach(sphere(0,r,0,.11,0xe6e2a0,1,group),'grid',409,`Crystal Light Grid ${k+1}`)}
// Cosmic nested spheres / Eckasha representation
for(let r of [11,13,15]){let mesh=new THREE.Mesh(new THREE.SphereGeometry(r,32,18),new THREE.MeshBasicMaterial({color:0x8293ed,wireframe:true,transparent:true,opacity:.06,depthWrite:false}));C.add(mesh)}
// Flow particles: paths are illustrative, not measured fields.
for(let i=0;i<120;i++){let a=i*Math.PI*(3-Math.sqrt(5));let h=2*(i+.5)/120-1;let r=Math.sqrt(1-h*h);let m=sphere(0,0,0,.055,i%2?0x65e4ff:0xffba6b,.8,F);animated.push({mesh:m,a,h,r,seed:i/120});}
const axes=new THREE.AxesHelper(12);axes.visible=false;scene.add(axes);
const layDiv=document.querySelector('#layers');Object.entries(layers).forEach(([key,v])=>{let el=document.createElement('label');el.className='switch';el.innerHTML=`<input type="checkbox" checked data-layer="${key}"><span>${v.name}</span>`;layDiv.appendChild(el);el.querySelector('input').onchange=e=>v.group.visible=e.target.checked});
const paramDef=[['speed','Угловая скорость',0,3,.05],['coupling','Коэффициент связи',0,2,.05],['breath','Амплитуда дыхания',0,1,.02],['projection','Смешение 15D→3D',0,1,.02]];for(let [key,label,min,max,step] of paramDef){let el=document.createElement('div');el.className='field';el.innerHTML=`<label>${label}<b id="v-${key}">${state[key].toFixed(2)}</b></label><input type="range" min="${min}" max="${max}" step="${step}" value="${state[key]}">`;document.querySelector('#params').appendChild(el);el.querySelector('input').oninput=e=>{state[key]=+e.target.value;el.querySelector('b').textContent=state[key].toFixed(2)}}
const presets={earth:[],all:['kathara','merkaba','lotus','density','grid','flow','cosmos'],kathara:['kathara'],merkaba:['kathara','merkaba','flow'],lotus:['kathara','lotus','flow'],cosmos:['density','cosmos','flow'],grid:['grid','kathara']};document.querySelector('#preset').onchange=e=>{let active=presets[e.target.value];Object.entries(layers).forEach(([k,v])=>{v.group.visible=active.includes(k);document.querySelector(`[data-layer="${k}"]`).checked=v.group.visible})};
document.querySelector('#earth-toggle').onchange=e=>concaveEarth.setVisible(e.target.checked);
document.querySelector('#earth-opacity').oninput=e=>concaveEarth.setShellOpacity(+e.target.value);
document.querySelector('#star-speed').oninput=e=>concaveEarth.setStarRotationSpeed(+e.target.value);
document.querySelector('#earth-camera').onclick=()=>{earthView=!earthView;camera.position.set(earthView?0:20,earthView?0:13,earthView?0:24);controls.target.set(0,0,0);controls.update();document.querySelector('#earth-camera').textContent=earthView?'Внешний обзор':'Внутри Земли';};
document.querySelector('#pause').onclick=e=>{state.paused=!state.paused;e.target.textContent=state.paused?'▶ Пуск':'⏸ Пауза'};document.querySelector('#axes').onclick=()=>axes.visible=!axes.visible;document.querySelector('#reset').onclick=()=>{camera.position.set(20,13,24);controls.target.set(0,0,0);controls.update();state.phase=0};
let catalog=[];fetch('./data/catalog.json').then(r=>r.json()).then(data=>{catalog=data;renderCatalog('');document.querySelector('#stats').textContent=`${data.length} понятий · 7 слоёв · WebXR`}).catch(()=>document.querySelector('#stats').textContent='Каталог: требуется локальный сервер');
function showEntry(item){document.querySelector('#detail').innerHTML=`<b>#${item.id} · ${escapeHtml(item.name)}</b><p>${escapeHtml(item.description)}</p><small>${escapeHtml(item.category)} · Источник: ${escapeHtml(item.source)}</small>`}
function escapeHtml(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function renderCatalog(q){let list=catalog.filter(x=>(String(x.id)+' '+x.name+' '+x.category).toLowerCase().includes(q.toLowerCase())).slice(0,80);const el=document.querySelector('#catalog');el.replaceChildren();for(let item of list){let div=document.createElement('div');div.className='entry';div.textContent=`#${item.id} ${item.name}`;div.onclick=()=>showEntry(item);el.appendChild(div)}if(!list.length)el.textContent='Нет совпадений'}document.querySelector('#search').oninput=e=>renderCatalog(e.target.value);
const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();renderer.domElement.addEventListener('click',e=>{pointer.x=e.clientX/innerWidth*2-1;pointer.y=-(e.clientY/innerHeight)*2+1;raycaster.setFromCamera(pointer,camera);let hit=raycaster.intersectObjects(objects,false).find(x=>x.object.userData.id);if(hit){let d=hit.object.userData;showEntry(catalog.find(x=>x.id===d.id)||{id:d.id,name:d.title,description:'Геометрическая визуализация концепции',category:d.layer,source:'модель'})}});
let prev=performance.now();renderer.setAnimationLoop(()=>{let now=performance.now(),dt=Math.min(.05,(now-prev)/1000);prev=now;if(!state.paused)state.phase+=dt*state.speed;let t=state.phase;pcm.rotation.y=t*.33;pka.rotation.y=-t*.233;M.scale.setScalar(1+state.breath*.09*Math.sin(t*1.3));L.rotation.y=t*.065;G.rotation.y=-t*.038;D.rotation.y=t*.01;densityGroups.forEach((g,i)=>g.scale.setScalar(1+state.projection*.04*(i-2)));for(let p of animated){let a=p.a+t*(p.seed<.5?1:-1)*.35;let rr=5.5+state.coupling*.5*Math.sin(t*2+p.seed*18);p.mesh.position.set(rr*p.r*Math.cos(a),7*p.h+state.breath*Math.sin(t*1.3+p.seed*8),rr*p.r*Math.sin(a));}C.rotation.y=t*.008;concaveEarth.update(state.paused?0:dt);controls.update();renderer.render(scene,camera)});
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)});
try{document.querySelector('#vr').appendChild(VRButton.createButton(renderer))}catch(e){console.warn('WebXR unavailable',e)}
// Shared parametric graph: same JSON powers SVG editor and interactive Three.js scene.
const customGraphGroup=new THREE.Group();scene.add(customGraphGroup);
function loadParametricGraph(g){
 if(!g||g.schema!=='keum.graph.v1'||!Array.isArray(g.nodes)||!Array.isArray(g.edges))return;
 customGraphGroup.clear();const lookup=new Map(g.nodes.map(n=>[String(n.id),n]));
 const material=new THREE.LineBasicMaterial({color:0x62f1ca,transparent:true,opacity:.88});
 for(const e of g.edges){const a=lookup.get(String(e.source)),b=lookup.get(String(e.target));if(!a||!b)continue;
 const geometry=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a.position),new THREE.Vector3(...b.position)]);
 customGraphGroup.add(new THREE.Line(geometry,material));}
 const geo=new THREE.SphereGeometry(.09,8,6);
 for(const n of g.nodes){const o=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:0xffd17a}));o.position.set(...n.position);o.userData={id:n.entity_id,title:n.label,layer:'parametric'};customGraphGroup.add(o);objects.push(o)}
 root.visible=false;document.querySelector('#stats').textContent=`Параметрический граф: ${g.nodes.length} узлов · ${g.edges.length} связей`;
}
try{
 const p=new URLSearchParams(location.search);
 if(p.get('graph')==='custom'){let raw=sessionStorage.getItem('keumGraph');if(raw)loadParametricGraph(JSON.parse(raw));}
 else if(p.has('graph'))fetch('./vector_engine/graph_exports/'+encodeURIComponent(p.get('graph'))+'.json').then(r=>r.json()).then(loadParametricGraph);
}catch(e){console.warn('Parametric graph not loaded',e)}