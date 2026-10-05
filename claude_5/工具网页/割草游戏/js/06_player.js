/* 06_player.js —— 玩家模型/输入/移动/受击/动画 */
/* ===== 玩家 ===== */
const keys = { w:false,a:false,s:false,d:false };
window.addEventListener('keydown', e=>{ if(e.key==='w'||e.key==='W')keys.w=true; if(e.key==='a'||e.key==='A')keys.a=true; if(e.key==='s'||e.key==='S')keys.s=true; if(e.key==='d'||e.key==='D')keys.d=true; });
window.addEventListener('keyup',   e=>{ if(e.key==='w'||e.key==='W')keys.w=false; if(e.key==='a'||e.key==='A')keys.a=false; if(e.key==='s'||e.key==='S')keys.s=false; if(e.key==='d'||e.key==='D')keys.d=false; });

// 构建玩家卡通3D模型（圆头+身体+手臂）
function buildCharacter(color, role){
  return buildSpriteRole(color, role);
  const g = new THREE.Group();
  const bodyMat = new THREE.MeshLambertMaterial({ color });
  const headMat = new THREE.MeshLambertMaterial({ color:0xffd9b3 });
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.55,0.9,8), bodyMat); body.position.y=0.55; body.castShadow=true;
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.42,12,10), headMat); head.position.y=1.45; head.castShadow=true;
  // 眼睛
  const eyeMat = new THREE.MeshBasicMaterial({ color:0x233046 });
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.08,8,6), eyeMat); eye.position.set(0.14,1.5,0.36);
  const eye2 = eye.clone(); eye2.position.x=-0.14;
  g.add(body,head,eye,eye2);
  // 小帽（职业头饰）
  const hatMat = new THREE.MeshLambertMaterial({ color });
  const hat = new THREE.Mesh(new THREE.ConeGeometry(0.4,0.5,8), hatMat); hat.position.y=1.85; g.add(hat);
  return g;
}

