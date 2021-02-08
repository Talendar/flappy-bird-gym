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

""" Tests the RGB-observations version of the Flappy Bird environment with a
human player.
"""

import time

import flappy_bird_gym
import numpy as np
import pygame
from PIL import Image


def play_with_render(env):
    clock = pygame.time.Clock()
    score = 0

    obs = env.reset()
    while True:
        env.render()

        # Getting action:
        action = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if (event.type == pygame.KEYDOWN and
                    (event.key == pygame.K_SPACE or event.key == pygame.K_UP)):
                action = 1

        # Processing:
        obs, reward, done, info = env.step(action)

        score += reward
        print(f"Obs shape: {obs.shape}")
        print(f"Score: {score}\n")

        clock.tick(30)

        if done:
            env.render()
            time.sleep(0.6)
            break


def play_with_obs(env, greyscale: bool):
    obs = env.reset()

    # noinspection PyProtectedMember
    display = pygame.display.set_mode((env._renderer._screen_width,
                                       env._renderer._screen_height))
    clock = pygame.time.Clock()
    score = 0

    while True:
        if greyscale:
            obs = obs.mean(axis=-1)
            print(f"Grayscale obs shape: {obs.shape}")
            obs = np.repeat(obs[:, :, np.newaxis], 3, axis=2)

        pygame.surfarray.blit_array(display, obs)
        pygame.display.update()

        # Getting action:
        action = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if (event.type == pygame.KEYDOWN and
                    (event.key == pygame.K_SPACE or event.key == pygame.K_UP)):
                action = 1

        # Processing:
        obs, reward, done, info = env.step(action)

        score += reward
        print(f"Obs shape: {obs.shape}")
        print(f"Score: {score}\n")

        clock.tick(30)

        if done:
            time.sleep(0.6)
            break


def visualize_obs(env, greyscale: bool):
    obs = env.reset()
    obs = np.moveaxis(obs, source=1, destination=0)  # width <-> height
    if greyscale:
        obs = obs.mean(axis=-1)

    print(f"Obs shape: {obs.shape}")
    img = Image.fromarray(obs)

    img.show()
    time.sleep(3)
    img.close()


if __name__ == "__main__":
    flappy_env = flappy_bird_gym.make("FlappyBird-rgb-v0")

    print(f"Action space: {flappy_env.action_space}")
    print(f"Observation space: {flappy_env.observation_space}")

    visualize_obs(env=flappy_env, greyscale=False)
    visualize_obs(env=flappy_env, greyscale=True)

    play_with_render(env=flappy_env)

    play_with_obs(env=flappy_env, greyscale=False)
    play_with_obs(env=flappy_env, greyscale=True)

    flappy_env.close()
