/* 09_items.js —— 掉落物(金币/血瓶/buff) */
/* ===== 掉落物：金币/血瓶/临时buff ===== */
let drops = []; // {mesh, x, z, kind, val, life}
function spawnCoinMesh(x,z,color,size){
  const m = new THREE.Mesh(new THREE.CylinderGeometry(size,size,0.15,10), new THREE.MeshBasicMaterial({color}));
  const gy = groundHeight(x,z,biomeOf(x,z));
  m.position.set(x,gy+0.2,z); m.rotation.x=Math.PI/2; m.rotation.z=Math.PI/2; scene.add(m);
  return m;
}
function dropCoin(x,z,val){
  const m = spawnCoinMesh(x,z,0xffd24d,0.28);
  drops.push({ mesh:m, x, z, kind:'coin', val, life:25 });
}
function dropPotion(x,z){
  const m = new THREE.Mesh(new THREE.SphereGeometry(0.25,8,6), new THREE.MeshBasicMaterial({color:0xff5a6b}));
  const gy = groundHeight(x,z,biomeOf(x,z));
  m.position.set(x,gy+0.3,z); scene.add(m);
  drops.push({ mesh:m, x, z, kind:'potion', val:35, life:20 });
}
function dropBuff(x,z){
  const m = new THREE.Mesh(new THREE.OctahedronGeometry(0.28,0), new THREE.MeshBasicMaterial({color:0x7fd0ff}));
  const gy = groundHeight(x,z,biomeOf(x,z));
  m.position.set(x,gy+0.4,z); scene.add(m);
  drops.push({ mesh:m, x, z, kind:'buff', val:8, life:14 }); // buff 8秒伤害翻倍
}
// 击杀后按概率生成掉落
function spawnDrops(x,z){
  if(Math.random()<DROP_RATE.potion) dropPotion(x,z);
  if(Math.random()<DROP_RATE.buff) dropBuff(x,z);
}
function updateDrops(dt){
  for(let i=drops.length-1;i>=0;i--){
    const d = drops[i];
    d.life -= dt;
    // 漂浮动画
    d.mesh.rotation.y += dt*3;
    // 拾取：距离够近
    if(dist2D({x:d.x,z:d.z}, player.pos) < 1.2){
      if(d.kind==='coin'){ player.coins += d.val; addCoinUI(d.val); }
      else if(d.kind==='potion'){ const heal = d.val*(player.role==='priest'?1.5:1); player.hp=Math.min(player.maxHp, player.hp+heal); updateHp(); floatText('+'+Math.round(heal)+' HP','#ff5a6b'); }
      else if(d.kind==='buff'){ player.buffTimer = d.val; floatText('伤害翻倍!','#7fd0ff'); }
      scene.remove(d.mesh); drops.splice(i,1); continue;
    }
    if(d.life<=0){ scene.remove(d.mesh); drops.splice(i,1); }
  }
  // buff 计时
  if(player.buffTimer>0) player.buffTimer-=dt;
}