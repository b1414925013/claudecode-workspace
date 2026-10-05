# -*- coding: utf-8 -*-
"""preview_monsters.py —— 放大预览候选怪物（站立正面帧）"""
import os, re, sys, glob
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from extract_mir import extract

MON_DIR = r"E:\Game\传奇端游\MirServer\996M2_release\DEV\anim\monster"
OUT = os.path.join(os.path.dirname(__file__), '..', '_mir_test')

# 候选怪物ID（首轮缩略图筛出的轮廓可辨识者）
CANDIDS = [10000, 10101, 10103, 10106, 10111, 10112, 10113, 10121,
           10124, 10133, 10137, 10145, 10146, 10152, 10158, 10160,
           10162, 10163, 10170, 10175, 10181, 10186, 10191, 10195,
           10198, 10205, 10211, 10213, 10216, 10241, 10250, 10255]

def build(ids):
    os.makedirs(OUT, exist_ok=True)
    cell, cols = 200, 8
    rows = (len(ids) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols*cell, rows*(cell+18)), (40, 44, 52, 255))
    draw = ImageDraw.Draw(sheet)
    for i, mid in enumerate(ids):
        pl = os.path.join(MON_DIR, f'monster_{mid}_0_0.plist')
        if not os.path.exists(pl):
            print(f'no plist for {mid}')
            continue
        tmp = os.path.join(OUT, f'_pv_{mid}')
        try:
            # 帧名格式 monster_{id}_0_0_{dir}_0000.png，取方向0(正面)第0帧
            extract(pl, tmp, frame_filter='_0_0_0_0000', first_frame_only=True)
        except Exception as e:
            print(f'skip {mid}: {e}'); continue
        imgs = glob.glob(os.path.join(tmp, '*.png'))
        if not imgs: continue
        im = Image.open(imgs[0])
        im.thumbnail((cell-10, cell-10))
        cx, cy = (i % cols)*cell, (i // cols)*(cell+18)
        sheet.paste(im, (cx + (cell-im.width)//2, cy + (cell-im.height)//2), im)
        draw.text((cx+6, cy+cell+2), str(mid), fill=(255, 220, 120, 255))
        for f in glob.glob(os.path.join(tmp, '*.png')): os.remove(f)
        os.rmdir(tmp)
    sheet.save(os.path.join(OUT, 'preview_big.png'))
    print('saved preview_big.png')

if __name__ == '__main__':
    build(CANDIDS)
