/* 11_main.js —— 主循环/结算/动画 */
/* ===== 主循环 ===== */
let gamePaused = true; // 菜单/升级时暂停
let elapsed = 0;       // 对局累计秒
let clock = new THREE.Clock();
let gameActive = false;

function startGame(roleId){
  // 清场
  while(monsters.length) removeMonsterMesh(monsters[0]);
  drops.forEach(d=>scene.remove(d.mesh)); drops.length=0;
  projectiles.forEach(p=>scene.remove(p.mesh)); projectiles.length=0;
  effects.forEach(e=>scene.remove(e.mesh)); effects.length=0;
  effectZones.length=0;
  if(player && player.mesh) scene.remove(player.mesh);
  selectedRole = roleId;
  initPlayer(roleId);
  updateExpUI(); updateHp(); updateTime();
  $('menuModal').classList.remove('show');
  $('endModal').classList.remove('show');
  runTime=0; elapsed=0; spawnTimer=0; bossSpawned=0; finalSpawned=false;
  gamePaused=false; gameActive=true;
  updateChunks(0,0);
}

function endGame(won){
  gameActive=false; gamePaused=true;
  const wins = won ? '胜利' : '失败';
  $('endTitle').textContent = won ? '通关成功！' : '挑战失败…';
  $('endPanel').className = 'panel result '+(won?'resultWin':'resultLose');
  $('endSub').textContent = won ? '你击杀了祖玛教主，本局通关！' : '你的角色倒下了，本局结束。';
  $('endStats').innerHTML = '存活时间：<b>'+Math.floor(runTime/60)+'分'+Math.floor(runTime%60)+'秒</b><br/>'+
    '击杀怪物：<b>'+player.kills+'</b> 只<br/>本局金币：<b>+'+player.coins+'</b><br/>角色等级：<b>Lv.'+player.level+'</b>';
  // 结算：累加金币+记录
  const gained = won ? player.coins : player.coins;
  settleRun(selectedRole, runTime, player.kills, won, gained);
  // 更新菜单金币显示
  $('menuCoins').textContent = '累计金币：'+save.totalCoins;
  $('endModal').classList.add('show');
}

// 动画主循环
function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  if(gamePaused || !gameActive || !player){ renderer.render(scene,camera); return; }
  // 推进对局时间
  elapsed += dt; runTime += dt;
  // 更新
  updateChunks(player.pos.x, player.pos.z);
  if(player.dying){
    player.anim.deadT -= dt;
    if(player.mesh.userData && player.mesh.userData.sprite) updateSpritePlayer(dt);
    if(player.anim.deadT<=0) endGame(false);
    renderer.render(scene,camera);
    return;
  }
  movePlayer(dt);
  if(player.mesh.userData && player.mesh.userData.sprite) updateSpritePlayer(dt);
  updateAbilities(dt);
  updateSpawning(dt, elapsed);
  updateMonsters(dt);
  updateProjectiles(dt);
  updateEffects(dt);
  updateDrops(dt);
  // 相机跟随
  updateCamera(player.pos);
  // HUD
  updateExpUI(); updateTime();
  // 通关判定：终极怪被击杀
  if(finalSpawned && !monsters.some(m=>m.type.final && !m.dead)){ endGame(true); }
  renderer.render(scene,camera);
}

// 首次渲染一帧（满足首帧契约）
function firstFrame(){ renderer.render(scene,camera); }
firstFrame();