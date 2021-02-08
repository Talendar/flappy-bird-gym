# MIT License
#
# Copyright (c) 2020 Gabriel Nogueira (Talendar)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

""" Utility functions.

Some of the code in this module is an adaption of the code in the `FlapPyBird`
GitHub repository by `sourahbhv` (https://github.com/sourabhv/FlapPyBird),
released under the MIT license.
"""

import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from pygame import image as pyg_image
from pygame import mixer as pyg_mixer
from pygame import Rect
from pygame.transform import flip as img_flip


_BASE_DIR = Path(os.path.dirname(os.path.realpath(__file__))).parent

SPRITES_PATH = str(_BASE_DIR / "assets/sprites")
AUDIO_PATH = str(_BASE_DIR / "assets/audio")


def pixel_collision(rect1: Rect,
                    rect2: Rect,
                    hitmask1: List[List[bool]],
                    hitmask2: List[List[bool]]) -> bool:
    """ Checks if two objects collide and not just their rects. """
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False


def get_hitmask(image) -> List[List[bool]]:
    """ Returns a hitmask using an image's alpha. """
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


def _load_sprite(filename, convert, alpha=True):
    img = pyg_image.load(f"{SPRITES_PATH}/{filename}")
    return (img.convert_alpha() if convert and alpha
            else img.convert() if convert
            else img)


def load_images(convert: bool = True,
                bg_type: Optional[str] = "day",
                bird_color: str = "yellow",
                pipe_color: str = "green") -> Dict[str, Any]:
    """ Loads and returns the image assets of the game. """
    images = {}

    try:
        # Sprites with the number for the score display:
        images["numbers"] = tuple([
            _load_sprite(f"{n}.png", convert=convert, alpha=True)
            for n in range(10)
        ])

        # Game over sprite:
        images["gameover"] = _load_sprite("gameover.png",
                                          convert=convert, alpha=True)

        # Welcome screen message sprite:
        images["message"] = _load_sprite("message.png",
                                         convert=convert, alpha=True)

        # Sprite for the base (ground):
        images["base"] = _load_sprite("base.png",
                                      convert=convert, alpha=True)

        # Background sprite:
        if bg_type is None:
            images["background"] = None
        else:
            images["background"] = _load_sprite(f"background-{bg_type}.png",
                                                convert=convert, alpha=False)

        # Bird sprites:
        images["player"] = (
            _load_sprite(f"{bird_color}bird-upflap.png",
                         convert=convert, alpha=True),
            _load_sprite(f"{bird_color}bird-midflap.png",
                         convert=convert, alpha=True),
            _load_sprite(f"{bird_color}bird-downflap.png",
                         convert=convert, alpha=True),
        )

        # Pipe sprites:
        pipe_sprite = _load_sprite(f"pipe-{pipe_color}.png",
                                   convert=convert, alpha=True)
        images["pipe"] = (img_flip(pipe_sprite, False, True),
                          pipe_sprite)
    except FileNotFoundError as ex:
        raise FileNotFoundError("Can't find the sprites folder! No such file or"
                                f" directory: {SPRITES_PATH}") from ex

    return images


def load_sounds() -> Dict[str, pyg_mixer.Sound]:
    """ Loads and returns the audio assets of the game. """
    pyg_mixer.init()
    sounds = {}

    if "win" in sys.platform:
        soundExt = ".wav"
    else:
        soundExt = ".ogg"

    try:
        sounds["die"] = pyg_mixer.Sound(AUDIO_PATH + "/die" + soundExt)
        sounds["hit"] = pyg_mixer.Sound(AUDIO_PATH + "/hit" + soundExt)
        sounds["point"] = pyg_mixer.Sound(AUDIO_PATH + "/point" + soundExt)
        sounds["swoosh"] = pyg_mixer.Sound(AUDIO_PATH + "/swoosh" + soundExt)
        sounds["wing"] = pyg_mixer.Sound(AUDIO_PATH + "/wing" + soundExt)
    except FileNotFoundError as ex:
        raise FileNotFoundError("Can't find the audio folder! No such file or "
                                f"directory: {AUDIO_PATH}") from ex

    return sounds
