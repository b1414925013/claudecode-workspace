/* 08_enemies.js —— 怪物生成/移动/伤害 */
/* ===== 怪物贴图精灵（卡通3D，替代球体几何） ===== */
// MON_TEX 由 assets/tex_data.js 定义
const MONSTER_MATS = {};
const MONSTER_READY = {};
(function preloadMonster(){
  const l = new THREE.TextureLoader();
  ['slime','ghost','runner','brute','boss','final'].forEach(k=>{
    MONSTER_READY[k]=false;
    MONSTER_MATS[k]={ face:null, back:null };
    let n=0;
    ['face','back'].forEach(f=>{
      l.load(MON_TEX[k][f], tex=>{
        tex.colorSpace = THREE.SRGBColorSpace;
        MONSTER_MATS[k][f] = new THREE.SpriteMaterial({ map:tex, transparent:true, depthWrite:false });
        n++; if(n>=2) MONSTER_READY[k]=true;
        // 记录正面帧宽高比，供按比例适配精灵尺寸
        const img = tex.image;
        if(img && img.width) MONSTER_MATS[k]._aspect = img.width/img.height;
      }, undefined, ()=>{});
    });
  });
})();
let monsters = []; // {mesh, pos, hp, type, dead, slow, slowTime, scale, baseH}
function dist2D(a,b){ return Math.hypot(a.x-b.x, a.z-b.z); }
function nearestMonster(from, maxDist=999, filter){
  let best=null, bd=maxDist;
  for(const m of monsters){
    if(m.dead) continue;
    if(filter && !filter(m)) continue;
    const d = dist2D(from, m.pos);
    if(d<bd){ bd=d; best=m; }
  }
  return best;
}
// 计算怪物精灵尺寸：按传奇帧实际宽高比适配（宽基准 scale*1.3，高上限 scale*2.4）
function monsterSize(type, scale){
  const aspect = MONSTER_MATS[type.tex]._aspect || 0.72;  // 未加载时用贴图库默认比例
  let w = scale*1.3, h = w/aspect;
  if(h > scale*2.4){ h = scale*2.4; w = h*aspect; }
  return { w, h };
}
// 创建怪物：传奇贴图精灵（billboard 自动面向相机）
function buildMonsterMesh(type, scale){
  const mat = MONSTER_MATS[type.tex].face || new THREE.SpriteMaterial();
  const spr = new THREE.Sprite(mat);
  const { w, h } = monsterSize(type, scale);
  spr.scale.set(w, h, 1);
  spr.position.y = h/2;  // 中心抬升对应 Sprite 半高
  spr.renderOrder = 10;  // 高于树/障碍(1)与玩家，确保怪物不被静态障碍遮挡
  spr.userData.phase = Math.random()*Math.PI*2;  // 浮动相位
  spr.userData.animT = 0;
  spr.userData.mats = MONSTER_MATS[type.tex];   // {face,back} 材质，供四向切换
  spr.userData.baseW = w;                       // 基准宽（左右翻转用）
  spr.userData.baseH = h;
  return spr;
}
function spawnMonster(typeId, px, pz){
  const type = MONSTER_TYPES[typeId];
  const scale = type.boss ? (type.final?2.5:2.0) : (0.8+Math.random()*0.5);
  const mesh = buildMonsterMesh(type, scale);
  const pos = { x:px, z:pz };
  // 站在起伏地形上（与障碍一致），并抬升到怪物主体中心高度，避免身体埋入地面
  const gy = groundHeight(px, pz, biomeOf(px, pz));
  const baseH = mesh.userData.baseH;
  mesh.position.set(px, gy + baseH/2, pz);
  // 避免出生在玩家身边过近
  scene.add(mesh);
  monsters.push({ mesh, pos, hp:type.hp*(type.boss?1: scale<1?1:1.15), type, dead:false, slow:0, slowTime:0, scale, baseH });
}
function removeMonsterMesh(m){
  scene.remove(m.mesh);
  const idx = monsters.indexOf(m); if(idx>=0) monsters.splice(idx,1);
}
function effectBurst(x,z,color){
  const burst = makeGlow(color,0.6); burst.position.set(x,0.8,z); scene.add(burst);
  effects.push({ mesh:burst, life:0.3, update:(e,t)=>e.mesh.scale.setScalar(1+t*3) });
}

