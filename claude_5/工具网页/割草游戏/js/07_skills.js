/* 07_skills.js —— 技能施放/弹道/特效 */
/* ===== 技能（主动施法与特效） ===== */
const projectiles = []; // {mesh, dir, speed, damage, life, homing, skill}
const effects = [];     // {mesh, life, update}
// 技能特效贴图（SKILL_TEX）预加载
const SKILL_MATS = {};
(function preloadSkill(){
  const l = new THREE.TextureLoader();
  ['fireball','frostnova','lightning','blade','holy','vine'].forEach(k=>{
    l.load(SKILL_TEX[k], tex=>{ tex.colorSpace=THREE.SRGBColorSpace; SKILL_MATS[k]=new THREE.SpriteMaterial({map:tex, transparent:true, depthWrite:false, depthTest:false}); }, undefined, ()=>{});
  });
})();
// 创建技能特效贴图精灵（billboard 面向相机，depthTest:false 保证发光不被地形/障碍遮挡）
function makeSkillSprite(key, size){
  const spr = new THREE.Sprite(SKILL_MATS[key]);
  spr.scale.set(size, size, 1);
  spr.renderOrder = 20;  // 高于怪物(10)/障碍(1)，特效最上层
  spr.userData.base = size;
  return spr;
}
// 特效材质：MeshBasicMaterial 不受光，天然发光
function makeGlow(color, size){
  const m = new THREE.Mesh(new THREE.SphereGeometry(size,10,8), new THREE.MeshBasicMaterial({ color, transparent:true, opacity:0.9 }));
  return m;
}
// 特效环
function makeRing(color, radius){
  const m = new THREE.Mesh(new THREE.RingGeometry(radius*0.85,radius,24), new THREE.MeshBasicMaterial({ color, transparent:true, opacity:0.8, side:THREE.DoubleSide }));
  m.rotation.x = -Math.PI/2; return m;
}
// 伤害怪物，返回是否击杀（处理血与金币）
function hitMonster(m, dmg){
  m.hp -= dmg;
  if(m.hp<=0){ killMonster(m); return true; }
  return false;
}
function killMonster(m){
  if(m.dead) return;
  m.dead = true;
  player.kills++;
  const type = m.type;
  const gain = type.exp * (1+player.passives.greed);
  addExp(gain);
  // 金币
  const g = type.gold[0]+Math.floor(Math.random()*(type.gold[1]-type.gold[0]+1));
  dropCoin(m.pos.x, m.pos.z, g);
  // 掉落
  spawnDrops(m.pos.x, m.pos.z);
  // 移除网格（延迟以播死亡特效）
  effectBurst(m.pos.x, m.pos.z, type.color);
  removeMonsterMesh(m);
}

