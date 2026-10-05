/* 01_config.js —— 全局常量·数据定义·存档
 依赖：assets/tex_data.js(ALL_TEX) */
/* ==== 全局常量与工具 ==== */
const GRASS_COLORS = [0x6fcf6a, 0x7fcf58, 0x63c96f, 0x7cd172];


// ALL_TEX 由 assets/tex_data.js 定义
const $ = id => document.getElementById(id);

/* ===== 数据定义 ===== */

// 角色贴图全局预加载：纹理就绪后才挂载到 Sprite，避免渲染未就绪纹理导致崩溃
const ALL_READY = {};
const ALL_MATS = {};
Object.keys(ALL_TEX).forEach(role=>{
  ALL_READY[role] = { face:false, back:false, left:false, right:false, atk:false };
  ALL_MATS[role] = {};
});
(function preloadRoleTex(){
  const l = new THREE.TextureLoader();
  Object.keys(ALL_TEX).forEach(role=>{
    ['face','back','left','right','atk'].forEach(k=>{
      if(!ALL_TEX[role][k]) return; // 无该帧（如未生成攻击帧）则跳过
      l.load(ALL_TEX[role][k], tex=>{
        tex.colorSpace = THREE.SRGBColorSpace;
        ALL_MATS[role][k] = new THREE.SpriteMaterial({ map:tex, transparent:true, depthWrite:false });
        ALL_READY[role][k] = true;
      }, undefined, ()=>{});
    });
  });
})();
// 人类角色（局外金币解锁，局内初始被动）—— 传奇职业主题
const ROLES = [
  { id:'warrior',  name:'传奇战士', price:0,    icon:'🗡', color:0xff7aa2, passive:'生命+30，普攻伤害+15%，初始旋风飞刃',
    stats:{ maxHp:130, atkMul:1.15, speed:5.5, expMul:1 }, grantSkills:['blade'] },
  { id:'mage',     name:'传奇法师', price:200,  icon:'🔮', color:0x8a6bff, passive:'自带火球术Lv1，技能冷却-10%',
    stats:{ maxHp:100, atkMul:1, speed:5.2, expMul:1 }, grantSkills:['fireball'] },
  { id:'ranger',   name:'丛林猎手', price:300,  icon:'🏹', color:0x4f8cff, passive:'移速+18%，初始追踪圣光箭',
    stats:{ maxHp:90, atkMul:1, speed:6.5, expMul:1 }, grantSkills:['holy'] },
  { id:'priest',   name:'传奇道士', price:500,  icon:'✨', color:0xffce4d, passive:'自带再生被动Lv1，初始神圣藤蔓',
    stats:{ maxHp:110, atkMul:1, speed:5.2, expMul:1 }, grantSkills:['vine'], grantPassives:['regen'] },
  { id:'berserk',  name:'狂野蛮王', price:600,  icon:'⚔', color:0xff6b6b, passive:'攻击+25%但移速-5%，自带坚韧Lv1，初始狂暴闪电',
    stats:{ maxHp:125, atkMul:1.25, speed:5.2, expMul:1 }, grantSkills:['lightning'], grantPassives:['tough'] },
  { id:'scholar',  name:'暗影刺客', price:800,  icon:'🎓', color:0x3a8fbf, passive:'经验获取+25%，升级可多刷新1次，初始奥术冰霜',
    stats:{ maxHp:95, atkMul:1, speed:5.4, expMul:1.25 }, grantSkills:['frostnova'] }
];

