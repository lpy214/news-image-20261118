"""Draw one image summing up the world news of Wednesday 18 November 2026.

Pure Python 3.13 standard library, no network, no files read: the picture
is drawn pixel by pixel from the stories listed in STORIES, so two runs
write exactly the same bytes. Run: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

CREAM = (247, 243, 232)
NAVY = (20, 33, 61)
WHITE = (255, 255, 255)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
TEAL = (0, 128, 128)
DARK = (30, 30, 30)
GREY = (90, 90, 90)

STORIES = [
    ("US-IRAN CLASH", RED,
     "US jets hit Qeshm Island. Iran drones hit "
     "a US radar base in Bahrain."),
    ("TRUMP IN MANILA", NAVY,
     "Trump meets Marcos in Manila. Next: "
     "China talks with Xi, Putin."),
    ("UKRAINE BRIDGE", TEAL,
     "Ukraine hits the Crimea bridge again. "
     "Russia strikes bridges in Kyiv."),
    ("NVIDIA BEATS", (90, 60, 140),
     "Nvidia beats estimates in its first "
     "report since Huang left."),
    ("MEASLES STATUS", (140, 90, 0),
     "The US loses its measles-free status "
     "as cases spread."),
    ("CYCLONE AKVAN", (0, 90, 140),
     "Cyclone Akvan heads for India's Andhra "
     "coast. Landfall due 20 Nov."),
]

# 5x7 bitmap font: each glyph is 7 rows of 5 bits, top to bottom.
FONT = {
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F],
    "3": [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    " ": [0, 0, 0, 0, 0, 0, 0],
    "-": [0, 0, 0, 0x1F, 0, 0, 0],
    ".": [0, 0, 0, 0, 0, 0x0C, 0x0C],
    ",": [0, 0, 0, 0, 0x0C, 0x04, 0x08],
    "'": [0x04, 0x04, 0x08, 0, 0, 0, 0],
    ":": [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0],
    "/": [0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10],
    "&": [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    "(": [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ")": [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04],
    "%": [0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13],
}


class Canvas:
    """An RGB pixel buffer with simple filled-shape and text drawing."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set_pixel(xx, yy, colour)

    def draw_line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_pixel(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set_pixel(xx, yy, colour)

    def circle_outline(self, cx, cy, r, colour, thick=3):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= thick / 2:
                    self.set_pixel(xx, yy, colour)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, colour):
        cx = x
        for ch in text.upper():
            rows = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = rows[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, colour)
            cx += 6 * scale
        return cx

    def draw_text_centred(self, cx, y, text, scale, colour):
        x = cx - self.text_width(text, scale) // 2
        self.draw_text(x, y, text, scale, colour)

    def wrap(self, text, max_chars):
        words = text.split(" ")
        lines = []
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if len(trial) <= max_chars:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines


def draw_panel(canvas, title, colour, body, x, y, w, h):
    canvas.fill_rect(x, y, w, h, WHITE)
    canvas.fill_rect(x, y, w, 10, colour)
    canvas.fill_rect(x + 24, y + 28, 14, 14, colour)
    canvas.draw_text(x + 46, y + 22, title, 5, colour)
    lines = canvas.wrap(body, 20)
    yy = y + 88
    for line in lines[:4]:
        canvas.draw_text(x + 24, yy, line, 4, DARK)
        yy += 38
    canvas.fill_rect(x, y + h - 2, w, 2, (220, 220, 220))


def png_bytes(canvas):
    raw = bytearray()
    for yy in range(canvas.height):
        raw.append(0)
        start = yy * canvas.width * 3
        raw += canvas.pixels[start:start + canvas.width * 3]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    header = struct.pack(">IIBBBBB", canvas.width, canvas.height,
                         8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", header)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    return data


def main():
    canvas = Canvas(WIDTH, HEIGHT, CREAM)
    canvas.fill_rect(0, 0, WIDTH, 150, NAVY)
    canvas.draw_text_centred(WIDTH // 2, 22, "WORLD NEWS", 8, WHITE)
    canvas.draw_text_centred(WIDTH // 2, 100, "WEDNESDAY 18 NOVEMBER 2026",
                             5, GOLD)
    canvas.fill_rect(0, 150, WIDTH, 6, GOLD)
    canvas.draw_text_centred(WIDTH // 2, 168, "SIX STORIES FROM ONE DAY",
                             4, GREY)
    top = 204
    panel_w = 496
    panel_h = 240
    gap = 12
    for i, (title, colour, body) in enumerate(STORIES):
        px = 8 + (i % 2) * (panel_w + gap)
        py = top + (i // 2) * (panel_h + gap)
        draw_panel(canvas, title, colour, body, px, py, panel_w, panel_h)
    canvas.fill_rect(0, 948, WIDTH, 76, NAVY)
    canvas.draw_text_centred(WIDTH // 2, 972,
                             "18 NOV 2026 - THE DAY IN SIX PICTURES",
                             4, WHITE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(canvas))


if __name__ == "__main__":
    main()