function castFireball(){
  const lv = getSkillLevel('fireball'); if(lv<1) return;
  const cfg = SKILLS.fireball.level(lv);
  const target = nearestMonster(player.pos);
  if(!target) return;
  const ang = Math.atan2(target.pos.x-player.pos.x, target.pos.z-player.pos.z);
  const cnt = cfg.count;
  for(let i=0;i<cnt;i++){
    const a = ang + (i-(cnt-1)/2)*0.25;
    const dir = new THREE.Vector3(Math.sin(a),0,Math.cos(a));
    const m = makeSkillSprite('fireball',0.7); m.position.copy(player.pos); m.position.y=0.9; scene.add(m);
    projectiles.push({ mesh:m, dir, speed:cfg.speed, damage:cfg.damage*player.atkMul, life:1.6, skill:'fireball' });
  }
};
function castFrostnova(){
  const lv = getSkillLevel('frostnova'); if(lv<1) return;
  const cfg = SKILLS.frostnova.level(lv);
  const ring = makeSkillSprite('frostnova', cfg.radius*2); ring.position.set(player.pos.x,0.3,player.pos.z); scene.add(ring);
  effects.push({ mesh:ring, life:0.5, update:(e,t)=>{ const b=e.mesh.userData.base; e.mesh.scale.set(b*(1+t*1.2),b*(1+t*1.2),1); } });
  // 范围伤害+减速
  for(const mon of monsters){
    if(mon.dead) continue;
    const d = dist2D(mon.pos, player.pos);
    if(d < cfg.radius+mon.type.radius){
      hitMonster(mon, cfg.damage*player.atkMul);
      mon.slow = cfg.slow; mon.slowTime = cfg.slowTime;
    }
  }
};
// 生成一段闪电电弧（zigzag 折线），用于表现闪电链相邻目标间的连接
function makeLightningBolt(from, to, y=1.2){
  const pts=[]; const dx=to.x-from.x, dz=to.z-from.z; const segs=6;
  for(let i=0;i<=segs;i++){
    const t=i/segs;
    let off=0;
    if(i>0&&i<segs) off=(Math.random()-0.5)*1.0;   // 中间段横向偏移形成曲折
    pts.push(new THREE.Vector3(from.x+dx*t+(Math.random()-0.5)*0.35, y+Math.abs(Math.sin(i*1.4))*0.5, from.z+dz*t+off));
  }
  const geo=new THREE.BufferGeometry().setFromPoints(pts);
  const mat=new THREE.LineBasicMaterial({ color:0xc9ecff, transparent:true, opacity:0.95, depthTest:false });
  const line=new THREE.Line(geo, mat);
  line.renderOrder=22;  // 特效最上层
  return line;
}
function castLightning(){
  const lv = getSkillLevel('lightning'); if(lv<1) return;
  const cfg = SKILLS.lightning.level(lv);
  let cur = nearestMonster(player.pos, cfg.range);
  let chain=0;
  while(cur && chain<cfg.chains){
    const bolt = makeSkillSprite('lightning',1.4); bolt.position.set(cur.pos.x,0.8,cur.pos.z); scene.add(bolt);
    effects.push({ mesh:bolt, life:0.25, update:(e,t)=>{ const b=e.mesh.userData.base; e.mesh.scale.set(b*(1-t*0.5),b*(1-t*0.5),1); } });
    hitMonster(cur, cfg.damage*player.atkMul);
    chain++;
    const prev = cur.pos;
    const next = nearestMonster(prev, cfg.range, mon=>mon!==cur && !mon.dead);
    // 链：在相邻两个目标之间画一道电弧，直观表现"闪电链"弹射
    if(next){
      const arc = makeLightningBolt(prev, next.pos);
      scene.add(arc);
      effects.push({ mesh:arc, life:0.28, update:(e,t)=>{ e.mesh.material.opacity=Math.max(0, 0.95-t/0.28); } });
    }
    cur = next;
  }
};
function castBlade(){
  const lv = getSkillLevel('blade'); if(lv<1) return;
  const cfg = SKILLS.blade.level(lv);
  const n = cfg.count;
  for(let i=0;i<n;i++){
    const ang = player.bladeAng + i*Math.PI*2/n;
    const px = player.pos.x+Math.cos(ang)*cfg.radius;
    const pz = player.pos.z+Math.sin(ang)*cfg.radius;
    const bladeMesh = makeSkillSprite('blade',0.9); bladeMesh.position.set(px,0.6,pz); scene.add(bladeMesh);
    effects.push({ mesh:bladeMesh, life:0.5, update:(e,t)=>{
      // 追踪刀片旋转
      const a2 = player.bladeAng + i*Math.PI*2/n;
      e.mesh.position.set(player.pos.x+Math.cos(a2)*cfg.radius, 0.6, player.pos.z+Math.sin(a2)*cfg.radius);
      // 伤害接触怪物
      for(const mon of monsters){
        if(mon.dead) continue;
        if(dist2D(e.mesh.position, mon.pos) < 0.7+mon.type.radius){ hitMonster(mon, cfg.damage*player.atkMul); }
      }
    } });
  }
  if(player.bladeAng===undefined) player.bladeAng=0;
};
function castHoly(){
  const lv = getSkillLevel('holy'); if(lv<1) return;
  const cfg = SKILLS.holy.level(lv);
  const target = nearestMonster(player.pos);
  if(!target) return;
  const dir = new THREE.Vector3(target.pos.x-player.pos.x, 0, target.pos.z-player.pos.z).normalize();
  const m = makeSkillSprite('holy',0.9); m.position.copy(player.pos); m.position.y=0.9; scene.add(m);
  projectiles.push({ mesh:m, dir, speed:cfg.speed, damage:cfg.damage*player.atkMul, life:2.5, homing:true, skill:'holy' });
};
function castVine(){
  const lv = getSkillLevel('vine'); if(lv<1) return;
  const cfg = SKILLS.vine.level(lv);
  const ring = makeSkillSprite('vine', cfg.radius*2); ring.position.set(player.pos.x,0.2,player.pos.z); scene.add(ring);
  effects.push({ mesh:ring, life:cfg.duration, update:(e,t)=>e.mesh.material.opacity = Math.max(0.2, 0.8-t/cfg.duration*0.5) });
  const zone = { x:player.pos.x, z:player.pos.z, r:cfg.radius, t:cfg.duration, dmg:cfg.damage*player.atkMul };
  effectZones.push(zone);
};
function getSkillLevel(sid){
  const arr = player.abilities.actives.concat(player.abilities.passives);
  const a = arr.find(x=>x.skillId===sid); return a ? a.level : 0;
}