// 技能池：active=主动（自动释放），passive=被动（常驻）
const SKILLS = {
  fireball:{ id:'fireball', name:'火球术', type:'active', icon:'🔥', color:0xff8a3c, cd:1.6, desc:'朝最近敌人发射火球，爆炸范围伤害',
    cast:(p)=>p.abilities.castFireball(),
    level:function(l){ return { damage:30+10*l, count:1+Math.floor(l/3), speed:11+l*1.4 }; } },
  frostnova:{ id:'frostnova', name:'冰霜新星', type:'active', icon:'❄', color:0x8ad4ff, cd:4, desc:'自身周围冰环，冰冻并减速敌人',
    cast:(p)=>p.abilities.castFrostnova(),
    level:function(l){ return { damage:40+13*l, radius:3.2+l*0.6, slow:0.5, slowTime:1.2+l*0.25 }; } },
  lightning:{ id:'lightning', name:'闪电链', type:'active', icon:'⚡', color:0xffce4d, cd:2.2, desc:'电击最近敌人并弹射多个目标',
    cast:(p)=>p.abilities.castLightning(),
    level:function(l){ return { damage:25+9*l, chains:2+l, range:6+l*0.8 }; } },
  blade:{ id:'blade', name:'旋风飞刃', type:'active', icon:'🌀', color:0x79c96b, cd:0.5, desc:'环绕自身的旋转飞刃持续切割',
    cast:(p)=>p.abilities.castBlade(),
    level:function(l){ return { damage:12+5*l, count:1+l, radius:2.4+l*0.3 }; } },
  holy:{ id:'holy', name:'神圣喷涌', type:'active', icon:'⭐', color:0xffffff, cd:3.5, desc:'圣光球自动追踪最近敌人',
    cast:(p)=>p.abilities.castHoly(),
    level:function(l){ return { damage:55+20*l, speed:9, homing:true }; } },
  vine:{ id:'vine', name:'藤蔓缠绕', type:'active', icon:'🌿', color:0x3fae5a, cd:5, desc:'脚下生成缠绕区域束缚并持续伤害',
    cast:(p)=>p.abilities.castVine(),
    level:function(l){ return { damage:15+6*l, radius:2.8+l*0.5, duration:2.5+l*0.6 }; } },
  atk:{ id:'atk', name:'攻击强化', type:'passive', icon:'💪', color:0xff6b6b, desc:'全部技能与普攻伤害+12%',
    apply:(p,l)=>p.passives.atk += 0.12*l },
  haste:{ id:'haste', name:'急速', type:'passive', icon:'👟', color:0x4f8cff, desc:'移动速度+10%',
    apply:(p,l)=>p.passives.haste += 0.10*l },
  tough:{ id:'tough', name:'坚韧', type:'passive', icon:'🛡', color:0x8a6bff, desc:'最大生命+25',
    apply:(p,l)=>{ p.passives.tough += 25*l; p.maxHp = p.baseMaxHp + p.passives.tough; if(p.hp>p.maxHp)p.hp=p.maxHp; } },
  cdr:{ id:'cdr', name:'回能', type:'passive', icon:'⏱', color:0xffce4d, desc:'技能冷却-12%',
    apply:(p,l)=>p.passives.cdr += 0.12*l },
  greed:{ id:'greed', name:'贪婪', type:'passive', icon:'💰', color:0xffd24d, desc:'金币与经验获取+15%',
    apply:(p,l)=>p.passives.greed += 0.15*l },
  regen:{ id:'regen', name:'再生', type:'passive', icon:'❤', color:0xff7aa2, desc:'每秒回复0.5生命',
    apply:(p,l)=>p.passives.regen += 0.5*l }
};

// 怪物基础模板（传奇主题命名；血量已整体上调：前期技能伤害约40，小怪扛2~4次，BOSS需持续输出）
const MONSTER_TYPES = {
  slime:  { name:'森林幼龙',  color:0x5fcf7f, hp:85,   speed:1.7, radius:0.45, exp:8,  gold:[0,2], tex:'slime' },
  ghost:  { name:'幽魂术士',  color:0xb39fff, hp:160,  speed:2.1, radius:0.5,  exp:14, gold:[1,3], tex:'ghost' },
  runner: { name:'烈焰灵狐',  color:0xffce6b, hp:120,  speed:3.2, radius:0.42, exp:16, gold:[1,3], tex:'runner' },
  brute:  { name:'沃玛勇士',  color:0x8a9a6a, hp:320,  speed:1.1, radius:0.9,  exp:35, gold:[4,7], boss:false, tex:'brute' },
  boss:   { name:'沃玛教主',  color:0x8a6bff, hp:3200, speed:0.9, radius:2.0,  exp:180,gold:[40,60], boss:true, tex:'boss' },
  final:  { name:'祖玛教主',  color:0xff4d5a, hp:16000,speed:0.8, radius:2.8,  exp:900,gold:[200,200], boss:true, final:true, tex:'final' }
};

// 存档键
const SAVE_KEY = 'grass-mow-save';
// 拾取物掉落常量
const DROP_RATE = { gold:0.30, potion:0.06, buff:0.04 };
/* ===== 存档（localStorage） ===== */
const defaultSave = { totalCoins:0, unlocked:['warrior'], records:[] };
let save = loadSave();
function loadSave(){
  try { const s = JSON.parse(localStorage.getItem(SAVE_KEY)); return Object.assign({}, defaultSave, s); }
  catch(e){ return { ...defaultSave }; }
}
function persistSave(){ try { localStorage.setItem(SAVE_KEY, JSON.stringify(save)); } catch(e){} }
function isUnlocked(id){ return save.unlocked.includes(id); }
// 解锁角色（扣金币）
function unlockRole(id){
  const r = ROLES.find(x=>x.id===id); if(!r||isUnlocked(id)) return false;
  if(save.totalCoins < r.price) return false;
  save.totalCoins -= r.price; save.unlocked.push(id); persistSave(); return true;
}
// 结算：累加金币 + 记录
function settleRun(roleId, aliveTime, kills, won, gained){
  save.totalCoins += gained; 
  save.records.push({ role:roleId, time:aliveTime, kills, won, coins:gained, at:Date.now() });
  if(save.records.length>50) save.records.shift();
  persistSave();
}