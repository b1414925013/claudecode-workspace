/* 10_ui.js —— HUD/飘字/技能栏/升级弹窗 */
/* ===== HUD ===== */
let runTime = 0; // 对局已过秒
let selectedRole = 'warrior';
let buffTimer = 0;

// 经验条
function updateExpUI(){
  $('expLv').textContent = 'Lv.'+player.level;
  $('expFill').style.width = Math.min(100, player.exp/player.expNeed*100)+'%';
}
// 血量
function updateHp(){
  $('hpTxt').textContent = Math.max(0,Math.floor(player.hp))+' / '+player.maxHp;
  $('hpFill').style.width = Math.max(0, player.hp/player.maxHp*100)+'%';
}
// 时间
function updateTime(){
  const remain = Math.max(0, 900-runTime);
  const mm = Math.floor(remain/60), ss = Math.floor(remain%60);
  $('timeBox').textContent = String(mm).padStart(2,'0')+':'+String(ss).padStart(2,'0');
}
// 金币 UI
function addCoinUI(val){
  $('coinBox').innerHTML = player.coins+'<small>本局 · 累计 '+save.totalCoins+'</small>';
  floatText('+'+val,'#ffd24d');
}
// 飘字
function floatText(txt, color){
  const el = document.createElement('div');
  el.className='floatText'; el.textContent=txt; el.style.color=color||'#fff';
  el.style.left=(Math.random()*40+30)+'%'; el.style.top=(Math.random()*20+30)+'%';
  document.getElementById('hud').appendChild(el);
  setTimeout(()=>el.remove(), 1000);
}
// 公告
function announce(txt, cls){
  const a = $('announce'); a.textContent=txt; a.className='show '+(cls||'');
  setTimeout(()=>a.className='', 2200);
}
// 底部技能栏
function renderSkillsBar(){
  const bar = $('skillsBar');
  const all = player ? player.abilities.actives.concat(player.abilities.passives) : [];
  bar.innerHTML = all.map(a=>{
    const s = SKILLS[a.skillId];
    const cd = s.type==='active' ? player.abilities.timers[a.skillId] : 0;
    const total = s.type==='active' ? s.cd*(1-player.passives.cdr) : 1;
    const pct = s.type==='active' && total>0 ? Math.min(100, cd/total*100) : 0;
    return '<div class="skillIcon"><div class="si-ico">'+s.icon+'</div><div class="si-name">'+s.name+'</div>'+
      (a.level>1?'<div class="si-lv">'+a.level+'</div>':'')+
      (s.type==='active'?'<div class="si-cd" style="height:'+pct+'%"></div>':'')+'</div>';
  }).join('');
}
/* ===== 升级弹窗（三选一） ===== */
function openUpgradeModal(){
  // 暂停主循环施法，弹三选一
  gamePaused = true;
  $('upgModal').classList.add('show');
  const cards = $('upgCards');
  cards.innerHTML = '';
  // 抽取 3 个可选技能：未满级
  const allIds = Object.keys(SKILLS);
  const available = allIds.filter(sid=>{
    const lv = getSkillLevel(sid);
    return lv<5;
  });
  const picked = [];
  while(picked.length<3 && available.length>0){
    const i = Math.floor(Math.random()*available.length);
    const sid = available.splice(i,1)[0];
    picked.push(sid);
  }
  // 避免三选完全相同
  picked.forEach(sid=>{
    const s = SKILLS[sid];
    const cur = getSkillLevel(sid);
    const div = document.createElement('div');
    div.className='upgCard';
    div.innerHTML = '<div class="u-ico">'+s.icon+'</div><div class="u-name">'+s.name+
      (cur>0?' <small>(Lv.'+cur+'→'+(cur+1)+')</small>':'')+'</div>'+
      '<div class="u-desc">'+s.desc+'</div><div class="u-tag">'+(s.type==='active'?'主动':'被动')+'</div>';
    div.addEventListener('click', ()=>{ gainSkill(sid); $('upgModal').classList.remove('show'); gamePaused=false; updateExpUI(); renderSkillsBar(); });
    cards.appendChild(div);
  });
}
