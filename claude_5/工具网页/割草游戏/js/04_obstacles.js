/* 04_obstacles.js —— 树与障碍贴图精灵·可破坏物 */
// 卡通阔叶树 / 松树：贴图精灵（billboard 自动面向相机），比几何体更精致
// TREE_TEX 由 assets/tex_data.js 定义
// 共享材质：加载完成前为空（不渲染），就绪后挂 map 自动显示
const TREE_MATS = {
  leaf: new THREE.SpriteMaterial({ transparent:true, depthWrite:false }),
  pine: new THREE.SpriteMaterial({ transparent:true, depthWrite:false })
};
const TREE_READY = { leaf:false, pine:false };
(function preloadTree(){
  const l = new THREE.TextureLoader();
  l.load(TREE_TEX.leaf, t=>{ t.colorSpace=THREE.SRGBColorSpace; TREE_MATS.leaf.map=t; TREE_MATS.leaf.needsUpdate=true; TREE_READY.leaf=true; }, undefined, ()=>{});
  l.load(TREE_TEX.pine, t=>{ t.colorSpace=THREE.SRGBColorSpace; TREE_MATS.pine.map=t; TREE_MATS.pine.needsUpdate=true; TREE_READY.pine=true; }, undefined, ()=>{});
})();
// 场景物件统一按传奇贴图实际宽高比设置精灵尺寸（避免拉伸变形）
// 贴图 ar：tree=0.113 pine=0.231 rockpile=1.5 fountain=0.48 barrel=1.5 crate=1.5 fence=0.65 tower=0.21 mrock=0.294 cactus=0.64
function buildTree(px, pz, seed){
  const spr = new THREE.Sprite(TREE_MATS.leaf);
  spr.scale.set(0.55, 4.6, 1);      // 枯藤古树：窄高条带
  spr.position.set(px, 2.3, pz);
  spr.renderOrder = 1;
  return spr;
}

// 场景地标记录（喷泉/塔楼），供 BOSS 战作参照
const landmarks = [];
// 卡通松树：贴图精灵
function buildPine(px,pz,seed){
  const spr = new THREE.Sprite(TREE_MATS.pine);
  spr.scale.set(0.82, 3.55, 1);     // 绿藤柱
  spr.position.set(px, 1.78, pz);
  spr.renderOrder = 1;
  return spr;
}
// 障碍物贴图系统：6 种卡通道具（岩石/喷泉/木桶/木箱/栅栏桩/塔楼）贴图精灵
// OBST_TEX 由 assets/tex_data.js 定义
const OBST_MATS = {
  rockpile:new THREE.SpriteMaterial({transparent:true,depthWrite:false}),
  fountain:new THREE.SpriteMaterial({transparent:true,depthWrite:false}),
  barrel:new THREE.SpriteMaterial({transparent:true,depthWrite:false}),
  crate:new THREE.SpriteMaterial({transparent:true,depthWrite:false}),
  fence:new THREE.SpriteMaterial({transparent:true,depthWrite:false}),
  tower:new THREE.SpriteMaterial({transparent:true,depthWrite:false}),
  mrock:new THREE.SpriteMaterial({transparent:true,depthWrite:false})
};
const OBST_READY = {};
(function preloadObst(){
  const l=new THREE.TextureLoader();
  ['rockpile','fountain','barrel','crate','fence','tower','mrock'].forEach(k=>{
    OBST_READY[k]=false;
    l.load(OBST_TEX[k], t=>{ t.colorSpace=THREE.SRGBColorSpace; OBST_MATS[k].map=t; OBST_MATS[k].needsUpdate=true; OBST_READY[k]=true; }, undefined, ()=>{});
  });
})();
// 岩石堆（传奇石块，贴图精灵）
function buildRockPile(px,pz,seed,r){
  const spr = new THREE.Sprite(OBST_MATS.rockpile);
  const h = 0.62 + r*0.3;                       // r 为碰撞半径，随大小微调高度
  spr.scale.set(h*1.5, h, 1); spr.position.set(px, h/2, pz); spr.renderOrder=1;
  return spr;
}
// 石质喷泉（地标：传奇木桥/石台，贴图精灵）
function buildFountain(px,pz,seed){
  const spr = new THREE.Sprite(OBST_MATS.fountain);
  spr.scale.set(1.15, 2.4, 1); spr.position.set(px, 1.2, pz); spr.renderOrder=1;
  return spr;
}
// 木桶（可破坏：传奇石堆块，贴图精灵）
function buildBarrel(px,pz,seed){
  const spr = new THREE.Sprite(OBST_MATS.barrel);
  spr.scale.set(1.13, 0.75, 1); spr.position.set(px, 0.38, pz); spr.renderOrder=1;
  return spr;
}
// 木箱（可破坏：传奇石堆块，贴图精灵）
function buildCrate(px,pz,seed){
  const spr = new THREE.Sprite(OBST_MATS.crate);
  spr.scale.set(1.13, 0.75, 1); spr.position.set(px, 0.38, pz); spr.renderOrder=1;
  return spr;
}
// 栅栏柱（尖顶木桩，贴图精灵）
function buildFencePost(px,pz,seed){
  const spr = new THREE.Sprite(OBST_MATS.fence);
  spr.scale.set(0.97, 1.5, 1); spr.position.set(px, 0.75, pz); spr.renderOrder=1;
  return spr;
}
// 破损塔楼/废墟石柱（地标：传奇细高石柱，贴图精灵）
function buildRuinTower(px,pz,seed){
  const spr = new THREE.Sprite(OBST_MATS.tower);
  spr.scale.set(0.86, 4.1, 1); spr.position.set(px, 2.05, pz); spr.renderOrder=1;
  return spr;
}
// 山川石山（窄高岩壁，贴图精灵）
function buildMrock(px,pz,seed){
  const spr = new THREE.Sprite(OBST_MATS.mrock);
  spr.scale.set(0.96, 3.25, 1); spr.position.set(px, 1.63, pz); spr.renderOrder=1;
  return spr;
}
// 击碎可破坏物：移除模型、掉金币
function breakObstacle(ob){
  ob.destroyed = true;
  if(ob.mesh && ob.mesh.parent) ob.mesh.parent.remove(ob.mesh);
  const v = 4 + Math.floor(Math.random()*5);
  dropCoin(ob.x, ob.z, v);
  floatText('击碎 +'+v+' 金币','#ffd24d');
}