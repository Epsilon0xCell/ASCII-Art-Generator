#!/usr/bin/env python3
"""ASCII Art Generator: text banners and image-to-ASCII conversion.

Banner mode renders text in a chunky 5-row block font, handy for shell
startup files (.bashrc, .zshrc, motd):

    python3 ascii_art.py banner "HELLO"
    python3 ascii_art.py banner --double "HI"      # double-width glyphs

Image mode converts an image to ASCII art:

    python3 ascii_art.py image photo.png
    python3 ascii_art.py image photo.png --width 120 --invert

Images are read with Pillow when it is installed (PNG, JPEG, GIF, ...).
Without Pillow, Netpbm files (PGM/PPM, plain or raw) are read natively.

Library use:
    from ascii_art import banner, image_to_ascii
"""

import argparse
import sys

# 5-row block font. Each glyph is 5 strings of equal width.
FONT = {
    "A": (" ██ ", "█  █", "████", "█  █", "█  █"),
    "B": ("███ ", "█  █", "███ ", "█  █", "███ "),
    "C": (" ███", "█   ", "█   ", "█   ", " ███"),
    "D": ("███ ", "█  █", "█  █", "█  █", "███ "),
    "E": ("████", "█   ", "███ ", "█   ", "████"),
    "F": ("████", "█   ", "███ ", "█   ", "█   "),
    "G": (" ███", "█   ", "█  █", "█  █", " ███"),
    "H": ("█  █", "█  █", "████", "█  █", "█  █"),
    "I": ("███", " █ ", " █ ", " █ ", "███"),
    "J": ("████", "   █", "   █", "█  █", " ██ "),
    "K": ("█  █", "█ █ ", "██  ", "█ █ ", "█  █"),
    "L": ("█   ", "█   ", "█   ", "█   ", "████"),
    "M": ("█   █", "██ ██", "█ █ █", "█   █", "█   █"),
    "N": ("█  █", "██ █", "█ ██", "█  █", "█  █"),
    "O": (" ██ ", "█  █", "█  █", "█  █", " ██ "),
    "P": ("███ ", "█  █", "███ ", "█   ", "█   "),
    "Q": (" ██ ", "█  █", "█  █", "█ █ ", " █ █"),
    "R": ("███ ", "█  █", "███ ", "█ █ ", "█  █"),
    "S": (" ███", "█   ", " ██ ", "   █", "███ "),
    "T": ("█████", "  █  ", "  █  ", "  █  ", "  █  "),
    "U": ("█  █", "█  █", "█  █", "█  █", " ██ "),
    "V": ("█  █", "█  █", "█  █", " █ █ ", "  █  "),
    "W": ("█   █", "█   █", "█ █ █", "██ ██", "█   █"),
    "X": ("█  █", " █ █ ", "  █  ", " █ █ ", "█  █"),
    "Y": ("█  █", " █ █ ", "  █  ", "  █  ", "  █  "),
    "Z": ("████", "   █", "  █ ", " █  ", "████"),
    "0": (" ██ ", "█  █", "█  █", "█  █", " ██ "),
    "1": (" █ ", "██ ", " █ ", " █ ", "███"),
    "2": ("███ ", "█  █", "  █ ", " █  ", "████"),
    "3": ("███ ", "   █", " ██ ", "   █", "███ "),
    "4": ("█  █", "█  █", "████", "   █", "   █"),
    "5": ("████", "█   ", "███ ", "   █", "███ "),
    "6": (" ███", "█   ", "████", "█  █", " ██ "),
    "7": ("████", "   █", "  █ ", " █  ", " █  "),
    "8": (" ██ ", "█  █", " ██ ", "█  █", " ██ "),
    "9": (" ██ ", "█  █", " ███", "   █", "███ "),
    " ": ("   ", "   ", "   ", "   ", "   "),
    ".": (" ", " ", " ", " ", "█"),
    ",": ("  ", "  ", "  ", " █", "█ "),
    "!": ("█", "█", "█", " ", "█"),
    "?": ("███ ", "█  █", "  █ ", "    ", " █  "),
    "-": ("    ", "    ", "████", "    ", "    "),
    "+": ("   ", " █ ", "███", " █ ", "   "),
    "'": ("█", "█", " ", " ", " "),
    ":": (" ", "█", " ", "█", " "),
    "/": ("   █", "  █ ", " █  ", "█   ", "    "),
    "_": ("    ", "    ", "    ", "    ", "████"),
    "*": ("    ", "█ █ ", " █  ", "█ █ ", "    "),
    "#": (" █ █ ", "█████", " █ █ ", "█████", " █ █ "),
}