// 刷怪逻辑
let spawnTimer=0, bossSpawned=0, finalSpawned=false, bossDead=false;
function updateSpawning(dt, elapsed){
  const minute = elapsed/60;
  // 普通怪按公式动态生成
  spawnTimer -= dt;
  const gap = Math.max(0.35, 1.2 - minute*0.06);
  if(spawnTimer<=0){
    spawnTimer = gap;
    const cap = 80 + Math.floor(minute*12);
    if(monsters.length < cap){
      const ang = Math.random()*Math.PI*2;
      const r = 26 + Math.random()*10;
      const px = player.pos.x+Math.cos(ang)*r;
      const pz = player.pos.z+Math.sin(ang)*r;
      // 按分钟选类型
      let tid='slime';
      const roll = Math.random();
      if(minute<3){ tid = roll<0.85?'slime':'ghost'; }
      else if(minute<5){ tid = roll<0.6?'slime':(roll<0.9?'ghost':'runner'); }
      else if(minute<10){ tid = roll<0.5?'slime':(roll<0.8?'ghost':(roll<0.95?'runner':'brute')); }
      else { tid = roll<0.45?'slime':(roll<0.7?'ghost':(roll<0.9?'runner':'brute')); }
      spawnMonster(tid, px, pz);
    }
  }
  // BOSS：每5分钟1只
  const bossDue = Math.floor(elapsed/300);
  if(bossDue>bossSpawned && !finalSpawned && elapsed>=15){
    bossSpawned = bossDue;
    let bx, bz, note='';
    if(landmarks.length){
      const lm = landmarks[Math.floor(Math.random()*landmarks.length)];
      bx=lm.x; bz=lm.z;
      note='于'+(lm.type==='fountain'?'喷泉':'废墟石柱')+'旁现身';
    } else { const ang=Math.random()*Math.PI*2; bx=player.pos.x+Math.cos(ang)*24; bz=player.pos.z+Math.sin(ang)*24; }
    announce('⚔ BOSS 降临！'+note,'warn');
    spawnMonster('boss', bx, bz);
  }
  // 终极：15分钟
  if(!finalSpawned && elapsed>=900){
    finalSpawned = true;
    announce('☠ 祖玛教主降临！击杀通关！','danger');
    const ang=Math.random()*Math.PI*2;
    spawnMonster('final', player.pos.x+Math.cos(ang)*22, player.pos.z+Math.sin(ang)*22);
  }
}

// 怪物移动：朝玩家，受障碍阻挡；碰到玩家造成伤害
function updateMonsters(dt){
  for(const m of monsters){
    if(m.dead) continue;
    if(m.slowTime>0){ m.slowTime-=dt; m.slow=0.5; } else m.slow=0;
    const spd = m.type.speed*(1-m.slow*0.6)*(m.type.final?0.8:1);
    const dx = player.pos.x-m.pos.x, dz = player.pos.z-m.pos.z;
    const d = Math.hypot(dx,dz)||1;
    const base = Math.atan2(dx,dz);
    // 障碍绕行：主方向朝玩家，若前方被障碍阻挡则依次尝试左右偏转方向，避免卡在障碍前
    let moved=false;
    const cands=[base, base+1.05, base-1.05, base+2.2, base-2.2, base+3.4, base-3.4];
    for(const a of cands){
      const tx = THREE.MathUtils.clamp(m.pos.x+Math.sin(a)*spd*dt, -WORLD_LIMIT, WORLD_LIMIT);
      const tz = THREE.MathUtils.clamp(m.pos.z+Math.cos(a)*spd*dt, -WORLD_LIMIT, WORLD_LIMIT);
      const test={ x:tx, z:tz };
      const bx=test.x, bz=test.z;
      collideObstacles(test, m.type.radius);
      if(Math.abs(test.x-bx)<0.0001 && Math.abs(test.z-bz)<0.0001){
        m.pos.x=test.x; m.pos.z=test.z; moved=true; break;
      }
    }
    if(!moved) collideObstacles(m.pos, m.type.radius);
    // 四向朝向：按移动方向相对屏幕切换正面/背面帧 + 左右镜像翻转
    const camDir = new THREE.Vector3(); camera.getWorldDirection(camDir);
    const lookH = new THREE.Vector2(camDir.x, camDir.z); if(lookH.lengthSq()>1e-4) lookH.normalize();
    const rightH = new THREE.Vector2(-lookH.y, lookH.x);
    const mvx = player.pos.x-m.pos.x, mvz = player.pos.z-m.pos.z;
    const dotF = mvx*lookH.x + mvz*lookH.y;
    const dotR = mvx*rightH.x + mvz*rightH.y;
    const dir = Math.abs(dotF)>=Math.abs(dotR) ? (dotF>=0?'back':'face') : (dotR>=0?'right':'left');
    const mats = m.mesh.userData.mats;
    const target = dir==='back' ? mats.back : mats.face;
    if(target && m.mesh.material!==target){ m.mesh.material=target; }
    m.mesh.scale.x = (dir==='left') ? -Math.abs(m.mesh.userData.baseW) : Math.abs(m.mesh.userData.baseW);
    // 贴图精灵浮动动画：不同怪物幅度/节奏不同（BOSS 更沉稳）
    const ud = m.mesh.userData;
    ud.animT = (ud.animT||0) + dt;
    const amp = (m.type.final?0.15 : m.type.boss?0.18 : m.type.ghost?0.28 : 0.14) * Math.min(1, m.scale);
    const bob = Math.sin(ud.animT*(m.type.ghost?5:4) + ud.phase)*amp;
    // 贴地高度 = 地形起伏 + 怪物主体中心 + 浮动
    const gy = groundHeight(m.pos.x, m.pos.z, biomeOf(m.pos.x, m.pos.z));
    m.mesh.position.set(m.pos.x, gy + m.baseH/2 + bob, m.pos.z);
    // 接触伤害
    if(d < 0.9 + m.type.radius*0.8){
      const dmg = m.type.final ? 20 : 14;
      damagePlayer(dmg);
    }
  }
}