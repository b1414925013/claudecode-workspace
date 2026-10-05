# -*- coding: utf-8 -*-
"""
contact_sheet.py —— 批量提取怪物/玩家站立帧并拼接对比图（带ID标注）
用于目视挑选传奇素材
"""
import os, re, sys, glob
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from extract_mir import extract

MON_DIR = r"E:\Game\传奇端游\MirServer\996M2_release\DEV\anim\monster"
OUT = os.path.join(os.path.dirname(__file__), '..', '_mir_test')

def build_monster_sheet():
    """提取每个怪物的站立帧(方向0第0帧)，拼成网格对比图"""
    plists = sorted(glob.glob(os.path.join(MON_DIR, '*_0_0.plist')),
                    key=lambda p: int(re.search(r'monster_(\d+)_', p).group(1)))
    os.makedirs(OUT, exist_ok=True)
    cell, cols = 130, 12
    rows = (len(plists) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols*cell, rows*(cell+16)), (40, 44, 52, 255))
    draw = ImageDraw.Draw(sheet)
    for i, pl in enumerate(plists):
        mid = re.search(r'monster_(\d+)_', pl).group(1)
        tmp = os.path.join(OUT, f'_tmp_{mid}')
        try:
            extract(pl, tmp, frame_filter='_0_0000', first_frame_only=True)
        except Exception as e:
            print(f'skip {mid}: {e}')
            continue
        imgs = glob.glob(os.path.join(tmp, '*.png'))
        if not imgs:
            continue
        im = Image.open(imgs[0])
        im.thumbnail((cell-8, cell-8))
        cx, cy = (i % cols)*cell, (i // cols)*(cell+16)
        sheet.paste(im, (cx + (cell-im.width)//2, cy + (cell-im.height)//2), im)
        draw.text((cx+4, cy+cell-2), mid, fill=(255, 220, 120, 255))
        for f in glob.glob(os.path.join(tmp, '*.png')):
            os.remove(f)
        os.rmdir(tmp)
    sheet.save(os.path.join(OUT, 'monster_sheet.png'))
    print(f'sheet saved: {len(plists)} monsters')

if __name__ == '__main__':
    build_monster_sheet()
