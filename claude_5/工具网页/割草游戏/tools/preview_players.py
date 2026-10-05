# -*- coding: utf-8 -*-
"""preview_players.py —— 预览玩家各衣服ID的站立正面帧"""
import os, sys, glob
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from extract_mir import extract

PL_DIR = r"E:\Game\传奇端游\MirServer\996M2_release\DEV\anim\player"
OUT = os.path.join(os.path.dirname(__file__), '..', '_mir_test')
IDS = [1250,1251,1252,1253,1254,1255,1256,1257,1258,1259,
       30501,30502,30503,30504,30505,30506,30507,30508,
       41000,41001,41002,41003,80001,80002,80003,80004]

def build():
    os.makedirs(OUT, exist_ok=True)
    cell, cols = 170, 9
    rows = (len(IDS)+cols-1)//cols
    sheet = Image.new('RGBA', (cols*cell, rows*(cell+16)), (40,44,52,255))
    draw = ImageDraw.Draw(sheet)
    for i, pid in enumerate(IDS):
        pl = os.path.join(PL_DIR, f'player_{pid}_0_0_0.plist')
        if not os.path.exists(pl):
            print(f'no plist player_{pid}_0_0_0'); continue
        tmp = os.path.join(OUT, f'_pl_{pid}')
        try:
            extract(pl, tmp, frame_filter='_0_0000', first_frame_only=True)
        except Exception as e:
            print(f'skip {pid}: {e}'); continue
        imgs = glob.glob(os.path.join(tmp, '*.png'))
        if not imgs: continue
        im = Image.open(imgs[0])
        im.thumbnail((cell-10, cell-10))
        cx, cy = (i%cols)*cell, (i//cols)*(cell+16)
        sheet.paste(im, (cx+(cell-im.width)//2, cy+(cell-im.height)//2), im)
        draw.text((cx+6, cy+cell), str(pid), fill=(255,220,120,255))
        for f in glob.glob(os.path.join(tmp,'*.png')): os.remove(f)
        os.rmdir(tmp)
    sheet.save(os.path.join(OUT, 'players.png'))
    print('saved players.png')

if __name__ == '__main__':
    build()
