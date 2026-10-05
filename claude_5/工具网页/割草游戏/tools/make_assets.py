# -*- coding: utf-8 -*-
"""
make_assets.py —— 从传奇 996M2 客户端批量提取游戏所需资源
输出：assets/mir/*.png + assets/mir_data.js（base64 内联，供 file:// 直载）
映射表：
  怪物 mon_{key}: slime=10146 ghost=10101 runner=10215 brute=10113 boss=10137 final=10162
  角色 char_{role}: warrior=1253 mage=1254 ranger=1256 priest=1258 berserk=1257 scholar=1251
  地面 ground_{biome}: grass/desert=tiles200, mountain=tiles48, river=tiles237
  物件 obst_{kind}: 取自 obj200 各编号
"""
import os, sys, glob, re, base64, shutil, json
sys.path.insert(0, os.path.dirname(__file__))
from extract_mir import extract
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..')
DEV = r"E:\Game\传奇端游\MirServer\996M2_release\DEV"
OUT = os.path.join(ROOT, 'assets', 'mir')
TMP = os.path.join(ROOT, '_mir_test', '_batch')

MON = { 'slime':10146, 'ghost':10101, 'runner':10215, 'brute':10113, 'boss':10137, 'final':10162 }
CHAR = { 'warrior':1253, 'mage':1254, 'ranger':1256, 'priest':1258, 'berserk':1257, 'scholar':1251 }
GROUND = { 'grass':('tiles200',0,0), 'desert':('tiles200',0,3), 'mountain':('tiles48',0,0), 'river':('tiles237',0,2) }
# 物件：游戏障碍类型 -> (obj组, 编号)
OBST = { 'tree':('obj200',6), 'pine':('obj200',26), 'rock':('obj200',15), 'cactus':('obj200',28),
         'mrock':('obj200',16), 'fence':('obj200',38), 'barrel':('obj200',9), 'crate':('obj200',3),
         'fountain':('obj200',37), 'tower':('obj200',2) }

def pick_frame(tmp, want=0):
    """取提取目录中第 want 张（按帧序号排序）"""
    fs = glob.glob(os.path.join(tmp, '*.png'))
    fs.sort()
    if not fs:
        raise RuntimeError('no frames extracted')
    return fs[min(want, len(fs)-1)]

def grab(plist, out_name, frame_filter=None, want=0, scale_to=None):
    """提取图集中指定帧，可选缩放到高度 scale_to"""
    shutil.rmtree(TMP, ignore_errors=True)
    extract(plist, TMP, frame_filter=frame_filter)
    src = pick_frame(TMP, want)
    im = Image.open(src)
    if scale_to and im.height > scale_to:
        w = round(im.width * scale_to / im.height)
        im = im.resize((w, scale_to), Image.LANCZOS)
    im.save(os.path.join(OUT, out_name))
    shutil.rmtree(TMP, ignore_errors=True)

def do_monsters():
    for key, mid in MON.items():
        mon_dir = os.path.join(DEV, 'anim', 'monster')
        a0 = os.path.join(mon_dir, f'monster_{mid}_0_0.plist')   # 站立
        a4 = os.path.join(mon_dir, f'monster_{mid}_0_4.plist')   # 攻击
        grab(a0, f'mon_{key}_face.png', frame_filter='_4_0000.png')  # 方向4=正面
        grab(a0, f'mon_{key}_back.png', frame_filter='_0_0000.png')  # 方向0=背面
        if os.path.exists(a4):
            grab(a4, f'mon_{key}_atk.png', frame_filter='_4_', want=0)
        else:
            shutil.copyfile(os.path.join(OUT, f'mon_{key}_face.png'), os.path.join(OUT, f'mon_{key}_atk.png'))
        print(f'monster {key}({mid}) ok')

