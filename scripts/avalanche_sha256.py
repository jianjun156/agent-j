#!/usr/bin/env python3
"""
EXP-20260402-016 AVALANCHE-CASCADE
SHA-256 雪崩效应可视化：翻转输入消息的每一个比特，
观察输出 256 位哈希中有多少位发生改变。
理论值 ~50%（128 位），实际结果？

生成一张 PNG 热力图：
- X 轴 = 输入消息的每个比特位（被翻转的位置）
- Y 轴 = 输出哈希的每个比特位（0-255）
- 颜色 = 该输出位是否翻转（翻转=亮色，未翻转=暗色）
- 右侧汇总每行翻转次数，底部汇总每列翻转次数

纯 Python + hashlib，手写 PNG 编码器，零 pip 依赖。
"""

import hashlib
import struct
import zlib
import math

# === 参数 ===
MESSAGE = b"Agent J is watching."  # 20 bytes = 160 bits
INPUT_BITS = len(MESSAGE) * 8       # 160
OUTPUT_BITS = 256                    # SHA-256

# === 计算原始哈希 ===
original_hash = hashlib.sha256(MESSAGE).digest()
original_bits = []
for byte in original_hash:
    for bit_pos in range(7, -1, -1):
        original_bits.append((byte >> bit_pos) & 1)

# === 雪崩矩阵：翻转每个输入比特，记录输出变化 ===
# matrix[input_bit][output_bit] = 1 if flipped, 0 if same
matrix = []
flip_counts_per_input = []  # 每个输入比特翻转后，输出变化了多少位

for i in range(INPUT_BITS):
    # 翻转第 i 位
    byte_idx = i // 8
    bit_idx = 7 - (i % 8)
    mutated = bytearray(MESSAGE)
    mutated[byte_idx] ^= (1 << bit_idx)
    
    # 计算新哈希
    new_hash = hashlib.sha256(bytes(mutated)).digest()
    new_bits = []
    for byte in new_hash:
        for bit_pos in range(7, -1, -1):
            new_bits.append((byte >> bit_pos) & 1)
    
    # 比较差异
    row = []
    flips = 0
    for j in range(OUTPUT_BITS):
        diff = original_bits[j] ^ new_bits[j]
        row.append(diff)
        flips += diff
    matrix.append(row)
    flip_counts_per_input.append(flips)

# 每个输出比特在所有输入翻转中被改变的次数
flip_counts_per_output = []
for j in range(OUTPUT_BITS):
    count = sum(matrix[i][j] for i in range(INPUT_BITS))
    flip_counts_per_output.append(count)

# === 统计 ===
avg_flips = sum(flip_counts_per_input) / INPUT_BITS
min_flips = min(flip_counts_per_input)
max_flips = max(flip_counts_per_input)
total_cells = INPUT_BITS * OUTPUT_BITS
total_flips = sum(flip_counts_per_input)
flip_ratio = total_flips / total_cells * 100

print(f"消息: {MESSAGE.decode()}")
print(f"输入比特数: {INPUT_BITS}")
print(f"输出比特数: {OUTPUT_BITS}")
print(f"平均翻转位数: {avg_flips:.1f} / {OUTPUT_BITS} ({avg_flips/OUTPUT_BITS*100:.1f}%)")
print(f"最少翻转: {min_flips}, 最多翻转: {max_flips}")
print(f"全局翻转率: {flip_ratio:.2f}%")

# === PNG 渲染 ===
CELL_SIZE = 4          # 每个矩阵单元的像素大小
MARGIN_LEFT = 60       # 左边距（标签）
MARGIN_TOP = 80        # 上边距（标题）
MARGIN_RIGHT = 120     # 右边距（行统计条形图）
MARGIN_BOTTOM = 130    # 下边距（列统计条形图）
BAR_MAX = 50           # 条形图最大长度（像素）

GRID_W = INPUT_BITS * CELL_SIZE
GRID_H = OUTPUT_BITS * CELL_SIZE

IMG_W = MARGIN_LEFT + GRID_W + MARGIN_RIGHT
IMG_H = MARGIN_TOP + GRID_H + MARGIN_BOTTOM

# 画布
pixels = [[(8, 12, 20)] * IMG_W for _ in range(IMG_H)]

def set_pixel(x, y, color):
    if 0 <= x < IMG_W and 0 <= y < IMG_H:
        pixels[y][x] = color

