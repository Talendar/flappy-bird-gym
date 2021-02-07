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

""" Implements the game's renderer, responsible from drawing the game on the
screen.

Some of the code in this module is an adaption of the code in the `FlapPyBird`
GitHub repository by `sourahbhv` (https://github.com/sourabhv/FlapPyBird),
released under the MIT license.
"""

from typing import Tuple

import pygame

from gym_flappy_bird.envs import utils

PLAYER_ROT_THR = 20  # rotation threshold


class FlappyBirdRenderer:
    """ Handles the rendering of the game.

    This class implements the game's renderer, responsible from drawing the game
    on the screen.

    Args:
        screen_size (Tuple[int, int]): The screen's width and height.
        audio_on (bool): Whether the game's audio is ON or OFF.
        bird_color (str): Color of the flappy bird.
        pipe_color (str): Color of the pipes.
        background (str): Type of background image.
    """

    def __init__(self,
                 screen_size: Tuple[int, int] = (288, 512),
                 audio_on: bool = True,
                 bird_color: str = "yellow",
                 pipe_color: str = "green",
                 background: str = "day") -> None:
        self._screen_width = screen_size[0]
        self._screen_height = screen_size[1]

        self._display = pygame.display.set_mode(screen_size)
        self.images = utils.load_images(bird_color=bird_color,
                                        pipe_color=pipe_color,
                                        bg_type=background)
        self.audio_on = audio_on
        if audio_on:
            self.sounds = utils.load_sounds()

        self.game = None
        self._clock = pygame.time.Clock()

    def _show_score(self) -> None:
        """ Displays score in center of screen. """
        score_digits = [int(x) for x in list(str(self.game.score))]
        total_width = 0  # total width of all numbers to be printed

        for digit in score_digits:
            total_width += self.images['numbers'][digit].get_width()

        x_offset = (self._screen_width - total_width) / 2

        for digit in score_digits:
            self._display.blit(self.images['numbers'][digit],
                               (x_offset, self._screen_height * 0.1))
            x_offset += self.images['numbers'][digit].get_width()

    def render(self) -> None:
        """ Renders the next frame. """
        if self.game is None:
            raise ValueError("A game logic must be assigned to the renderer!")

        # Sounds:
        if self.audio_on and self.game.sound_cache is not None:
            self.sounds[self.game.sound_cache].play()

        # Images:
        self._display.blit(self.images['background'], (0, 0))

        for up_pipe, low_pipe in zip(self.game.upper_pipes,
                                     self.game.lower_pipes):
            self._display.blit(self.images['pipe'][0],
                               (up_pipe['x'], up_pipe['y']))
            self._display.blit(self.images['pipe'][1],
                               (low_pipe['x'], low_pipe['y']))

        self._display.blit(self.images['base'], (self.game.base_x,
                                                 self.game.base_y))
        # print score so player overlaps the score
        self._show_score()

        # Player rotation has a threshold
        visible_rot = PLAYER_ROT_THR
        if self.game.player_rot <= PLAYER_ROT_THR:
            visible_rot = self.game.player_rot

        player_surface = pygame.transform.rotate(
            self.images['player'][self.game.player_idx],
            visible_rot,
        )

        self._display.blit(player_surface, (self.game.player_x,
                                            self.game.player_y))

        pygame.display.update()