// 每帧更新技能冷却与施法
function updateAbilities(dt){
  player.hitCooldown = Math.max(0, player.hitCooldown-dt);
  // 再生被动
  if(player.passives.regen>0){ player.hp = Math.min(player.maxHp, player.hp+player.passives.regen*dt); updateHp(); }
  // 刀片旋转角
  if(player.bladeAng===undefined) player.bladeAng=0;
  player.bladeAng += dt*3.2;
  // 主动技能自动释放
  for(const a of player.abilities.actives){
    const sid = a.skillId;
    const cd = SKILLS[sid].cd * (1-player.passives.cdr);
    player.abilities.timers[sid] = (player.abilities.timers[sid]||0) - dt;
    if(player.abilities.timers[sid]<=0){
      SKILLS[sid].cast(player);
      if(player.mesh.userData && player.mesh.userData.sprite) player.anim.atkT = 0.3;
      player.abilities.timers[sid] = cd;
    }
  }
  renderSkillsBar();
}
// 弹道更新
function updateProjectiles(dt){
  for(let i=projectiles.length-1;i>=0;i--){
    const p = projectiles[i];
    if(p.homing){
      const t = nearestMonster(p.mesh.position);
      if(t){ const d = new THREE.Vector3(t.pos.x-p.mesh.position.x,0,t.pos.z-p.mesh.position.z).normalize(); p.dir.lerp(d,0.1).normalize(); }
    }
    p.mesh.position.x += p.dir.x*p.speed*dt; p.mesh.position.z += p.dir.z*p.speed*dt;
    p.life -= dt;
    // 障碍碰撞：阻挡类(树/石/栅栏/地标)挡弹道，可破坏物(桶/箱)被技能击碎
    for(const ob of obstacleList){
      if(ob.destroyed) continue;
      if(dist2D(p.mesh.position, ob) < ob.r + 0.3){
        if(ob.kind==='breakable'){ ob.hp -= p.damage; if(ob.hp<=0) breakObstacle(ob); }
        p.life = 0; break;
      }
    }
    // 命中检测
    for(const mon of monsters){
      if(mon.dead) continue;
      if(dist2D(p.mesh.position, mon.pos) < 0.6+mon.type.radius){ hitMonster(mon, p.damage); p.life=0; break; }
    }
    if(p.life<=0){ scene.remove(p.mesh); projectiles.splice(i,1); }
  }
}
const effectZones = []; // 藤蔓区域
function updateEffects(dt){
  for(let i=effects.length-1;i>=0;i--){
    const e = effects[i]; e.life -= dt; if(e.update) e.update(e, 0.06);
    if(e.life<=0){ scene.remove(e.mesh); effects.splice(i,1); }
  }
  for(let i=effectZones.length-1;i>=0;i--){
    const z = effectZones[i]; z.t -= dt;
    if(z.t>0){
      for(const mon of monsters){
        if(mon.dead) continue;
        if(dist2D(mon.pos,{x:z.x,z:z.z}) < z.r+mon.type.radius){ hitMonster(mon, z.dmg*dt*2); }
      }
    } else { effectZones.splice(i,1); }
  }
}