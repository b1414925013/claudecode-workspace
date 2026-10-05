/* 12_boot.js —— 主菜单/启动 */
/* ===== 菜单 / 角色选择 ===== */
function renderMenu(){
  $('menuCoins').textContent = '累计金币：'+save.totalCoins;
  const grid = $('roleGrid');
  grid.innerHTML = '';
  ROLES.forEach(r=>{
    const unlocked = isUnlocked(r.id);
    const card = document.createElement('div');
    card.className = 'roleCard' + (unlocked?'':' locked');
    card.innerHTML = '<div class="r-top"><span class="r-ico">'+r.icon+'</span>'+
      (unlocked ? '<span class="r-state un">已解锁</span>' : '<span class="r-state lo">'+(r.price>0?r.price+' 金币解锁':'免费')+'</span>')+'</div>'+
      '<div class="r-name">'+r.name+'</div>'+
      '<div class="r-passive">被动：'+r.passive+'</div>';
    card.addEventListener('click', ()=>{
      if(unlocked){ selectedRole = r.id; $('startBtn').textContent = '开始冒险（'+r.name+'）'; }
      else {
        if(unlockRole(r.id)){ renderMenu(); floatText('解锁 '+r.name+'！','#4fae5a'); }
        else floatText('金币不足！','#ff6b6b');
      }
    });
    grid.appendChild(card);
  });
}
$('startBtn').addEventListener('click', ()=>{ startGame(selectedRole); });
$('againBtn').addEventListener('click', ()=>{ startGame(selectedRole); });
$('menuBtn').addEventListener('click', ()=>{ $('endModal').classList.remove('show'); $('menuModal').classList.add('show'); renderMenu(); });

// 初始展示主菜单
renderMenu();
$('menuModal').classList.add('show');
// 启动动画循环（首帧已渲染，循环不依赖场景就绪）
animate();