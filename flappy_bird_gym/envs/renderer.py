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

from typing import Optional, Tuple

import pygame

from flappy_bird_gym.envs import utils

#: Player's rotation threshold.
PLAYER_ROT_THR = 20

#: Color to fill the surface's background when no background image was loaded.
FILL_BACKGROUND_COLOR = (200, 200, 200)


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
                 background: Optional[str] = "day") -> None:
        self._screen_width = screen_size[0]
        self._screen_height = screen_size[1]

        self.display = None
        self.surface = pygame.Surface(screen_size)
        self.images = utils.load_images(convert=False,
                                        bird_color=bird_color,
                                        pipe_color=pipe_color,
                                        bg_type=background)
        self.audio_on = audio_on
        self._audio_queue = []
        if audio_on:
            self.sounds = utils.load_sounds()

        self.game = None
        self._clock = pygame.time.Clock()

    def make_display(self) -> None:
        """ Initializes the pygame's display.

        Required for drawing images on the screen.
        """
        self.display = pygame.display.set_mode((self._screen_width,
                                                self._screen_height))
        for name, value in self.images.items():
            if value is None:
                continue

            if type(value) in (tuple, list):
                self.images[name] = tuple([img.convert_alpha()
                                           for img in value])
            else:
                self.images[name] = (value.convert() if name == "background"
                                     else value.convert_alpha())

    def _draw_score(self) -> None:
        """ Draws the score in the center of the surface. """
        score_digits = [int(x) for x in list(str(self.game.score))]
        total_width = 0  # total width of all numbers to be printed

        for digit in score_digits:
            total_width += self.images['numbers'][digit].get_width()

        x_offset = (self._screen_width - total_width) / 2

        for digit in score_digits:
            self.surface.blit(self.images['numbers'][digit],
                              (x_offset, self._screen_height * 0.1))
            x_offset += self.images['numbers'][digit].get_width()

    def draw_surface(self, show_score: bool = True) -> None:
        """ Re-draws the renderer's surface.

        This method updates the renderer's surface by re-drawing it according to
        the current state of the game.

        Args:
            show_score (bool): Whether to draw the player's score or not.
        """
        if self.game is None:
            raise ValueError("A game logic must be assigned to the renderer!")

        # Background
        if self.images['background'] is not None:
            self.surface.blit(self.images['background'], (0, 0))
        else:
            self.surface.fill(FILL_BACKGROUND_COLOR)

        # Pipes
        for up_pipe, low_pipe in zip(self.game.upper_pipes,
                                     self.game.lower_pipes):
            self.surface.blit(self.images['pipe'][0],
                              (up_pipe['x'], up_pipe['y']))
            self.surface.blit(self.images['pipe'][1],
                              (low_pipe['x'], low_pipe['y']))

        # Base (ground)
        self.surface.blit(self.images['base'], (self.game.base_x,
                                                self.game.base_y))

        # Score
        # (must be drawn before the player, so the player overlaps it)
        if show_score:
            self._draw_score()

        # Getting player's rotation
        visible_rot = PLAYER_ROT_THR
        if self.game.player_rot <= PLAYER_ROT_THR:
            visible_rot = self.game.player_rot

        # Player
        player_surface = pygame.transform.rotate(
            self.images['player'][self.game.player_idx],
            visible_rot,
        )

        self.surface.blit(player_surface, (self.game.player_x,
                                           self.game.player_y))

    def update_display(self) -> None:
        """ Updates the display with the current surface of the renderer.

        A call to this method is usually preceded by a call to
        :meth:`.draw_surface()`. This method simply updates the display by
        showing the current state of the renderer's surface on it, it doesn't
        make any change to the surface.
        """
        if self.display is None:
            raise RuntimeError(
                "Tried to update the display, but a display hasn't been "
                "created yet! To create a display for the renderer, you must "
                "call the `make_display()` method."
            )

        self.display.blit(self.surface, [0, 0])
        pygame.display.update()

        # Sounds:
        if self.audio_on and self.game.sound_cache is not None:
            sound_name = self.game.sound_cache
            self.sounds[sound_name].play()
