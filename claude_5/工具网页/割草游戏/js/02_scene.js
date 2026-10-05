/* 02_scene.js —— 场景/渲染器/相机/光照/resize */
/* ===== 场景与渲染器 ===== */
const gameRoot = $('game');
const scene = new THREE.Scene();
// 明亮清新天空：渐变背景
scene.background = new THREE.Color(0x9cd6f0);
scene.fog = new THREE.Fog(0x9cd6f0, 60, 160);

const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setSize(window.innerWidth, window.innerHeight);
// 像素比上限 2，移动端更低
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
gameRoot.appendChild(renderer.domElement);

// 相机：上帝俯视角（斜俯视），限位极角与距离
const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 400);
const CAM = { dist:26, height:22, angYaw:0 }; // dist=水平半径, height=相机高度
// 相机围绕玩家，yaw 可被鼠标拖动微调；极角固定，距离限位在 [18,40]
function updateCamera(playerPos){
  const dist = THREE.MathUtils.clamp(CAM.dist, 18, 40);
  const targetX = playerPos.x + Math.sin(CAM.angYaw)*dist;
  const targetZ = playerPos.z + Math.cos(CAM.angYaw)*dist;
  camera.position.set(targetX, CAM.height, targetZ);
  camera.lookAt(playerPos.x, 0, playerPos.z);
}

// 光照：主光(太阳) + 补光(暖) + 环境光(天空)，避免死平
const sun = new THREE.DirectionalLight(0xfff6d8, 1.4);
sun.position.set(30, 40, 20); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -40; sun.shadow.camera.right = 40;
sun.shadow.camera.top = 40; sun.shadow.camera.bottom = -40;
sun.shadow.camera.far = 100;
scene.add(sun);

const fill = new THREE.DirectionalLight(0xffe0b0, 0.5);
fill.position.set(-20, 25, -15); scene.add(fill);

const hemi = new THREE.HemisphereLight(0xbfe7ff, 0x6fcf6a, 0.55);
scene.add(hemi);

// resize 处理
window.addEventListener('resize', ()=>{
  camera.aspect = window.innerWidth/window.innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});