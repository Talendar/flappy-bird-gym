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

""" Implements the logic of the Flappy Bird game.

Some of the code in this module is an adaption of the code in the `FlapPyBird`
GitHub repository by `sourahbhv` (https://github.com/sourabhv/FlapPyBird),
released under the MIT license.
"""


import random
from enum import IntEnum
from itertools import cycle
from typing import Dict, Tuple, Union

import pygame

############################ Speed and Acceleration ############################
PIPE_VEL_X = -4

PLAYER_MAX_VEL_Y = 10  # max vel along Y, max descend speed
PLAYER_MIN_VEL_Y = -8  # min vel along Y, max ascend speed

PLAYER_ACC_Y = 1       # players downward acceleration
PLAYER_VEL_ROT = 3     # angular speed

PLAYER_FLAP_ACC = -9   # players speed on flapping
################################################################################


################################## Dimensions ##################################
PLAYER_WIDTH = 34
PLAYER_HEIGHT = 24

PIPE_WIDTH = 52
PIPE_HEIGHT = 320

BASE_WIDTH = 336
BASE_HEIGHT = 112

BACKGROUND_WIDTH = 288
BACKGROUND_HEIGHT = 512
################################################################################


class FlappyBirdLogic:
    """ Handles the logic of the Flappy Bird game.

    The implementation of this class is decoupled from the implementation of the
    game's graphics. This class implements the logical portion of the game.

    Args:
        screen_size (Tuple[int, int]): Tuple with the screen's width and height.
        pipe_gap_size (int): Space between a lower and an upper pipe.

    Attributes:
        player_x (int): The player's x position.
        player_y (int): The player's y position.
        base_x (int): The base/ground's x position.
        base_y (int): The base/ground's y position.
        score (int): Current score of the player.
        upper_pipes (List[Dict[str, int]): List with the upper pipes. Each pipe
            is represented by a dictionary containing two keys: "x" (the pipe's
            x position) and "y" (the pipe's y position).
        lower_pipes (List[Dict[str, int]): List with the lower pipes. Each pipe
            is represented by a dictionary containing two keys: "x" (the pipe's
            x position) and "y" (the pipe's y position).
        player_vel_y (int): The player's vertical velocity.
        player_rot (int): The player's rotation angle.
        last_action (Optional[FlappyBirdLogic.Actions]): The last action taken
            by the player. If `None`, the player hasn't taken any action yet.
        sound_cache (Optional[str]): Stores the name of the next sound to be
            played. If `None`, then no sound should be played.
        player_idx (int): Current index of the bird's animation cycle.
    """

    def __init__(self,
                 screen_size: Tuple[int, int],
                 pipe_gap_size: int = 100) -> None:
        self._screen_width = screen_size[0]
        self._screen_height = screen_size[1]

        self.player_x = int(self._screen_width * 0.2)
        self.player_y = int((self._screen_height - PLAYER_HEIGHT) / 2)

        self.base_x = 0
        self.base_y = self._screen_height * 0.79
        self._base_shift = BASE_WIDTH - BACKGROUND_WIDTH

        self.score = 0
        self._pipe_gap_size = pipe_gap_size

        # Generate 2 new pipes to add to upper_pipes and lower_pipes lists
        new_pipe1 = self._get_random_pipe()
        new_pipe2 = self._get_random_pipe()

        # List of upper pipes:
        self.upper_pipes = [
            {"x": self._screen_width + 200,
             "y": new_pipe1[0]["y"]},
            {"x": self._screen_width + 200 + (self._screen_width / 2),
             "y": new_pipe2[0]["y"]},
        ]

        # List of lower pipes:
        self.lower_pipes = [
            {"x": self._screen_width + 200,
             "y": new_pipe1[1]["y"]},
            {"x": self._screen_width + 200 + (self._screen_width / 2),
             "y": new_pipe2[1]["y"]},
        ]

        # Player's info:
        self.player_vel_y = -9  # player"s velocity along Y
        self.player_rot = 45  # player"s rotation

        self.last_action = None
        self.sound_cache = None

        self._player_flapped = False
        self.player_idx = 0
        self._player_idx_gen = cycle([0, 1, 2, 1])
        self._loop_iter = 0

    class Actions(IntEnum):
        """ Possible actions for the player to take. """
        IDLE, FLAP = 0, 1

    def _get_random_pipe(self) -> Dict[str, int]:
        """ Returns a randomly generated pipe. """
        # y of gap between upper and lower pipe
        gap_y = random.randrange(0,
                                 int(self.base_y * 0.6 - self._pipe_gap_size))
        gap_y += int(self.base_y * 0.2)

        pipe_x = self._screen_width + 10
        return [
            {"x": pipe_x, "y": gap_y - PIPE_HEIGHT},          # upper pipe
            {"x": pipe_x, "y": gap_y + self._pipe_gap_size},  # lower pipe
        ]

    def check_crash(self) -> bool:
        """ Returns True if player collides with the ground (base) or a pipe.
        """
        # if player crashes into ground
        if self.player_y + PLAYER_HEIGHT >= self.base_y - 1:
            return True
        else:
            player_rect = pygame.Rect(self.player_x, self.player_y,
                                      PLAYER_WIDTH, PLAYER_HEIGHT)

            for up_pipe, low_pipe in zip(self.upper_pipes, self.lower_pipes):
                # upper and lower pipe rects
                up_pipe_rect = pygame.Rect(up_pipe['x'], up_pipe['y'],
                                           PIPE_WIDTH, PIPE_HEIGHT)
                low_pipe_rect = pygame.Rect(low_pipe['x'], low_pipe['y'],
                                            PIPE_WIDTH, PIPE_HEIGHT)

                # check collision
                up_collide = player_rect.colliderect(up_pipe_rect)
                low_collide = player_rect.colliderect(low_pipe_rect)

                if up_collide or low_collide:
                    return True

        return False

    def update_state(self, action: Union[Actions, int]) -> bool:
        """ Given an action taken by the player, updates the game's state.

        Args:
            action (Union[FlappyBirdLogic.Actions, int]): The action taken by
                the player.

        Returns:
            `True` if the player is alive and `False` otherwise.
        """
        self.sound_cache = None
        if action == FlappyBirdLogic.Actions.FLAP:
            if self.player_y > -2 * PLAYER_HEIGHT:
                self.player_vel_y = PLAYER_FLAP_ACC
                self._player_flapped = True
                self.sound_cache = "wing"

        self.last_action = action
        if self.check_crash():
            self.sound_cache = "hit"
            return False

        # check for score
        player_mid_pos = self.player_x + PLAYER_WIDTH / 2
        for pipe in self.upper_pipes:
            pipe_mid_pos = pipe['x'] + PIPE_WIDTH / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                self.score += 1
                self.sound_cache = "point"

        # player_index base_x change
        if (self._loop_iter + 1) % 3 == 0:
            self.player_idx = next(self._player_idx_gen)

        self._loop_iter = (self._loop_iter + 1) % 30
        self.base_x = -((-self.base_x + 100) % self._base_shift)

        # rotate the player
        if self.player_rot > -90:
            self.player_rot -= PLAYER_VEL_ROT

        # player's movement
        if self.player_vel_y < PLAYER_MAX_VEL_Y and not self._player_flapped:
            self.player_vel_y += PLAYER_ACC_Y

        if self._player_flapped:
            self._player_flapped = False

            # more rotation to cover the threshold
            # (calculated in visible rotation)
            self.player_rot = 45

        self.player_y += min(self.player_vel_y,
                             self.base_y - self.player_y - PLAYER_HEIGHT)

        # move pipes to left
        for up_pipe, low_pipe in zip(self.upper_pipes, self.lower_pipes):
            up_pipe['x'] += PIPE_VEL_X
            low_pipe['x'] += PIPE_VEL_X

        # add new pipe when first pipe is about to touch left of screen
        if len(self.upper_pipes) > 0 and 0 < self.upper_pipes[0]['x'] < 5:
            new_pipe = self._get_random_pipe()
            self.upper_pipes.append(new_pipe[0])
            self.lower_pipes.append(new_pipe[1])

        # remove first pipe if its out of the screen
        if (len(self.upper_pipes) > 0 and
                self.upper_pipes[0]['x'] < -PIPE_WIDTH):
            self.upper_pipes.pop(0)
            self.lower_pipes.pop(0)

        return True