// 四向贴图角色（传奇时装帧）：THREE.Sprite 自动 billboard 朝向相机，按移动方向切换帧，行走/攻击程序化动画
function buildSpriteRole(color, role){
  const g = new THREE.Group();
  // 初始空材质（无 map），纹理就绪前不渲染，避免崩
  const spr = new THREE.Sprite(new THREE.SpriteMaterial({ transparent:true, depthWrite:false }));
  spr.scale.set(1.7, 2.5, 1); // 默认世界尺寸：宽1.7 高2.5（贴图就绪后按宽高比重算）
  spr.position.y = 1.25;      // 底部贴地
  g.add(spr);
  g.userData.sprite = { spr, mats:ALL_MATS[role], ready:ALL_READY[role], baseW:1.7, baseH:2.5, fit:false };
  return g;
}
// 每帧：四向帧切换 + 行走弹跳 + 攻击挥摆（Sprite 自动面向相机）
function updateSpritePlayer(dt){
  const sd = player.mesh.userData.sprite;
  if(!sd) return;
  const spr = sd.spr;
  // 首次贴图就绪：按传奇帧实际宽高比修正基准尺寸（高固定 2.5，宽随比例）
  if(!sd.fit && sd.ready.face && sd.mats.face && sd.mats.face.map){
    const img = sd.mats.face.map.image;
    if(img && img.width){
      const ar = img.width/img.height;
      sd.baseH = 2.5; sd.baseW = 2.5*THREE.MathUtils.clamp(ar, 0.45, 1.4);
      sd.fit = true;
    }
  }
  const W = sd.baseW, H = sd.baseH, HALF = H/2;
  const dir = (player.anim.atkT>0 && sd.mats.atk && sd.ready.atk) ? 'atk' : (player.anim.dir || 'face');
  const mat = spr.material;
  if(sd.ready[dir] && sd.mats[dir]){
    if(mat.map !== sd.mats[dir].map){ mat.map = sd.mats[dir].map; mat.needsUpdate = true; }
  } else if(mat.map !== null){ mat.map = null; mat.needsUpdate = true; }
  // 死亡状态：倒地 + 变灰 + 渐隐
  if(player.anim.state==='dead'){
    const k = 1 - Math.max(0, player.anim.deadT/1.1);   // 0 → 1 倒地进度
    spr.position.y = HALF*(1 - k*0.85);
    spr.rotation.z = k*1.5;
    spr.scale.set(W, H*(1 - k*0.45), 1);
    mat.transparent = true;
    if(mat.color) mat.color.set(1, 1-0.55*k, 1-0.55*k);
    if(k>0.55) mat.opacity = Math.max(0, 1-(k-0.55)/0.45);
    mat.needsUpdate = true;
    return;
  }
  // 受击状态：闪红 + 后仰回弹
  if(player.anim.state==='hit'){
    player.anim.hitT -= dt;
    const k = Math.max(0, player.anim.hitT/0.35);
    spr.position.y = HALF + 0.12*k;
    spr.rotation.z = (1-k)*0.45;
    if(mat.color) mat.color.set(1, 1-0.5*k, 1-0.5*k);
    spr.scale.set(W, H, 1);
    if(player.anim.hitT<=0){
      player.anim.state='idle'; player.anim.walk=false;
      if(mat.color) mat.color.set(1,1,1);
      mat.opacity = 1; mat.needsUpdate = true;
    }
    return;
  }
  if(player.anim.atkT>0){
    player.anim.atkT -= dt;
    const k = Math.max(0, player.anim.atkT/0.3);
    spr.position.y = HALF + 0.12*Math.sin(k*Math.PI);
    spr.rotation.z = 0.22*Math.sin(k*Math.PI);   // 屏幕内小挥摆模拟挥击
    spr.scale.set(W+0.25*Math.sin(k*Math.PI), H+0.25*Math.sin(k*Math.PI), 1);
  } else {
    if(player.anim.walk){
      player.anim.bobT += dt*9;
      spr.position.y = HALF + Math.abs(Math.sin(player.anim.bobT))*0.16;
      spr.rotation.z = 0.08*Math.sin(player.anim.bobT*2);
    } else {
      spr.position.y = HALF;
      spr.rotation.z = 0;
    }
    spr.scale.set(W, H, 1);
  }
}

// 技能状态
function makeAbilityState(){
  return {
    actives: [],       // [{skillId, level}]
    passives: [],      // [{skillId, level}]
    timers: {}         // active cooldown 计时
  };
}
// 玩家全局状态
let player = null;
function initPlayer(role){
  const R = ROLES.find(x=>x.id===role) || ROLES[0];
  const mesh = buildCharacter(R.color, R.id);
  scene.add(mesh);
  player = {
    role: role, mesh: mesh, pos: new THREE.Vector3(0,0,0),
    baseMaxHp: R.stats.maxHp, hp: R.stats.maxHp, maxHp: R.stats.maxHp,
    atkMul: R.stats.atkMul, speed: R.stats.speed, expMul: R.stats.expMul,
    passives:{ atk:0, haste:0, tough:0, cdr:0, greed:0, regen:0 },
    abilities: makeAbilityState(),
    level: 1, exp: 0, expNeed: expNeedFor(1),
    coins: 0, kills: 0,
    hitCooldown: 0, dashTimer: 0,
    anim: { dir:'face', walk:false, bobT:0, atkT:0, state:'idle', hitT:0, deadT:0, dead:false }
  };
  player.abilities.castFireball = castFireball;
  player.abilities.castFrostnova = castFrostnova;
  player.abilities.castLightning = castLightning;
  player.abilities.castBlade = castBlade;
  player.abilities.castHoly = castHoly;
  player.abilities.castVine = castVine;
  // 角色自带技能/被动
  if(R.grantSkills) R.grantSkills.forEach(sid=>gainSkill(sid));
  if(R.grantPassives) R.grantPassives.forEach(sid=>gainSkill(sid));
  // 保底：开局至少一个主动技能，保证能自动打怪
  if(player.abilities.actives.length===0) gainSkill('fireball');
}
function expNeedFor(lv){ return Math.round(8*Math.pow(lv+1,1.6)); }

