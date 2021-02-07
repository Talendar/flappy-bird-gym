## Flappy Bird for OpenAI Gym

This repository contains an implementation of an OpenAI Gym environment for the Flappy Bird
game. It's based on [FlapPyBird](https://github.com/sourabhv/FlapPyBird), by
[@sourabhv](https://github.com/sourabhv). Currently, the environment provides the following
observation parameters to the agents: 

* The bird's *y* position;
* The bird's vertical velocity;
* Horizontal distance to the next pipe;
* The next pipe's *y* position.

In the future, I also intend to implement a version of the environment that provides an
image representing the game's screen as observation.

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

Like with other `gym` environments, it's very easy to use `flappy-bird-gym`. Simply import the
package and create the environment with the `make` function. Take a look at the sample code
below:

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
