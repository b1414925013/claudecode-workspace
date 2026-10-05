/* 03_terrain.js —— 地貌/分块/哈希/仙人掌石山 */
/* ===== 地貌系统：草地/沙漠/山川/河流 随机分布 ===== */
const BIOME_COLORS = {
  grass:   [0x6fcf6a, 0x7fcf58, 0x63c96f, 0x7cd172], // 草地
  desert:  [0xe8c877, 0xe6c06a, 0xf0d080, 0xddb86a], // 沙漠
  mountain:[0x9aa0a8, 0x8d949d, 0xa6abb3, 0x848a93], // 山川
  river:   [0x7ec8e3, 0x69b7d8, 0x8fd4e6, 0x63b4dd]  // 河流
};
// 地貌：平滑噪声场决定（value noise）→ 非方格拼接、斑块大小随机
const BIO_CELL = 48; // 地貌种子网格间距（比块大，产生大地貌斑块）
function bioNoise(ci,cj){ return rng(ci*104729, cj*15485863); }
function biomeField(x,z){
  const cx=Math.floor(x/BIO_CELL), cz=Math.floor(z/BIO_CELL);
  const fx=(x-cx*BIO_CELL)/BIO_CELL, fz=(z-cz*BIO_CELL)/BIO_CELL;
  const sx=fx*fx*(3-2*fx), sz=fz*fz*(3-2*fz);
  const v00=bioNoise(cx,cz),v10=bioNoise(cx+1,cz),v01=bioNoise(cx,cz+1),v11=bioNoise(cx+1,cz+1);
  return v00*(1-sx)*(1-sz)+v10*sx*(1-sz)+v01*(1-sx)*sz+v11*sx*sz;
}
function biomeOf(x,z){ // 世界坐标
  const v=biomeField(x,z);
  if(v<0.45) return 'grass';      // 草地
  if(v<0.70) return 'desert';     // 沙漠
  if(v<0.90) return 'mountain';   // 山川
  return 'river';                 // 河流
}
function biomeColor(x,z){
  const b=biomeOf(x,z);
  const arr=BIOME_COLORS[b];
  return arr[Math.floor(rng(Math.floor(x)*31, Math.floor(z)*57)*arr.length)];
}
// 世界边界：玩家/怪物不可越出该范围（边界外的地面不能通过）
const WORLD_LIMIT = 150;
// 卡通地形起伏：低频平滑高度噪声，各地貌起伏幅度不同
function heightNoise(x,z){
  const c=26, cx=Math.floor(x/c), cz=Math.floor(z/c);
  const fx=(x-cx*c)/c, fz=(z-cz*c)/c;
  const sx=fx*fx*(3-2*fx), sz=fz*fz*(3-2*fz);
  const v00=rng(cx*97,cz*163),v10=rng((cx+1)*97,cz*163),v01=rng(cx*97,(cz+1)*163),v11=rng((cx+1)*97,(cz+1)*163);
  return v00*(1-sx)*(1-sz)+v10*sx*(1-sz)+v01*(1-sx)*sz+v11*sx*sz;
}
function groundHeight(x,z,biome){
  const n=heightNoise(x,z);
  if(biome==='mountain') return 1.0*n;   // 山川起伏大
  if(biome==='desert')   return 0.5*n;   // 沙丘起伏
  if(biome==='grass')    return 0.24*n;  // 草地微起伏
  return 0.06*n;                          // 河流平坦
}
// 沙漠仙人掌（阻挡）—— 传奇贴图精灵（细长植物，贴图宽高比约 0.64）
let CACTUS_MAT = null;
function cactusMat(){
  if(CACTUS_MAT) return CACTUS_MAT;
  const tex = new THREE.TextureLoader().load(OBST_TEX.cactus);
  tex.colorSpace = THREE.SRGBColorSpace;
  CACTUS_MAT = new THREE.SpriteMaterial({ map:tex, transparent:true, depthWrite:false });
  return CACTUS_MAT;
}
function buildCactus(px,pz,seed){
  const spr = new THREE.Sprite(cactusMat());
  spr.scale.set(1.15, 1.8, 1);     // 比例贴合贴图 ar=0.64
  spr.position.set(px, 0.9, pz);   // 中心抬升到半高，站地
  spr.renderOrder = 1;
  return spr;
}
// 山川高石山（阻挡，比岩石更大更挺拔）
function buildMountainRock(px,pz,seed){
  const g = new THREE.Group();
  const shades=[0x8d949d,0x7d8791,0x9aa0a8];
  const main = new THREE.Mesh(new THREE.ConeGeometry(1.0+seed*0.5, 2.2+seed*0.9, 7), new THREE.MeshLambertMaterial({color:shades[Math.floor(seed*3)]}));
  main.position.set(px, 1.1+seed*0.45, pz); main.castShadow=true;
  const snow = new THREE.Mesh(new THREE.ConeGeometry((1.0+seed*0.5)*0.5, 0.7, 7), new THREE.MeshLambertMaterial({color:0xeef3f7}));
  snow.position.set(px, 1.95+seed*0.75, pz);
  g.add(main, snow);
  const rubbleMat = new THREE.MeshLambertMaterial({color:0x737c86});
  for(let i=0;i<3;i++){
    const rr=0.3+rng(px*11+i,pz*13+i)*0.35;
    const rock=new THREE.Mesh(new THREE.DodecahedronGeometry(rr,0), rubbleMat);
    rock.position.set(px+(rng(px*7+i,pz*3+i)-0.5)*1.2, 0.25, pz+(rng(px*17+i,pz*5+i)-0.5)*1.2);
    g.add(rock);
  }
  return g;
}

/* ===== 地图：无限程序化随机生成 ===== */
const MAP_CELL = 16; // 分块大小，按块懒生成
const chunkMap = new Map(); // "x,z" -> { grass, obstacles }
// 简单确定性哈希（同坐标永远同随机，Math.imul 避免 32 位溢出偏置，保证均匀分布）
function rng(x,z){
  let h = (Math.imul(x|0,0x9E3779B1) + Math.imul(z|0,0x85EBCA6B)) >>> 0;
  h = Math.imul(h ^ (h>>>16), 0x21E0E4F9) >>> 0;
  h = Math.imul(h ^ (h>>>15), 0x735A2D97) >>> 0;
  h = (h ^ (h>>>15)) >>> 0;
  return h / 4294967296;
}

// 障碍物列表（用于碰撞），记录在块内
const obstacleList = []; // {x,z,r} 阻挡玩家与怪物