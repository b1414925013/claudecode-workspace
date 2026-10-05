/* 05_world.js —— buildChunk 分块生成·障碍碰撞 */
// 传奇地表贴图材质（按地貌缓存；tile 平铺 × 顶点色染色）
const GROUND_MATS = {};
function groundMat(biome){
  if(GROUND_MATS[biome]) return GROUND_MATS[biome];
  const tex = new THREE.TextureLoader().load(MIR_GROUND_TEX[biome] || MIR_GROUND_TEX.grass);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(2.2, 1.5);   // 96×64 tile 在 16×16 块上平铺约 2 周期
  const m = new THREE.MeshLambertMaterial({ vertexColors:true, map:tex });
  GROUND_MATS[biome] = m;
  return m;
}
function buildChunk(cx, cz){
  const key = cx+','+cz;
  if(chunkMap.has(key)) return;
  const group = new THREE.Group();
  // 地貌地面：细分 plane + 逐顶点地貌色 + 卡通起伏（无方格拼接）
  const biome = biomeOf(cx*MAP_CELL + MAP_CELL/2, cz*MAP_CELL + MAP_CELL/2);
  const SEG = 5;
  const gGeo = new THREE.PlaneGeometry(MAP_CELL, MAP_CELL, SEG, SEG);
  gGeo.rotateX(-Math.PI/2);
  const posA = gGeo.attributes.position;
  const colors = new Float32Array(posA.count*3);
  for(let i=0;i<posA.count;i++){
    const wx = cx*MAP_CELL + MAP_CELL/2 + posA.getX(i);
    const wz = cz*MAP_CELL + MAP_CELL/2 + posA.getZ(i);
    const b = biomeOf(wx, wz);
    const arr = BIOME_COLORS[b];
    const c = arr[Math.floor(rng(Math.floor(wx)*31, Math.floor(wz)*57)*arr.length)];
    colors[i*3]=((c>>16)&255)/255; colors[i*3+1]=((c>>8)&255)/255; colors[i*3+2]=(c&255)/255;
    posA.setY(i, groundHeight(wx, wz, b));
  }
  gGeo.setAttribute('color', new THREE.BufferAttribute(colors,3));
  gGeo.computeVertexNormals();
  const gMat = groundMat(biome);   // 传奇地表 tile 纹理（×顶点色染色）
  const grass = new THREE.Mesh(gGeo, gMat);
  grass.position.set(cx*MAP_CELL + MAP_CELL/2, 0, cz*MAP_CELL + MAP_CELL/2);
  grass.receiveShadow = true;
  group.add(grass);

  // 块内随机障碍物：阔叶树/松树/岩石堆/栅栏柱(阻挡) + 木桶/箱子(可破坏) + 喷泉/塔楼(地标)
  const seed = rng(cx+999, cz+777);
  const obstacleCount = 4 + Math.floor(seed*5);
  const chunkX0 = cx*MAP_CELL, chunkZ0 = cz*MAP_CELL;
  // 地标：每块约25%概率生成一座喷泉或塔楼（场景参照 / BOSS 战参照物）；不放河面
  if(rng(cx*17, cz*29) < 0.25){
    const lm = rng(cx*71, cz*41);
    const lx = chunkX0 + MAP_CELL*0.5 + (rng(cx*3,cz*5)-0.5)*4;
    const lz = chunkZ0 + MAP_CELL*0.5 + (rng(cx*11,cz*7)-0.5)*4;
    const lb = biomeOf(lx, lz);
    if(lb !== 'river'){
      const gy = groundHeight(lx, lz, lb);
      if(lm < 0.5){
        const f=buildFountain(lx, lz, lm); f.position.y += gy; group.add(f);
        obstacleList.push({ x:lx, z:lz, r:1.6, type:'fountain', kind:'block' });
        landmarks.push({ x:lx, z:lz, type:'fountain' });
      } else {
        const tw=buildRuinTower(lx, lz, lm); tw.position.y += gy; group.add(tw);
        obstacleList.push({ x:lx, z:lz, r:1.5, type:'tower', kind:'block' });
        landmarks.push({ x:lx, z:lz, type:'tower' });
      }
    }
  }
  // 树木成片：草地地块生成1~2个树丛，每丛4~6棵树围绕树丛中心聚集（而非孤零零单棵）
  if(biome==='grass'){
    const groves = 1 + Math.floor(rng(cx*37, cz*61)*1.6);
    const gcc = [chunkX0+MAP_CELL/2, chunkZ0+MAP_CELL/2];
    for(let gi=0; gi<groves; gi++){
      const gcX = gcc[0] + (rng(cx*5+gi*13, cz*9+gi*7)-0.5)*7;
      const gcZ = gcc[1] + (rng(cx*7+gi*3, cz*11+gi*17)-0.5)*7;
      if(biomeOf(gcX, gcZ)!=='grass') continue;
      const nTrees = 4 + Math.floor(rng(cx*19+gi, cz*23+gi)*2.5);
      for(let ti=0; ti<nTrees; ti++){
        const ang = rng(cx*29+gi*5+ti, cz*31+gi*3+ti)*Math.PI*2;
        const rr = 0.6 + rng(cx*37+gi*7+ti, cz*41+gi*11+ti)*2.0;
        const tx = gcX + Math.cos(ang)*rr, tz = gcZ + Math.sin(ang)*rr;
        if(tx<chunkX0+0.8||tx>chunkX0+MAP_CELL-0.8||tz<chunkZ0+0.8||tz>chunkZ0+MAP_CELL-0.8) continue;
        const tb = biomeOf(tx, tz); if(tb!=='grass') continue;
        const isPine = rng(tx*13+tz, tz*7+tx)<0.45;
        const gy = groundHeight(tx, tz, tb);
        let ob={ x:tx, z:tz, r:0.5, type:isPine?'pine':'tree', kind:'block' };
        if(isPine){ const m=buildPine(tx,tz,rng(tx*3,tz*5)); m.position.y+=gy; group.add(m); }
        else { const m=buildTree(tx,tz,rng(tx*3,tz*5)); m.position.y+=gy; group.add(m); }
        obstacleList.push(ob);
      }
    }
  }
  // 障碍数量：草地因已有成片树丛，散布障碍减少；河流地块显著稀疏
  const obsCount = biome==='grass' ? 3 : (biome==='river' ? Math.max(1, obstacleCount-3) : obstacleCount);
  for(let i=0;i<obsCount;i++){
    const s1 = rng(cx*31+i, cz*17+i);
    const px = chunkX0 + 1.5 + s1*(MAP_CELL-3);
    const s2 = rng(cx*53+i, cz*29+i);
    const pz = chunkZ0 + 1.5 + s2*(MAP_CELL-3);
    const s3 = rng(cx*73+i, cz*43+i);
    // 类型权重按【障碍实际坐标】的地貌决定，避免石山/仙人掌落入河面
    const obsBiome = biomeOf(px, pz);
    let kind;
    if(obsBiome==='desert'){ // 沙漠：仙人掌+岩石+栅栏+可破坏
      if(s3<0.30) kind='cactus';
      else if(s3<0.52) kind='rock';
      else if(s3<0.70) kind='fence';
      else if(s3<0.86) kind='barrel';
      else kind='crate';
    } else if(obsBiome==='mountain'){ // 山川：石山+岩石+栅栏
      if(s3<0.40) kind='mrock';
      else if(s3<0.62) kind='rock';
      else if(s3<0.82) kind='fence';
      else if(s3<0.93) kind='crate';
      else kind='barrel';
    } else if(obsBiome==='river'){ // 河流：稀疏的小石+木桶+箱子
      if(s3<0.5) kind='rock';
      else if(s3<0.75) kind='barrel';
      else kind='crate';
    } else { // 草地：岩石+栅栏+可破坏（树木已按树丛成片生成）
      if(s3<0.30) kind='rock';
      else if(s3<0.55) kind='fence';
      else if(s3<0.72) kind='barrel';
      else kind='crate';
    }
    const isBreakable = (kind==='barrel'||kind==='crate');
    const radius = kind==='fence' ? 0.35 : kind==='barrel' ? 0.5 : kind==='crate' ? 0.6 : kind==='rock' ? (0.55+s3*0.4) : kind==='cactus' ? 0.4 : kind==='mrock' ? (1.1+s3*0.5) : 0.5;
    let ob = { x:px, z:pz, r:radius, type:kind, kind:isBreakable?'breakable':'block' };
    const gy = groundHeight(px, pz, biomeOf(px,pz));
    if(kind==='tree'){ const m=buildTree(px, pz, s3); m.position.y += gy; group.add(m); }
    else if(kind==='pine'){ const m=buildPine(px, pz, s3); m.position.y += gy; group.add(m); }
    else if(kind==='rock'){ const m=buildRockPile(px, pz, s3, radius); m.position.y += gy; group.add(m); }
    else if(kind==='cactus'){ const m=buildCactus(px, pz, s3); m.position.y += gy; group.add(m); }
    else if(kind==='mrock'){ const m=buildMrock(px, pz, s3); m.position.y += gy; group.add(m); }
    else if(kind==='fence'){ const m=buildFencePost(px, pz, s3); m.position.y += gy; group.add(m); }
    else if(kind==='barrel'){ const b=buildBarrel(px,pz,s3); b.position.y += gy; group.add(b); ob.mesh=b; ob.hp=25; }
    else { const c=buildCrate(px,pz,s3); c.position.y += gy; group.add(c); ob.mesh=c; ob.hp=35; }
    obstacleList.push(ob);
  }
  scene.add(group);
  chunkMap.set(key, { group });
}

// 懒加载玩家周围块
function updateChunks(px, pz){
  const cxc = Math.floor(px/MAP_CELL), czc = Math.floor(pz/MAP_CELL);
  for(let dx=-2;dx<=2;dx++) for(let dz=-2;dz<=2;dz++) buildChunk(cxc+dx, czc+dz);
}

// 障碍物碰撞：把实体(玩家/怪物)推出圆形障碍
function collideObstacles(pos, radius){
  for(const o of obstacleList){
    if(o.destroyed) continue;
    const ddx = pos.x-o.x, ddz = pos.z-o.z;
    const dist = Math.hypot(ddx,ddz);
    const min = radius + o.r;
    if(dist < min){
      if(dist===0){ pos.x = o.x+min; pos.z = o.z; }
      else { pos.x = o.x + ddx/dist*min; pos.z = o.z + ddz/dist*min; }
    }
  }
}