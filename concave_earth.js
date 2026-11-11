import * as THREE from 'three';

/**
 * Symbolic concave-Earth visualization. NOT a geophysical model.
 * A globe of stars is placed INSIDE a hollow inward-facing terrestrial shell.
 * Deterministic seeded points and constellation connections.
 */
export function createConcaveEarth(scene,{radius=27,starRadius=12,starCount=850,seed=20261111}={}){
  if(!(radius>starRadius+2))throw new Error('Earth shell must enclose star globe');
  const earth=new THREE.Group();earth.name='Concave Earth (symbolic)';scene.add(earth);
  const shell=new THREE.Group();earth.add(shell);
  const canvas=document.createElement('canvas');canvas.width=2048;canvas.height=1024;
  const ctx=canvas.getContext('2d');ctx.fillStyle='#0c304b';ctx.fillRect(0,0,2048,1024);
  // Abstract land masses, deliberately NOT a geographically accurate Earth map.
  const polygons=[
    [[.06,.22],[.18,.16],[.26,.28],[.22,.43],[.16,.50],[.10,.42]],
    [[.25,.53],[.33,.50],[.38,.62],[.33,.86],[.29,.91],[.26,.74]],
    [[.43,.23],[.54,.18],[.61,.30],[.56,.47],[.50,.48],[.46,.38]],
    [[.49,.50],[.57,.47],[.62,.62],[.57,.82],[.53,.88],[.49,.69]],
    [[.62,.22],[.80,.19],[.89,.32],[.85,.46],[.73,.52],[.64,.42]],
    [[.82,.66],[.92,.63],[.95,.76],[.88,.84],[.81,.75]]
  ];
  for(const poly of polygons){ctx.beginPath();poly.forEach(([u,v],i)=>i?ctx.lineTo(u*2048,v*1024):ctx.moveTo(u*2048,v*1024));ctx.closePath();ctx.fillStyle='#28635d';ctx.fill();ctx.strokeStyle='#76b09b';ctx.lineWidth=3;ctx.stroke();}
  ctx.strokeStyle='#4e8ea0';ctx.lineWidth=1;
  for(let lat=-75;lat<=75;lat+=15){let y=(90-lat)/180*1024;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(2048,y);ctx.stroke();}
  for(let lon=0;lon<360;lon+=15){let x=lon/360*2048;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,1024);ctx.stroke();}
  const tex=new THREE.CanvasTexture(canvas);tex.colorSpace=THREE.SRGBColorSpace;
  const surface=new THREE.Mesh(new THREE.SphereGeometry(radius,96,64),new THREE.MeshBasicMaterial({map:tex,side:THREE.BackSide,transparent:true,opacity:.33,depthWrite:false}));shell.add(surface);
  const wire=new THREE.Mesh(new THREE.SphereGeometry(radius-.06,48,24),new THREE.MeshBasicMaterial({color:0x54bed1,wireframe:true,side:THREE.BackSide,transparent:true,opacity:.08,depthWrite:false}));shell.add(wire);
  const boundary=new THREE.Mesh(new THREE.SphereGeometry(radius,48,24),new THREE.MeshBasicMaterial({color:0x153d52,wireframe:true,transparent:true,opacity:.045,depthWrite:false}));shell.add(boundary);
  // Inward-facing celestial globe; stars distributed on a spherical surface.
  const sky=new THREE.Group();sky.name='Star Globe';earth.add(sky);
  let s=seed>>>0;const rand=()=>{s=(1664525*s+1013904223)>>>0;return s/4294967296;};
  const positions=new Float32Array(starCount*3),colors=new Float32Array(starCount*3),sizes=[];
  const color=new THREE.Color();
  for(let i=0;i<starCount;i++){
    const z=2*(i+.5)/starCount-1,phi=(i*2.399963229728653+rand()*.12),r=Math.sqrt(1-z*z);
    positions[3*i]=starRadius*r*Math.cos(phi);positions[3*i+1]=starRadius*z;positions[3*i+2]=starRadius*r*Math.sin(phi);
    const temperature=rand();color.setHSL(temperature<.2?.08:.57,.25+rand()*.28,.62+rand()*.35);
    colors[3*i]=color.r;colors[3*i+1]=color.g;colors[3*i+2]=color.b;
    sizes.push(.035+rand()*.09);
  }
  const geom=new THREE.BufferGeometry();geom.setAttribute('position',new THREE.BufferAttribute(positions,3));geom.setAttribute('color',new THREE.BufferAttribute(colors,3));
  const points=new THREE.Points(geom,new THREE.PointsMaterial({size:.13,vertexColors:true,transparent:true,opacity:.96,sizeAttenuation:true,depthWrite:false}));sky.add(points);
  // Constellation arcs: selected nearby stars are joined by short chords.
  const segments=[];for(let i=0;i<Math.min(starCount-7,160);i+=2){
    const j=i+3+(i%5),a=new THREE.Vector3(positions[i*3],positions[i*3+1],positions[i*3+2]),b=new THREE.Vector3(positions[j*3],positions[j*3+1],positions[j*3+2]);
    if(a.distanceTo(b)<5.3)segments.push(a,b);
  }
  const constellations=new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(segments),new THREE.LineBasicMaterial({color:0x9eb7ff,transparent:true,opacity:.22,depthWrite:false}));sky.add(constellations);
  const equator=new THREE.Group();sky.add(equator);
  for(const theta of [Math.PI/2,Math.PI/3,2*Math.PI/3]){
    const curve=[];for(let k=0;k<=180;k++){const p=k*Math.PI*2/180;curve.push(new THREE.Vector3(starRadius*Math.sin(theta)*Math.cos(p),starRadius*Math.cos(theta),starRadius*Math.sin(theta)*Math.sin(p)));}
    equator.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve),new THREE.LineBasicMaterial({color:0xb6a4ff,transparent:true,opacity:.23,depthWrite:false})));
  }
  const core=new THREE.Mesh(new THREE.SphereGeometry(.65,24,16),new THREE.MeshBasicMaterial({color:0xffdca4,transparent:true,opacity:.25,depthWrite:false}));sky.add(core);
  // Sun and Moon: symbolic local luminaries, both strictly INSIDE the concave shell.
  // Their orbital radii are less than the star-globe radius, with a tilted lunar path.
  const luminaries=new THREE.Group();luminaries.name='Sun and Moon';earth.add(luminaries);
  const sunRadius=1.25,moonRadius=.78,sunOrbit=starRadius*.57,moonOrbit=starRadius*.79;
  const sun=new THREE.Group();sun.name='Sun';luminaries.add(sun);
  const sunBody=new THREE.Mesh(new THREE.SphereGeometry(sunRadius,40,28),new THREE.MeshBasicMaterial({color:0xffd36a}));sun.add(sunBody);
  const corona=new THREE.Mesh(new THREE.SphereGeometry(sunRadius*1.5,32,24),new THREE.MeshBasicMaterial({color:0xffae3b,transparent:true,opacity:.17,depthWrite:false}));sun.add(corona);
  const sunlight=new THREE.PointLight(0xffd79a,15,starRadius*2,1.5);sun.add(sunlight);
  const moon=new THREE.Group();moon.name='Moon';luminaries.add(moon);
  const moonBody=new THREE.Mesh(new THREE.SphereGeometry(moonRadius,32,24),new THREE.MeshStandardMaterial({color:0xcbd2db,roughness:.95,metalness:0,emissive:0x202a40,emissiveIntensity:.12}));moon.add(moonBody);
  // Explicit illumination: a terminator becomes visible as Sun and Moon move.
  const moonFill=new THREE.AmbientLight(0x63718a,.16);moon.add(moonFill);
  function orbitLine(r,tilt,color){
    const pts=[];for(let k=0;k<=192;k++){const a=k*Math.PI*2/192;pts.push(new THREE.Vector3(r*Math.cos(a),r*Math.sin(a)*Math.sin(tilt),r*Math.sin(a)*Math.cos(tilt)));}
    const obj=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color,transparent:true,opacity:.32,depthWrite:false}));luminaries.add(obj);return obj;
  }
  const sunPath=orbitLine(sunOrbit,.08,0xffc66b),moonPath=orbitLine(moonOrbit,.34,0xb2c8e7);
  let sunPhase=.4,moonPhase=2.5,sunSpeed=.035,moonSpeed=.065;
  function positionLuminaries(){
    sun.position.set(sunOrbit*Math.cos(sunPhase),sunOrbit*Math.sin(sunPhase)*Math.sin(.08),sunOrbit*Math.sin(sunPhase)*Math.cos(.08));
    moon.position.set(moonOrbit*Math.cos(moonPhase),moonOrbit*Math.sin(moonPhase)*Math.sin(.34),moonOrbit*Math.sin(moonPhase)*Math.cos(.34));
  }
  positionLuminaries();
  let enabled=true,rotationSpeed=.012;
  return {
    earth,shell,sky,sun,moon,luminaries,radius,starRadius,
    get visible(){return enabled;},
    setVisible(v){enabled=!!v;earth.visible=enabled;},
    setShellOpacity(v){surface.material.opacity=THREE.MathUtils.clamp(v,0,.85);},
    setStarRotationSpeed(v){rotationSpeed=Number(v)||0;},
    setLuminariesVisible(v){luminaries.visible=!!v;},
    setSunSpeed(v){sunSpeed=THREE.MathUtils.clamp(Number(v)||0,0,.2);},
    setMoonSpeed(v){moonSpeed=THREE.MathUtils.clamp(Number(v)||0,0,.2);},
    update(dt){if(enabled){sky.rotation.y+=rotationSpeed*dt;sunPhase+=sunSpeed*dt;moonPhase+=moonSpeed*dt;positionLuminaries();}},
    dispose(){scene.remove(earth);tex.dispose();surface.geometry.dispose();surface.material.dispose();wire.geometry.dispose();wire.material.dispose();boundary.geometry.dispose();boundary.material.dispose();geom.dispose();points.material.dispose();constellations.geometry.dispose();constellations.material.dispose();sunBody.geometry.dispose();sunBody.material.dispose();corona.geometry.dispose();corona.material.dispose();moonBody.geometry.dispose();moonBody.material.dispose();sunPath.geometry.dispose();sunPath.material.dispose();moonPath.geometry.dispose();moonPath.material.dispose();}
  };
}