// 获得/升级技能：返回该技能的现有等级（新获得=1）
function gainSkill(sid){
  const ab = player.abilities;
  const arr = SKILLS[sid].type==='active' ? ab.actives : ab.passives;
  const ex = arr.find(a=>a.skillId===sid);
  if(ex){ ex.level = Math.min(ex.level+1, 5); }
  else { arr.push({ skillId:sid, level:1 }); if(SKILLS[sid].type==='active') ab.timers[sid]=0; }
  // 应用被动
  if(SKILLS[sid].type==='passive'){
    const l = arr.find(a=>a.skillId===sid).level;
    SKILLS[sid].apply(player, l);
  }
  renderSkillsBar();
  return ex ? ex.level : 1;
}

// 增加经验并处理升级
function addExp(amount){
  player.exp += amount * (1+player.passives.greed) * player.expMul;
  while(player.exp >= player.expNeed){
    player.exp -= player.expNeed;
    player.level++;
    player.expNeed = expNeedFor(player.level);
    openUpgradeModal();
  }
}

// WASD 移动（每帧）
function movePlayer(dt){
  let mx=0, mz=0;
  if(keys.w) mz-=1; if(keys.s) mz+=1; if(keys.a) mx-=1; if(keys.d) mx+=1;
  if(mx||mz){
    const len = Math.hypot(mx,mz); mx/=len; mz/=len;
    let spd = player.speed * (1+player.passives.haste);
    if(biomeOf(player.pos.x, player.pos.z)==='river') spd *= 0.5; // 河流减速（可通行）
    player.pos.x += mx*spd*dt; player.pos.z += mz*spd*dt;
    // 世界边界：不可越出地图范围
    player.pos.x = THREE.MathUtils.clamp(player.pos.x, -WORLD_LIMIT, WORLD_LIMIT);
    player.pos.z = THREE.MathUtils.clamp(player.pos.z, -WORLD_LIMIT, WORLD_LIMIT);
    collideObstacles(player.pos, 0.55);
    player.mesh.position.copy(player.pos);
    const isSprite = player.mesh.userData && player.mesh.userData.sprite;
    if(isSprite){
      // 四向贴图：按移动方向相对屏幕的方向切换帧
      const camDir = new THREE.Vector3(); camera.getWorldDirection(camDir);
      const lookH = new THREE.Vector2(camDir.x, camDir.z);
      if(lookH.lengthSq()>1e-4) lookH.normalize();
      const rightH = new THREE.Vector2(-lookH.y, lookH.x);
      const dotF = mx*lookH.x + mz*lookH.y;
      const dotR = mx*rightH.x + mz*rightH.y;
      player.anim.dir = Math.abs(dotF)>=Math.abs(dotR) ? (dotF>=0?'back':'face') : (dotR>=0?'right':'left');
      player.anim.walk = true;
    } else {
      // 3D 模型朝向移动方向
      player.mesh.rotation.y = Math.atan2(mx,mz);
    }
  } else if(player.anim){
    player.anim.walk = false;
  }
}

// 玩家受击
function damagePlayer(amount){
  if(player.hitCooldown>0 || !player) return;
  player.hp -= amount; player.hitCooldown=0.8;
  if(player.hp>0 && player.mesh.userData && player.mesh.userData.sprite){
    player.anim.state='hit'; player.anim.hitT=0.35;
  }
  updateHp();
  if(player.hp<=0){
    player.hp=0; updateHp();
    if(player.mesh.userData && player.mesh.userData.sprite){
      player.anim.state='dead'; player.anim.deadT=1.1; player.dying=true;
      return;
    }
    endGame(false);
  }
}