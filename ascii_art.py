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
# The equal width rule is per glyph, not across the font. A narrow
# glyph like I is 3 wide and a wide one like M is 5 wide, and banner()
# below trusts the rows inside one glyph to match each other. If one
# row of a glyph is longer, every character after it on that row
# shifts. I learned that from V, X, and Y, whose rows once disagreed
# and made any banner using them come out crooked.
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
    "V": ("█   █", "█   █", "█   █", " █ █ ", "  █  "),
    "W": ("█   █", "█   █", "█ █ █", "██ ██", "█   █"),
    "X": ("█   █", " █ █ ", "  █  ", " █ █ ", "█   █"),
    "Y": ("█   █", " █ █ ", "  █  ", "  █  ", "  █  "),
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
    '"': ("█ █", "█ █", "   ", "   ", "   "),
    ":": (" ", "█", " ", "█", " "),
    "/": ("   █", "  █ ", " █  ", "█   ", "    "),
    "_": ("    ", "    ", "    ", "    ", "████"),
    "*": ("    ", "█ █ ", " █  ", "█ █ ", "    "),
    "#": (" █ █ ", "█████", " █ █ ", "█████", " █ █ "),
}

CHARS = " .:-=+*#%@"  # dark to bright
# I read this ramp as ink density. A black pixel maps to the space
# at the left and a white pixel maps to the @ at the right, so the
# marks get heavier where the picture gets brighter.


def banner(text, double=False):
    """Render text as a block-letter banner. Unsupported chars become spaces."""
    # I fold case here, at the entry, so the font only needs one set
    # of letters. Lowercase input is not drawn a second way. It is
    # replaced by the capital before any glyph lookup happens.
    text = text.upper()
    # The five empty rows are the output height. They have to match
    # the five strings in every glyph, or the indexing below runs
    # past the end of a glyph.
    rows = ["", "", "", "", ""]
    for ch in text:
        # A character with no glyph gets the space glyph. It still
        # takes that glyph's width, 3 columns, so an unsupported
        # character leaves a narrow gap instead of dropping out and
        # pulling the rest of the line to the left.
        glyph = FONT.get(ch, FONT[" "])
        for i in range(5):
            line = glyph[i]
            if double:
                # Doubling runs character by character before the
                # separator is added, so the spaces inside a glyph
                # widen too and the letter keeps its shape.
                line = "".join(c * 2 for c in line)
            rows[i] += line + ("  " if double else " ")
    # I strip the right edge of each finished row because every
    # glyph adds a separator after it, including the last one.
    # Without this, each line would end in a blank column.
    return "\n".join(r.rstrip() for r in rows)


def _read_netpbm(path):
    """Read a PGM/PPM (P2/P3/P5/P6) file. Return (width, height, gray rows)."""
    # I read the whole file into memory first. The header and the
    # pixel data share one byte stream, and the raw formats below
    # work by byte position, so holding it all makes the offset in
    # i something I can follow from the header straight into the data.
    with open(path, "rb") as fh:
        data = fh.read()
    tokens, i, n = [], 0, len(data)
    # I collect only the first four tokens: magic, width, height,
    # maxval. That is the whole header this reader accepts. A #
    # starts a comment only when it sits where a token could start.
    # A # glued to a number becomes part of that token instead, and
    # the number fails to parse further down.
    # When this loop ends, i sits on the delimiter right after
    # maxval. The raw readers below count from that exact spot, so
    # changing what this loop leaves in i breaks raw files first.
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
    # The token count check comes before the magic check, so a
    # short file reports as truncated even when its first bytes are
    # not Netpbm either. I want the caller told what stopped me.
    if len(tokens) < 4:
        raise ValueError("truncated Netpbm header: {}".format(path))
    magic = tokens[0].decode()
    if magic not in ("P2", "P3", "P5", "P6"):
        raise ValueError("not a Netpbm file: {}".format(path))
    width, height, maxval = int(tokens[1]), int(tokens[2]), int(tokens[3])
    # I check these three before any size math uses them. maxval of
    # 0 would divide by zero at the scaling step at the bottom, and
    # a zero width or height would make the pixel counts below lie.
    if width < 1 or height < 1 or maxval < 1:
        raise ValueError("invalid Netpbm header: {}".format(path))
    count = width * height
    if magic in ("P2", "P3"):
        # Plain formats store their numbers as text, so split() does
        # the work. Comment text left in the data area would fail
        # int() instead of being skipped. I accept that limit. The
        # header is the only place this reader handles comments.
        nums = list(map(int, data[i:].split()))
        need = count * 3 if magic == "P3" else count
        if len(nums) < need:
            raise ValueError("truncated Netpbm data: {}".format(path))
        if magic == "P3":
            # I use the same three luma weights here that the raw P6
            # path uses below, so a plain copy and a raw copy of one
            # image do not come out at different brightnesses.
            nums = [round(0.299 * nums[k] + 0.587 * nums[k + 1] + 0.114 * nums[k + 2])
                    for k in range(0, count * 3, 3)]
        # Extra numbers past the pixels I need are ignored. A file
        # with too much data parses the same as an exact one.
        gray = nums[:count]
    else:
        # Raw data starts after a single whitespace delimiter; a CRLF
        # line ending counts as one delimiter, not two.
        start = i + 2 if data[i:i + 2] == b"\r\n" else i + 1
        channels = 3 if magic == "P6" else 1
        # sample_bytes follows maxval, not the magic number. The
        # format stores two bytes per sample once maxval passes 255,
        # for gray and color alike, high byte first, which is why
        # the two byte path below multiplies the first byte by 256.
        sample_bytes = 2 if maxval > 255 else 1
        need = count * channels * sample_bytes
        # I slice exactly need bytes. Trailing bytes after the image
        # are ignored, the same as extra numbers on the plain path.
        raw = data[start:start + need]
        if len(raw) < need:
            raise ValueError("truncated Netpbm data: {}".format(path))
        if sample_bytes == 2:
            samples = [raw[k] * 256 + raw[k + 1] for k in range(0, need, 2)]
        else:
            samples = list(raw)
        if magic == "P6":
            gray = [round(0.299 * samples[k] + 0.587 * samples[k + 1] + 0.114 * samples[k + 2])
                    for k in range(0, count * 3, 3)]
        else:
            gray = samples[:count]
    # Scaling runs after the plain and raw paths join, so all four
    # formats land on the 0 to 255 range image_to_ascii() expects.
    # A sample written above maxval in the file is not clamped here
    # and can scale past 255. The ramp index in image_to_ascii()
    # clamps its end, but these rows themselves can hold more.
    scale = 255.0 / maxval if maxval != 255 else 1.0
    rows = [[round(gray[y * width + x] * scale) for x in range(width)]
            for y in range(height)]
    return width, height, rows


