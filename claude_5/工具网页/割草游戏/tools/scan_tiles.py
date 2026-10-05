# -*- coding: utf-8 -*-
"""scan_tiles.py —— 扫描各地图组 tile 图集，挑出色彩丰富(草地类)的非黑帧预览"""
import os, sys, glob, shutil
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from extract_mir import extract

TILES = r"E:\Game\传奇端游\MirServer\996M2_release\DEV\scene\tiles"
OUT = os.path.join(os.path.dirname(__file__), '..', '_mir_test')

def scan_group(name, per_sheet=8, max_frames=260):
    """提取组内非黑帧，返回拼图；统计平均亮度"""
    plists = sorted(glob.glob(os.path.join(TILES, f'tiles{name}_*.plist')),
                    key=lambda p: int(p.rsplit('_',1)[1][:-6]))
    frames = []
    for pl in plists[:max_frames//50+2]:
        tmp = os.path.join(OUT, f'_scan_{name}')
        shutil.rmtree(tmp, ignore_errors=True)
        try:
            extract(pl, tmp)
        except Exception as e:
            print('skip', pl, e); continue
        for f in glob.glob(os.path.join(tmp, '*.png')):
            im = Image.open(f)
            # 过滤接近纯黑的帧：非透明像素平均RGB
            px = im.resize((16,16)).getdata()
            vals = [p[:3] for p in px if p[3] > 40]
            if len(vals) > 30:
                avg = tuple(sum(c[i] for c in vals)//len(vals) for i in range(3))
                if sum(avg) > 90:   # 排除暗黑洞窟类
                    frames.append((im, sum(avg)))
        shutil.rmtree(tmp, ignore_errors=True)
        if len(frames) >= per_sheet*3: break
    if not frames:
        print(f'tiles{name}: 无明亮帧'); return None
    frames.sort(key=lambda t: -t[1])
    picked = frames[:per_sheet]
    cell = max(max(i.width for i,_ in picked), max(i.height for i,_ in picked))
    sheet = Image.new('RGBA', (per_sheet*(cell+4), cell+18), (70,70,80,255))
    draw = ImageDraw.Draw(sheet)
    for i,(im,b) in enumerate(picked):
        sheet.paste(im, (i*(cell+4)+(cell-im.width)//2, (cell-im.height)), im)
        draw.text((i*(cell+4)+4, cell+2), f'{name}#{i}', fill=(255,220,120,255))
    print(f'tiles{name}: 明亮帧 {len(frames)}')
    return sheet

if __name__ == '__main__':
    groups = sys.argv[1].split(',') if len(sys.argv)>1 else ['48','199','200','210','220','237']
    sheets = []
    for g in groups:
        s = scan_group(g)
        if s: sheets.append(s)
    W = max(s.width for s in sheets); H = sum(s.height for s in sheets)
    allsheet = Image.new('RGBA', (W, H), (70,70,80,255))
    y = 0
    for s in sheets: allsheet.paste(s, (0, y)); y += s.height
    allsheet.save(os.path.join(OUT, 'tiles_groups.png'))
    print('saved tiles_groups.png')