CHARS = " .:-=+*#%@"  # dark to bright


def banner(text, double=False):
    """Render text as a block-letter banner. Unsupported chars become spaces."""
    text = text.upper()
    rows = ["", "", "", "", ""]
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for i in range(5):
            line = glyph[i]
            if double:
                line = "".join(c * 2 for c in line)
            rows[i] += line + ("  " if double else " ")
    return "\n".join(r.rstrip() for r in rows)


def _read_netpbm(path):
    """Read a PGM/PPM (P2/P3/P5/P6) file. Return (width, height, gray rows)."""
    with open(path, "rb") as fh:
        data = fh.read()
    tokens, i, n = [], 0, len(data)
    while len(tokens) < 4 and i < n:
        c = data[i:i + 1]
        if c == b"#":
            while i < n and data[i:i + 1] != b"\n":
                i += 1
        elif c.isspace():
            i += 1
        else:
            j = i
            while j < n and not data[j:j + 1].isspace():
                j += 1
            tokens.append(data[i:j])
            i = j
    magic = tokens[0].decode()
    if magic not in ("P2", "P3", "P5", "P6"):
        raise ValueError("not a Netpbm file: {}".format(path))
    width, height, maxval = int(tokens[1]), int(tokens[2]), int(tokens[3])
    count = width * height
    if magic in ("P2", "P3"):
        nums = list(map(int, data[i:].split()))
        if magic == "P3":
            nums = [round(0.299 * nums[k] + 0.587 * nums[k + 1] + 0.114 * nums[k + 2])
                    for k in range(0, count * 3, 3)]
        gray = nums[:count]
    else:
        raw = data[i + 1:i + 1 + count * (3 if magic == "P6" else 1)]
        if magic == "P6":
            gray = [round(0.299 * raw[k] + 0.587 * raw[k + 1] + 0.114 * raw[k + 2])
                    for k in range(0, count * 3, 3)]
        else:
            gray = list(raw[:count])
    scale = 255.0 / maxval if maxval != 255 else 1.0
    rows = [[round(gray[y * width + x] * scale) for x in range(width)]
            for y in range(height)]
    return width, height, rows


def _load_gray(path):
    """Load an image as (width, height, grayscale rows 0-255)."""
    try:
        from PIL import Image
    except ImportError:
        return _read_netpbm(path)
    with Image.open(path) as img:
        img = img.convert("L")
        width, height = img.size
        px = list(img.getdata())
    rows = [px[y * width:(y + 1) * width] for y in range(height)]
    return width, height, rows


def image_to_ascii(path, width=80, invert=False, charset=CHARS):
    """Convert an image file to an ASCII-art string."""
    if width < 1:
        raise ValueError("width must be at least 1")
    src_w, src_h, rows = _load_gray(path)
    # Terminal characters are about twice as tall as they are wide.
    height = max(1, round(src_h * (width / src_w) * 0.5))
    ramp = charset[::-1] if invert else charset
    out = []
    for y in range(height):
        line = ""
        y0 = y * src_h // height
        y1 = max(y0 + 1, (y + 1) * src_h // height)
        for x in range(width):
            x0 = x * src_w // width
            x1 = max(x0 + 1, (x + 1) * src_w // width)
            total, cnt = 0, 0
            for yy in range(y0, min(y1, src_h)):
                for xx in range(x0, min(x1, src_w)):
                    total += rows[yy][xx]
                    cnt += 1
            avg = total / cnt if cnt else 0
            idx = min(len(ramp) - 1, int(avg / 256 * len(ramp)))
            line += ramp[idx]
        out.append(line)
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description="ASCII art generator.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_banner = sub.add_parser("banner", help="render text as a block-letter banner")
    p_banner.add_argument("text", help="text to render (A-Z, 0-9, basic punctuation)")
    p_banner.add_argument("--double", action="store_true", help="double-width glyphs")

    p_image = sub.add_parser("image", help="convert an image to ASCII art")
    p_image.add_argument("path", help="image file (PNG/JPEG via Pillow, or PGM/PPM)")
    p_image.add_argument("--width", type=int, default=80, help="output width in characters")
    p_image.add_argument("--invert", action="store_true", help="invert brightness ramp")

    args = parser.parse_args(argv)
    if args.command == "banner":
        print(banner(args.text, double=args.double))
    else:
        try:
            print(image_to_ascii(args.path, width=args.width, invert=args.invert))
        except (OSError, ValueError) as exc:
            print("Error: {}".format(exc), file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
