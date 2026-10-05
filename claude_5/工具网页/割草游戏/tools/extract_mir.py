# -*- coding: utf-8 -*-
"""
mir_extract.py —— 从传奇 996M2 客户端 cocos2d 图集中提取单帧 PNG
图集格式：XML plist（frames dict）+ 同名 PNG
帧属性：frame={{x,y},{w,h}}, offset={ox,oy}, rotated, sourceSize={w,h}
用法：
  python mir_extract.py <plist路径> <输出目录> [--max N] [--frame 关键字]
"""
import sys, os, re, plistlib
from PIL import Image

def parse_rect(s):
    """解析 '{{x,y},{w,h}}' 或 '{x,y}' 字符串为元组"""
    nums = [int(v) for v in re.findall(r'-?\d+', s)]
    return nums

def extract(plist_path, out_dir, max_frames=0, frame_filter=None, first_frame_only=False):
    """解析 plist 图集并裁剪输出所有帧；返回成功提取的帧数"""
    with open(plist_path, 'rb') as f:
        pl = plistlib.load(f)
    meta = pl.get('metadata', {})
    tex_path = os.path.splitext(plist_path)[0] + '.png'
    if not os.path.exists(tex_path):
        # metadata.textureFilename 可能指向真实图集名
        tex_name = meta.get('textureFilename', '')
        tex_path = os.path.join(os.path.dirname(plist_path), tex_name)
    atlas = Image.open(tex_path).convert('RGBA')
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(plist_path))[0]
    count = 0
    for name, fr in pl['frames'].items():
        if frame_filter and frame_filter not in name:
            continue
        nums = parse_rect(fr['frame'])          # [x, y, w, h]
        x, y, w, h = nums
        # format2 + rotated：frame 尺寸为逻辑宽高，图集内实际占位为 h×w，内容顺时针旋转90°存储
        rotated = fr.get('rotated') in (True, 'true', 1)
        if rotated:
            region = atlas.crop((x, y, x + h, y + w)).rotate(90, expand=True)
        else:
            region = atlas.crop((x, y, x + w, y + h))
        src_w, src_h = parse_rect(fr['sourceSize'])
        # 该引擎导出的 sourceColorRect 恒为全尺寸（未 trim），region 即完整帧；
        # offset 字段语义非标准中心偏移，直接使用 region 避免拼合错位
        if region.width == src_w and region.height == src_h:
            canvas = region
        else:
            canvas = Image.new('RGBA', (src_w, src_h), (0, 0, 0, 0))
            canvas.paste(region, ((src_w-region.width)//2, (src_h-region.height)//2))
        out_name = f"{base}_{os.path.splitext(name)[0]}.png" if not first_frame_only else f"{base}.png"
        canvas.save(os.path.join(out_dir, out_name))
        count += 1
        if first_frame_only:
            break
        if max_frames and count >= max_frames:
            break
    return count

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    opts = {a.split('=')[0].lstrip('-'): a.split('=')[1] for a in sys.argv[1:] if a.startswith('--') and '=' in a}
    plist = args[0]
    out = args[1] if len(args) > 1 else 'extracted'
    n = extract(plist, out,
                max_frames=int(opts.get('max', 0)),
                frame_filter=opts.get('frame'))
    print(f"extracted {n} frames -> {out}")