def blend_pixel(x, y, color, alpha):
    if 0 <= x < IMG_W and 0 <= y < IMG_H:
        bg = pixels[y][x]
        r = int(bg[0] * (1 - alpha) + color[0] * alpha)
        g = int(bg[1] * (1 - alpha) + color[1] * alpha)
        b = int(bg[2] * (1 - alpha) + color[2] * alpha)
        pixels[y][x] = (min(255, r), min(255, g), min(255, b))

def draw_rect(x, y, w, h, color):
    for dy in range(h):
        for dx in range(w):
            set_pixel(x + dx, y + dy, color)

# === 热力图颜色 ===
# 翻转 = 亮青/蓝, 未翻转 = 深暗色
COLOR_FLIP = (0, 200, 255)      # 亮青
COLOR_NO_FLIP = (15, 20, 30)    # 几乎黑

# 渲染雪崩矩阵
for i in range(INPUT_BITS):
    for j in range(OUTPUT_BITS):
        x = MARGIN_LEFT + i * CELL_SIZE
        y = MARGIN_TOP + j * CELL_SIZE
        if matrix[i][j]:
            # 翻转 - 用渐变色，按输入位置着色
            hue = i / INPUT_BITS
            # 从青色到品红的渐变
            if hue < 0.5:
                r = int(0 + hue * 2 * 100)
                g = int(200 - hue * 2 * 100)
                b = 255
            else:
                r = int(100 + (hue - 0.5) * 2 * 155)
                g = int(100 - (hue - 0.5) * 2 * 100)
                b = int(255 - (hue - 0.5) * 2 * 55)
            color = (r, g, b)
            draw_rect(x, y, CELL_SIZE, CELL_SIZE, color)
        else:
            draw_rect(x, y, CELL_SIZE, CELL_SIZE, COLOR_NO_FLIP)

# === 网格线（每 8 比特 = 1 字节分隔）===
# 竖线 - 输入字节分隔
for byte_i in range(len(MESSAGE) + 1):
    x = MARGIN_LEFT + byte_i * 8 * CELL_SIZE
    for y in range(MARGIN_TOP, MARGIN_TOP + GRID_H):
        blend_pixel(x, y, (100, 150, 200), 0.3)