def _load_gray(path):
    """Load an image as (width, height, grayscale rows 0-255)."""
    # I try Pillow here, per call, instead of at import time.
    # Importing this module should not fail on a machine without
    # Pillow, and the banner path never needs an image library.
    try:
        from PIL import Image
    except ImportError:
        return _read_netpbm(path)
    # The fallback catches ImportError only. If Pillow is installed
    # and a file is damaged, Pillow's error is the one the caller
    # sees. I do not fall through and try the Netpbm reader as a
    # second guess at the same file.
    with Image.open(path) as img:
        img = img.convert("L")
        width, height = img.size
        # getdata() gives one flat list in row order, top row first.
        # The slicing below only works because that order holds and
        # because width comes from this same image object.
        px = list(img.getdata())
    rows = [px[y * width:(y + 1) * width] for y in range(height)]
    return width, height, rows


def image_to_ascii(path, width=80, invert=False, charset=CHARS):
    """Convert an image file to an ASCII-art string."""
    # I check width before the file is opened. A bad width reports
    # as a width error even if the path is also wrong, because the
    # width is the mistake I can name with certainty at this point.
    if width < 1:
        raise ValueError("width must be at least 1")
    src_w, src_h, rows = _load_gray(path)
    # Terminal characters are about twice as tall as they are wide.
    # The 0.5 is that correction, not a quality setting. max(1, ...)
    # keeps a very flat image at one output row instead of zero.
    height = max(1, round(src_h * (width / src_w) * 0.5))
    # Inverting reverses the ramp list and nothing else. The pixel
    # values and the averaging below run the same either way.
    ramp = charset[::-1] if invert else charset
    out = []
    # Each output cell owns a box of source pixels, cut with floor
    # division so the boxes tile the image with no overlap and no
    # gap. When the output is larger than the source, the max()
    # calls force each box to cover at least one source pixel, so
    # pixels repeat instead of leaving cells empty.
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
            # The cnt guard is the divide by zero guard. If a box
            # ever came up empty after the min() clipping above,
            # I map it to 0, the dark end of the ramp, instead of
            # letting the average raise on a conversion that far in.
            avg = total / cnt if cnt else 0
            # The clamp guards the top end. A plain 255 lands in
            # the last slot on its own, but a row value past 255
            # from the unclamped Netpbm scaling would index past
            # the end of the ramp without it.
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
    # The banner branch has no error path of its own. Any text
    # renders, even an empty string, which prints five blank lines.
    # Only the image branch turns errors into the exit 2 message.
    if args.command == "banner":
        print(banner(args.text, double=args.double))
    else:
        try:
            print(image_to_ascii(args.path, width=args.width, invert=args.invert))
        except (OSError, ValueError) as exc:
            print("Error: {}".format(exc), file=sys.stderr)
            return 2
    # argparse failures never reach this return. They exit with
    # code 2 through SystemExit, so a caller sees the same code for
    # a bad flag and for a bad image file, from two different paths.
    return 0


if __name__ == "__main__":
    sys.exit(main())
