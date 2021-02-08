## Flappy Bird for OpenAI Gym

![Python versions](https://img.shields.io/pypi/pyversions/flappy-bird-gym)
[![PyPI](https://img.shields.io/pypi/v/flappy-bird-gym)](https://pypi.org/project/flappy-bird-gym/)
[![License](https://img.shields.io/github/license/Talendar/flappy-bird-gym)](https://github.com/Talendar/flappy-bird-gym/blob/master/LICENSE)

This repository contains the implementation of two OpenAI Gym environments for
the Flappy Bird game. The implementation of the game's logic and graphics was
based on the [FlapPyBird](https://github.com/sourabhv/FlapPyBird) project, by
[@sourabhv](https://github.com/sourabhv). 

The two environments differ only on the type of observations they yield for the
agents. The "FlappyBird-rgb-v0" environment, yields RGB-arrays (images)
representing the game's screen. The "FlappyBird-v0" environment, on the other
hand, yields simple numerical information about the game's state as
observations. The yielded attributes are the:

* horizontal distance to the next pipe;
* difference between the player's y position and the next hole's y position.

<br>

<p align="center">
  <img align="center" 
       src="https://github.com/Talendar/flappy-bird-gym/blob/main/imgs/yellow_bird_playing.gif?raw=true" 
       width="200"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img align="center" 
       src="https://github.com/Talendar/flappy-bird-gym/blob/main/imgs/red_bird_start_screen.gif?raw=true" 
       width="200"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img align="center" 
       src="https://github.com/Talendar/flappy-bird-gym/blob/main/imgs/blue_bird_playing.gif?raw=true" 
       width="200"/>
</p>

## Installation

To install `flappy-bird-gym`, simply run the following command:

    $ pip install flappy-bird-gym
    
## Usage

Like with other `gym` environments, it's very easy to use `flappy-bird-gym`.
Simply import the package and create the environment with the `make` function.
Take a look at the sample code below:

```
import time
import flappy_bird_gym
env = flappy_bird_gym.make("FlappyBird-v0")

obs = env.reset()
while True:
    # Next action:
    # (feed the observation to your agent here)
    action = ...  # env.action_space.sample() for a random action

    # Processing:
    obs, reward, done, info = env.step(action)
    
    # Rendering the game:
    # (remove this two lines during training)
    env.render()
    time.sleep(1 / 30)  # FPS
    
    # Checking if the player is still alive
    if done:
        break

env.close()
```

## Playing

To play the game (human mode), run the following command:

    $ flappy_bird_gym
    
To see a random agent playing, add an argument to the command:

    $ flappy_bird_gym --mode random