# 横线 - 输出字节分隔（每 32 字节 = 每 8 位一组）
for byte_j in range(OUTPUT_BITS // 8 + 1):
    y = MARGIN_TOP + byte_j * 8 * CELL_SIZE
    for x in range(MARGIN_LEFT, MARGIN_LEFT + GRID_W):
        blend_pixel(x, y, (100, 150, 200), 0.3)

# === 右侧条形图：每行（输出比特）被翻转的次数 ===
max_per_output = max(flip_counts_per_output) if flip_counts_per_output else 1
bar_start_x = MARGIN_LEFT + GRID_W + 10

for j in range(OUTPUT_BITS):
    count = flip_counts_per_output[j]
    bar_len = int(count / max_per_output * BAR_MAX)
    y_center = MARGIN_TOP + j * CELL_SIZE + CELL_SIZE // 2
    ratio = count / INPUT_BITS
    # 颜色：接近 50% 为绿色，偏离为黄/红
    deviation = abs(ratio - 0.5) * 2  # 0~1
    r = int(deviation * 255)
    g = int((1 - deviation) * 200)
    b = 50
    for dx in range(bar_len):
        for dy in range(max(1, CELL_SIZE - 1)):
            set_pixel(bar_start_x + dx, y_center - CELL_SIZE // 2 + dy, (r, g, b))

# === 底部条形图：每列（输入比特）翻转的输出位数 ===
bar_start_y = MARGIN_TOP + GRID_H + 10

for i in range(INPUT_BITS):
    count = flip_counts_per_input[i]
    bar_len = int(count / OUTPUT_BITS * BAR_MAX * 2)  # 放大一些
    x_center = MARGIN_LEFT + i * CELL_SIZE + CELL_SIZE // 2
    ratio = count / OUTPUT_BITS
    deviation = abs(ratio - 0.5) * 2
    r = int(deviation * 255)
    g = int((1 - deviation) * 200)
    b = 50
    for dy in range(bar_len):
        for dx in range(max(1, CELL_SIZE - 1)):
            set_pixel(x_center - CELL_SIZE // 2 + dx, bar_start_y + dy, (r, g, b))

# === 简单文字标注（用点阵小字体）===
# 简化：不画文字，用色块标注关键统计数据

# 顶部标题区域 - 用彩色条表示
# 画一条渐变色的分隔线
for x in range(MARGIN_LEFT, MARGIN_LEFT + GRID_W):
    hue = (x - MARGIN_LEFT) / GRID_W
    if hue < 0.5:
        r = int(hue * 2 * 100)
        g = int(200 - hue * 2 * 100)
        b = 255
    else:
        r = int(100 + (hue - 0.5) * 2 * 155)
        g = int(100 - (hue - 0.5) * 2 * 100)
        b = int(255 - (hue - 0.5) * 2 * 55)
    set_pixel(x, MARGIN_TOP - 2, (r, g, b))
    set_pixel(x, MARGIN_TOP - 1, (r, g, b))

# 左侧色标
for y in range(MARGIN_TOP, MARGIN_TOP + GRID_H):
    progress = (y - MARGIN_TOP) / GRID_H
    v = int(40 + progress * 60)
    set_pixel(MARGIN_LEFT - 2, y, (v, v, v + 30))
    set_pixel(MARGIN_LEFT - 1, y, (v, v, v + 30))

# === 50% 参考线（在底部条形图上标注理想翻转率位置）===
ideal_bar_len = int(0.5 * BAR_MAX * 2)
for i in range(INPUT_BITS):
    x_center = MARGIN_LEFT + i * CELL_SIZE + CELL_SIZE // 2
    set_pixel(x_center, bar_start_y + ideal_bar_len, (255, 215, 0))
    if CELL_SIZE > 2:
        set_pixel(x_center - 1, bar_start_y + ideal_bar_len, (255, 215, 0))

# 右侧条形图的 50% 参考线
ideal_right = int(0.5 * BAR_MAX)
for j in range(OUTPUT_BITS):
    y_center = MARGIN_TOP + j * CELL_SIZE + CELL_SIZE // 2
    set_pixel(bar_start_x + ideal_right, y_center, (255, 215, 0))

# === 小字体渲染器 ===
FONT_3x5 = {
    '0': ['111','101','101','101','111'],
    '1': ['010','110','010','010','111'],
    '2': ['111','001','111','100','111'],
    '3': ['111','001','111','001','111'],
    '4': ['101','101','111','001','001'],
    '5': ['111','100','111','001','111'],
    '6': ['111','100','111','101','111'],
    '7': ['111','001','010','010','010'],
    '8': ['111','101','111','101','111'],
    '9': ['111','101','111','001','111'],
    '.': ['000','000','000','000','010'],
    '%': ['101','001','010','100','101'],
    '/': ['001','001','010','100','100'],
    ':': ['000','010','000','010','000'],
    '-': ['000','000','111','000','000'],
    ' ': ['000','000','000','000','000'],
    'A': ['010','101','111','101','101'],
    'B': ['110','101','110','101','110'],
    'C': ['011','100','100','100','011'],
    'D': ['110','101','101','101','110'],
    'E': ['111','100','110','100','111'],
    'F': ['111','100','110','100','100'],
    'G': ['011','100','101','101','011'],
    'H': ['101','101','111','101','101'],
    'I': ['111','010','010','010','111'],
    'J': ['111','010','010','010','100'],
    'K': ['101','101','110','101','101'],
    'L': ['100','100','100','100','111'],
    'M': ['101','111','111','101','101'],
    'N': ['101','111','111','111','101'],
    'O': ['111','101','101','101','111'],
    'P': ['111','101','111','100','100'],
    'Q': ['111','101','101','111','001'],
    'R': ['111','101','111','110','101'],
    'S': ['011','100','010','001','110'],
    'T': ['111','010','010','010','010'],
    'U': ['101','101','101','101','111'],
    'V': ['101','101','101','101','010'],
    'W': ['101','101','111','111','101'],
    'X': ['101','101','010','101','101'],
    'Y': ['101','101','010','010','010'],
    'Z': ['111','001','010','100','111'],
    'a': ['000','011','101','101','011'],
    'b': ['100','110','101','101','110'],
    'c': ['000','011','100','100','011'],
    'd': ['001','011','101','101','011'],
    'e': ['011','101','111','100','011'],
    'f': ['011','100','111','100','100'],
    'g': ['011','101','011','001','110'],
    'h': ['100','110','101','101','101'],
    'i': ['010','000','010','010','010'],
    'j': ['010','000','010','010','100'],
    'k': ['100','101','110','101','101'],
    'l': ['110','010','010','010','111'],
    'm': ['000','111','111','101','101'],
    'n': ['000','110','101','101','101'],
    'o': ['000','010','101','101','010'],
    'p': ['000','110','101','110','100'],
    'r': ['000','011','100','100','100'],
    's': ['000','011','010','010','110'],
    't': ['010','111','010','010','011'],
    'u': ['000','101','101','101','011'],
    'v': ['000','101','101','010','010'],
    'w': ['000','101','111','111','010'],
    'x': ['000','101','010','010','101'],
    'y': ['000','101','011','001','110'],
    'z': ['000','111','010','100','111'],
    '(': ['010','100','100','100','010'],
    ')': ['010','001','001','001','010'],
    '=': ['000','111','000','111','000'],
    '+': ['000','010','111','010','000'],
    '"': ['101','101','000','000','000'],
    "'": ['010','010','000','000','000'],
    ',': ['000','000','000','010','100'],
    '_': ['000','000','000','000','111'],
    '[': ['110','100','100','100','110'],
    ']': ['011','001','001','001','011'],
}

def draw_text(text, x, y, color, scale=1):
    """绘制 3x5 点阵文字"""
    cursor_x = x
    for ch in text.upper():
        glyph = FONT_3x5.get(ch)
        if glyph is None:
            cursor_x += 4 * scale
            continue
        for row_idx, row in enumerate(glyph):
            for col_idx, bit in enumerate(row):
                if bit == '1':
                    for sy in range(scale):
                        for sx in range(scale):
                            set_pixel(cursor_x + col_idx * scale + sx,
                                     y + row_idx * scale + sy, color)
        cursor_x += (len(glyph[0]) + 1) * scale

# === 绘制标题和标注 ===
# 标题
draw_text("SHA-256 AVALANCHE EFFECT", MARGIN_LEFT, 8, (0, 200, 255), 3)
draw_text(f'"AGENT J IS WATCHING."', MARGIN_LEFT, 35, (180, 180, 200), 2)
draw_text(f"FLIP RATE: {flip_ratio:.1f}%  AVG: {avg_flips:.0f}/256  RANGE: {min_flips}-{max_flips}",
          MARGIN_LEFT, 55, (0, 255, 150), 2)

# X轴标注
draw_text("INPUT BIT POSITION (0-159)", MARGIN_LEFT + GRID_W // 4,
          MARGIN_TOP + GRID_H + BAR_MAX * 2 + 20, (150, 150, 180), 1)

# Y轴标注（竖向太难，改为左上角）
draw_text("OUTPUT", 5, MARGIN_TOP + 10, (150, 150, 180), 1)
draw_text("BIT", 5, MARGIN_TOP + 20, (150, 150, 180), 1)
draw_text("0-255", 5, MARGIN_TOP + 30, (150, 150, 180), 1)

# 右侧标注
draw_text("FLIPS", bar_start_x, MARGIN_TOP - 12, (150, 150, 180), 1)
draw_text("PER ROW", bar_start_x, MARGIN_TOP - 5, (150, 150, 180), 1)

# 底部标注
draw_text("FLIPS PER COL", MARGIN_LEFT, bar_start_y - 8, (150, 150, 180), 1)

# 50% 标注
draw_text("50%", bar_start_x + ideal_right + 3,
          MARGIN_TOP + GRID_H // 2, (255, 215, 0), 1)

# === 手写 PNG 编码器 ===
def write_png(filename, width, height, pixel_data):
    """pixel_data: list of rows, each row is list of (r,g,b) tuples"""
    def make_chunk(chunk_type, data):
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + chunk + crc

    # Signature
    sig = b'\x89PNG\r\n\x1a\n'
    
    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)
    
    # IDAT
    raw = b''
    for row in pixel_data:
        raw += b'\x00'  # filter: None
        for r, g, b in row:
            raw += bytes([r, g, b])
    
    compressed = zlib.compress(raw, 9)
    idat = make_chunk(b'IDAT', compressed)
    
    # IEND
    iend = make_chunk(b'IEND', b'')
    
    with open(filename, 'wb') as f:
        f.write(sig + ihdr + idat + iend)
    
    return len(sig + ihdr + idat + iend)

# 输出
output_path = '/Users/jianjun/.openclaw/workspace/agent-j/lab/avalanche-sha256.png'
file_size = write_png(output_path, IMG_W, IMG_H, pixels)
print(f"\nPNG 已生成: {output_path}")
print(f"图片尺寸: {IMG_W}×{IMG_H}")
print(f"文件大小: {file_size / 1024:.1f} KB")
