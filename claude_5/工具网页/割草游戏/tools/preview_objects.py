# -*- coding: utf-8 -*-
"""preview_objects.py —— 预览场景物件图集（树/石/建筑等）"""
import os, sys, glob, re
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from extract_mir import extract

OBJ_DIR = r"E:\Game\传奇端游\MirServer\996M2_release\DEV\scene\objects"
OUT = os.path.join(os.path.dirname(__file__), '..', '_mir_test')

def build(prefix='obj12', count=40, cols=10):
    """提取每组物件第一帧预览"""
    plists = glob.glob(os.path.join(OBJ_DIR, f'{prefix}_*.plist'))
    plists = sorted(plists, key=lambda p: int(re.search(rf'{prefix}_(\d+)\.plist', p).group(1)))[:count]
    os.makedirs(OUT, exist_ok=True)
    cell = 150
    rows = (len(plists)+cols-1)//cols
    sheet = Image.new('RGBA', (cols*(cell+4), rows*(cell+16)), (40,44,52,255))
    draw = ImageDraw.Draw(sheet)
    for i, pl in enumerate(plists):
        tag = re.search(rf'{prefix}_(\d+)\.plist', pl).group(1)
        tmp = os.path.join(OUT, f'_obj_{prefix}_{tag}')
        try:
            extract(pl, tmp, max_frames=1)
        except Exception as e:
            print('skip', pl, e); continue
        imgs = glob.glob(os.path.join(tmp, '*.png'))
        if imgs:
            im = Image.open(imgs[0])
            im.thumbnail((cell-8, cell-8))
            cx, cy = (i%cols)*(cell+4), (i//cols)*(cell+16)
            sheet.paste(im, (cx+(cell-im.width)//2, cy+(cell-im.height)//2), im)
            draw.text((cx+4, cy+cell), f'{prefix}_{tag}', fill=(255,220,120,255))
        for f in glob.glob(os.path.join(tmp,'*.png')): os.remove(f)
        os.rmdir(tmp)
    sheet.save(os.path.join(OUT, f'{prefix}_objects.png'))
    print(f'saved {prefix}_objects.png: {len(plists)} groups')

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv)>1 else 'obj12')