def do_chars():
    pl_dir = os.path.join(DEV, 'anim', 'player')
    for role, pid in CHAR.items():
        # 帧：face=d4站0 back=d0站0 left=d2 right=d6 atk=动作4 d4 帧1
        for name, (act, d, want) in {
            'face':(0,4,0), 'back':(0,0,0), 'left':(0,2,0), 'right':(0,6,0), 'atk':(4,4,1)
        }.items():
            pl = os.path.join(pl_dir, f'player_{pid}_0_{act}_{d}.plist')
            if not os.path.exists(pl):
                pl = os.path.join(pl_dir, f'player_{pid}_0_{act}_0.plist')  # 方向fallback
            grab(pl, f'char_{role}_{name}.png', frame_filter='_0000.png' if act==0 else None,
                 want=0 if act==0 else want, scale_to=220)
        print(f'char {role}({pid}) ok')

def do_ground():
    tiles = os.path.join(DEV, 'scene', 'tiles')
    for biome, (grp, part, idx) in GROUND.items():
        pl = os.path.join(tiles, f'{grp}_{part}.plist')
        shutil.rmtree(TMP, ignore_errors=True)
        extract(pl, TMP, frame_filter=f'_{idx:06d}.png')
        src = pick_frame(TMP)
        Image.open(src).save(os.path.join(OUT, f'ground_{biome}.png'))
        shutil.rmtree(TMP, ignore_errors=True)
        print(f'ground {biome} ok')

def do_obsts():
    obj_dir = os.path.join(DEV, 'scene', 'objects')
    for kind, (grp, num) in OBST.items():
        pl = os.path.join(obj_dir, f'{grp}_{num}.plist')
        grab(pl, f'obst_{kind}.png')
        print(f'obst {kind} ok')

def emit_js():
    """生成 mir_data.js：按游戏原贴图常量名输出（ALL_TEX/MON_TEX/OBST_TEX/TREE_TEX/SKILL_TEX）
    游戏侧零改动兼容；SKILL_TEX 取自原 assets/skill_*.png 转 base64"""
    def b64(p):
        with open(p, 'rb') as f:
            return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
    def rel(name):
        return b64(os.path.join(OUT, name))
    all_tex = { role: { k: rel(f'char_{role}_{k}.png') for k in ['face','back','left','right','atk'] }
                for role in CHAR }
    mon_tex = { key: { k: rel(f'mon_{key}_{k}.png') for k in ['face','back'] }
                for key in MON }
    obst_tex = {
        'rockpile': rel('obst_rock.png'), 'fountain': rel('obst_fountain.png'),
        'barrel': rel('obst_barrel.png'), 'crate': rel('obst_crate.png'),
        'fence': rel('obst_fence.png'), 'tower': rel('obst_tower.png'),
        'mrock': rel('obst_mrock.png'), 'cactus': rel('obst_cactus.png'),
    }
    tree_tex = { 'leaf': rel('obst_tree.png'), 'pine': rel('obst_pine.png') }
    skill_tex = {}
    for k in ['fireball','frostnova','lightning','blade','holy','vine']:
        p = os.path.join(ROOT, 'assets', f'skill_{k}.png')
        if os.path.exists(p):
            # 技能原图 2048² 太大，压缩到 256² 再内联
            im = Image.open(p).convert('RGBA')
            im = im.resize((256, 256), Image.LANCZOS)
            import io
            buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
            skill_tex[k] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
        else:
            skill_tex[k] = rel('obst_rock.png')
    ground_tex = { biome: rel(f'ground_{biome}.png') for biome in GROUND }
    lines = ['/* mir_data.js —— 传奇素材（自动生成 by tools/make_assets.py）*/']
    for gname, gdata in [('ALL_TEX',all_tex), ('MON_TEX',mon_tex), ('OBST_TEX',obst_tex),
                         ('TREE_TEX',tree_tex), ('SKILL_TEX',skill_tex), ('MIR_GROUND_TEX',ground_tex)]:
        lines.append(f'const {gname} = ' + json.dumps(gdata, ensure_ascii=False) + ';')
    with open(os.path.join(ROOT, 'assets', 'mir_data.js'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    size = os.path.getsize(os.path.join(ROOT, 'assets', 'mir_data.js'))
    print(f'mir_data.js emitted: {size/1048576:.1f} MB')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    do_monsters()
    do_chars()
    do_ground()
    do_obsts()
    emit_js()
    print('ALL DONE')
