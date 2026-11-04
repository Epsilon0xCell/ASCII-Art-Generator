# ASCII-Art-Generator

ASCII generated art: block-letter text banners and image-to-ASCII conversion. Small enough to include in a shell start config.

![License](https://img.shields.io/badge/license-MIT-green.svg)

<p align="center"><img src="banner.png" alt="ASCII-Art-Generator banner" width="700"></p>

**The Phosphor Blockworks**
_Pictures rebuilt block by block, in green light on charcoal._

> Bench note, stamped in phosphor: the bench below is laid out block by block, banners first, then photographs, then the library shelf.

## Quick Start

```sh
git clone https://github.com/Epsilon0xCell/ASCII-Art-Generator.git
```

No required dependencies: images are read with Pillow when it is installed, and Netpbm files are read natively without it (see Image to ASCII).

Formats and options: with Pillow installed, PNG, JPEG, GIF and BMP images are read; Netpbm files (PGM/PPM, plain or raw) are read natively without it. Image conversion takes a `--width` option (output width in characters, default 80) and an `--invert` option; see Image to ASCII below.

## Example: an image converted to ASCII

Source image in this repo, `logo.png`:

<p align="center"><img src="logo.png" alt="ASCII-Art-Generator logo, the source image for the conversion example" width="180"></p>

```sh
python3 ascii_art.py image logo.png --width 40
```

Output (real output of the command above, trailing spaces trimmed):

```
........................................
........................................
........................................
........................................
...................::...................
................::----::................
.............::--=+##+=-:::.............
..........:::-:-:-+**+----::::..........
.......::::--:--++===-+#+++++=-::.......
....:::---------#%#*+*#*=-::---::::...
... .::::::-----**=-----::::-::.....
..     .::::::*#*+-----::::......
..        .:::=#----:::::.....
.            .::..::::.....
                ...::...
                   ::.




```


<img src="sep-heavy.svg" alt="" width="100%">

## Text banners


```sh
python3 ascii_art.py banner "HELLO"
python3 ascii_art.py banner --double "HI"   # double-width glyphs
```

Output:

```
█  █ ███
█  █  █
████  █
█  █  █
█  █ ███
```

The font covers A-Z, 0-9 and basic punctuation (`.,!?-+'":/*_#` and space).
Input is uppercased first; any other character renders as a space.

Shell startup example (`.bashrc` / `.zshrc`):

```sh
python3 ~/ASCII-Art-Generator/ascii_art.py banner "WELCOME"
```

<img src="sep-light.svg" alt="" width="100%">

## Image to ASCII


```sh
python3 ascii_art.py image photo.png
python3 ascii_art.py image photo.png --width 120 --invert
```

- `--width` sets the output width in characters (default 80); height is scaled automatically with terminal character aspect correction.
- Images are read with Pillow when installed (PNG, JPEG, GIF, BMP, ...). Without Pillow, Netpbm files (PGM/PPM, plain or raw) are read natively, so the tool still works with zero dependencies.

<img src="sep-heavy.svg" alt="" width="100%">

## Library use


```python
from ascii_art import banner, image_to_ascii

print(banner("CODE"))
print(image_to_ascii("photo.png", width=100))
```

## License


MIT (see LICENSE).

## Visual Identity

<p align="center"><img src="intro-banner.png" alt="ASCII-Art-Generator introduction, wordless" width="800"></p>

<img src="assets-scene.svg" alt="ASCII-Art-Generator animated scene" width="100%">
