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

""" Implementation of the flappy bird gym environment.
"""

from typing import Dict, Tuple, Union

import gym
import numpy as np
from gym import spaces

from flappy_bird_gym.envs.game_logic import FlappyBirdLogic, PIPE_WIDTH
from flappy_bird_gym.envs.renderer import FlappyBirdRenderer


class FlappyBirdEnv(gym.Env):
    """ Flappy bird gym environment.

    The reward received by the agent in each step is equal to the score obtained
    by the agent in that step. A score point is obtained every time the bird
    passes a pipe.

    About the observation space:
        [0] Bird y position;
        [1] Bird y velocity;
        [2] Horizontal distance to the next pipe;
        [3] y position of the next pipe.

    Args:
        screen_size (Tuple[int, int]): The screen's width and height.
        pipe_gap (int): Space between a lower and an upper pipe.
        bird_color (str): Color of the flappy bird. The currently available
            colors are "yellow", "blue" and "red".
        pipe_color (str): Color of the pipes. The currently available colors are
            "green" and "red".
        background (str): Type of background image. The currently available
            types are "day" and "night".
    """

    metadata = {'render.modes': ['human']}

    def __init__(self,
                 screen_size: Tuple[int, int] = (288, 512),
                 pipe_gap: int = 100,
                 bird_color: str = "yellow",
                 pipe_color: str = "green",
                 background: str = "day") -> None:
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(-np.inf, np.inf,
                                            shape=(4,),
                                            dtype=np.float32)
        self._screen_size = screen_size
        self._pipe_gap = pipe_gap

        self._game = None
        self._renderer = None
        self._last_score = 0

        self._bird_color = bird_color
        self._pipe_color = pipe_color
        self._bg_type = background

    def _get_observation(self):
        next_pipe = None
        for pipe in self._game.lower_pipes:
            if (pipe["x"] + PIPE_WIDTH / 2) > self._game.player_x:
                next_pipe = pipe
                break

        return np.array([
            self._game.player_y,
            self._game.player_vel_y,
            (next_pipe["x"] + PIPE_WIDTH) / 2 - self._game.player_x,
            next_pipe["y"],
        ])

    def step(self,
             action: Union[FlappyBirdLogic.Actions, int],
    ) -> Tuple[np.ndarray, float, bool, Dict]:
        """ Given an action, updates the game state.

        Args:
            action (Union[FlappyBirdLogic.Actions, int]): The action taken by
                the agent. Zero (0) means "do nothing" and one (1) means "flap".

        Returns:
            A tuple containing, respectively:

                * an observation (bird's y position; bird's y velocity;
                  horizontal distance to the next pipe; next pipe's y position);
                * a reward (1 if the agent passed a pipe and 0 otherwise);
                * a status report (`True` if the game is over and `False`
                  otherwise);
                * an info dictionary.
        """
        alive = self._game.update_state(action)
        obs = self._get_observation()

        reward = self._game.score - self._last_score
        self._last_score = self._game.score

        done = not alive
        info = {"score": self._game.score}

        return obs, reward, done, info

    def reset(self):
        """ Resets the environment (starts a new game). """
        self._game = FlappyBirdLogic(screen_size=self._screen_size,
                                     pipe_gap_size=self._pipe_gap)
        if self._renderer is not None:
            self._renderer.game = self._game

        return self._get_observation()

    def render(self, mode='human'):
        """ Renders the next frame. """
        if self._renderer is None:
            self._renderer = FlappyBirdRenderer(screen_size=self._screen_size,
                                                bird_color=self._bird_color,
                                                pipe_color=self._pipe_color,
                                                background=self._bg_type)
            self._renderer.game = self._game

        self._renderer.render()
