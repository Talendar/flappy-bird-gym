""" Original Flappy Bird game by `sourahbhv`.

Copy of the code in the "FlapPyBird" repository on GitHub
(https://github.com/sourabhv/FlapPyBird) by `sourahbhv`. Minor alterations were
made on the code in order to improve readability.
"""

from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *

ASSETS_DIR = "./flappy_bird_gym/assets"

FPS = 30
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
PIPE_GAP_SIZE = 100  # gap between upper and lower part of pipe
BASE_Y = SCREEN_HEIGHT * 0.79

# image, sound and hit-mask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        ASSETS_DIR + '/sprites/redbird-upflap.png',
        ASSETS_DIR + '/sprites/redbird-midflap.png',
        ASSETS_DIR + '/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        ASSETS_DIR + '/sprites/bluebird-upflap.png',
        ASSETS_DIR + '/sprites/bluebird-midflap.png',
        ASSETS_DIR + '/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        ASSETS_DIR + '/sprites/yellowbird-upflap.png',
        ASSETS_DIR + '/sprites/yellowbird-midflap.png',
        ASSETS_DIR + '/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    ASSETS_DIR + '/sprites/background-day.png',
    ASSETS_DIR + '/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    ASSETS_DIR + '/sprites/pipe-green.png',
    ASSETS_DIR + '/sprites/pipe-red.png',
)


def main():
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load(ASSETS_DIR + '/sprites/0.png').convert_alpha(),
        pygame.image.load(ASSETS_DIR + '/sprites/1.png').convert_alpha(),
        pygame.image.load(ASSETS_DIR + '/sprites/2.png').convert_alpha(),
        pygame.image.load(ASSETS_DIR + '/sprites/3.png').convert_alpha(),
        pygame.image.load(ASSETS_DIR + '/sprites/4.png').convert_alpha(),
        pygame.image.load(ASSETS_DIR + '/sprites/5.png').convert_alpha(),
        pygame.image.load(ASSETS_DIR + '/sprites/6.png').convert_alpha(),
        pygame.image.load(ASSETS_DIR + '/sprites/7.png').convert_alpha(),
        pygame.image.load(ASSETS_DIR + '/sprites/8.png').convert_alpha(),
        pygame.image.load(ASSETS_DIR + '/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load(ASSETS_DIR + '/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load(ASSETS_DIR + '/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load(ASSETS_DIR + '/sprites/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die'] = pygame.mixer.Sound(ASSETS_DIR + '/audio/die' + soundExt)
    SOUNDS['hit'] = pygame.mixer.Sound(ASSETS_DIR + '/audio/hit' + soundExt)
    SOUNDS['point'] = pygame.mixer.Sound(ASSETS_DIR + '/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound(ASSETS_DIR + '/audio/swoosh' + soundExt)
    SOUNDS['wing'] = pygame.mixer.Sound(ASSETS_DIR + '/audio/wing' + soundExt)

    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipe_index = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipe_index]).convert_alpha(), False, True),
            pygame.image.load(PIPES_LIST[pipe_index]).convert_alpha(),
        )

        # hismask for pipes
        HITMASKS['pipe'] = (
            get_hitmask(IMAGES['pipe'][0]),
            get_hitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            get_hitmask(IMAGES['player'][0]),
            get_hitmask(IMAGES['player'][1]),
            get_hitmask(IMAGES['player'][2]),
        )

        movement_info = show_welcome_animation()
        crash_info = main_game(movement_info)
        show_game_over_screen(crash_info)


def show_welcome_animation():
    """ Shows welcome screen animation of flappy bird. """
    # index of player to blit on screen
    player_index = 0
    player_index_gen = cycle([0, 1, 2, 1])
    # iterator used to change player_index after every 5th iteration
    loop_iter = 0

    player_x = int(SCREEN_WIDTH * 0.2)
    player_y = int((SCREEN_HEIGHT - IMAGES['player'][0].get_height()) / 2)

    message_x = int((SCREEN_WIDTH - IMAGES['message'].get_width()) / 2)
    message_y = int(SCREEN_HEIGHT * 0.12)

    base_x = 0
    # amount by which base can maximum shift to left
    base_shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    player_shm_vals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for main_game
                SOUNDS['wing'].play()
                return {
                    'player_y': player_y + player_shm_vals['val'],
                    'base_x': base_x,
                    'player_index_gen': player_index_gen,
                }

        # adjust player_y, player_index, base_x
        if (loop_iter + 1) % 5 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 4) % base_shift)
        playerShm(player_shm_vals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][player_index],
                    (player_x, player_y + player_shm_vals['val']))
        SCREEN.blit(IMAGES['message'], (message_x, message_y))
        SCREEN.blit(IMAGES['base'], (base_x, BASE_Y))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def main_game(movement_info):
    score = player_index = loop_iter = 0
    player_index_gen = movement_info['player_index_gen']
    player_x, player_y = int(SCREEN_WIDTH * 0.2), movement_info['player_y']

    base_x = movement_info['base_x']
    base_shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upper_pipes lower_pipes list
    new_pipe1 = get_random_pipe()
    new_pipe2 = get_random_pipe()

    # list of upper pipes
    upper_pipes = [
        {'x': SCREEN_WIDTH + 200, 'y': new_pipe1[0]['y']},
        {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': new_pipe2[0]['y']},
    ]

    # list of lower pipes
    lower_pipes = [
        {'x': SCREEN_WIDTH + 200, 'y': new_pipe1[1]['y']},
        {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': new_pipe2[1]['y']},
    ]

    pipe_vel_x = -4

    # player velocity, max velocity, downward acceleration, acceleration on flap
    player_vel_y = -9  # player's velocity along Y, default same as player_flapped
    player_max_vel_y = 10   # max vel along Y, max descend speed
    player_min_vel_y = -8   # min vel along Y, max ascend speed
    player_acc_y = 1   # players downward accleration
    player_rot = 45   # player's rotation
    player_vel_rot = 3   # angular speed
    player_rot_thr = 20   # rotation threshold
    player_flap_acc = -9   # players speed on flapping
    player_flapped = False  # True when player flaps

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y > -2 * IMAGES['player'][0].get_height():
                    player_vel_y = player_flap_acc
                    player_flapped = True
                    SOUNDS['wing'].play()

        # check for crash here
        crash_test = check_crash({'x': player_x, 'y': player_y, 'index': player_index},
                                 upper_pipes, lower_pipes)
        if crash_test[0]:
            return {
                'y': player_y,
                'groundCrash': crash_test[1],
                'base_x': base_x,
                'upper_pipes': upper_pipes,
                'lower_pipes': lower_pipes,
                'score': score,
                'player_vel_y': player_vel_y,
                'player_rot': player_rot
            }

        # check for score
        player_mid_pos = player_x + IMAGES['player'][0].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1
                SOUNDS['point'].play()

        # player_index base_x change
        if (loop_iter + 1) % 3 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 100) % base_shift)

        # rotate the player
        if player_rot > -90:
            player_rot -= player_vel_rot

        # player's movement
        if player_vel_y < player_max_vel_y and not player_flapped:
            player_vel_y += player_acc_y
        if player_flapped:
            player_flapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            player_rot = 45

        player_height = IMAGES['player'][player_index].get_height()
        player_y += min(player_vel_y, BASE_Y - player_y - player_height)

        # move pipes to left
        for up_pipe, low_pipe in zip(upper_pipes, lower_pipes):
            up_pipe['x'] += pipe_vel_x
            low_pipe['x'] += pipe_vel_x

        # add new pipe when first pipe is about to touch left of screen
        if len(upper_pipes) > 0 and 0 < upper_pipes[0]['x'] < 5:
            newPipe = get_random_pipe()
            upper_pipes.append(newPipe[0])
            lower_pipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if len(upper_pipes) > 0 and upper_pipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for up_pipe, low_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGES['pipe'][0], (up_pipe['x'], up_pipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (low_pipe['x'], low_pipe['y']))

        SCREEN.blit(IMAGES['base'], (base_x, BASE_Y))
        # print score so player overlaps the score
        show_score(score)

        # Player rotation has a threshold
        visible_rot = player_rot_thr
        if player_rot <= player_rot_thr:
            visible_rot = player_rot
        
        player_surface = pygame.transform.rotate(IMAGES['player'][player_index], visible_rot)
        SCREEN.blit(player_surface, (player_x, player_y))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def show_game_over_screen(crash_info):
    """crashes the player down ans shows game over image"""
    score = crash_info['score']
    player_x = SCREEN_WIDTH * 0.2
    player_y = crash_info['y']
    player_height = IMAGES['player'][0].get_height()
    player_vel_y = crash_info['player_vel_y']
    player_acc_y = 2
    player_rot = crash_info['player_rot']
    player_vel_rot = 7

    base_x = crash_info['base_x']

    upper_pipes, lower_pipes = crash_info['upper_pipes'], crash_info['lower_pipes']

    # play hit and die sounds
    SOUNDS['hit'].play()
    if not crash_info['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y + player_height >= BASE_Y - 1:
                    return

        # player y shift
        if player_y + player_height < BASE_Y - 1:
            player_y += min(player_vel_y, BASE_Y - player_y - player_height)

        # player velocity change
        if player_vel_y < 15:
            player_vel_y += player_acc_y

        # rotate only when it's a pipe crash
        if not crash_info['groundCrash']:
            if player_rot > -90:
                player_rot -= player_vel_rot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for up_pipe, low_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGES['pipe'][0], (up_pipe['x'], up_pipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (low_pipe['x'], low_pipe['y']))

        SCREEN.blit(IMAGES['base'], (base_x, BASE_Y))
        show_score(score)

        player_surface = pygame.transform.rotate(IMAGES['player'][1], player_rot)
        SCREEN.blit(player_surface, (player_x,player_y))
        SCREEN.blit(IMAGES['gameover'], (50, 180))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(player_shm):
    """ Oscillates the value of player_shm['val'] between 8 and -8. """
    if abs(player_shm['val']) == 8:
        player_shm['dir'] *= -1

    if player_shm['dir'] == 1:
        player_shm['val'] += 1
    else:
        player_shm['val'] -= 1


def get_random_pipe():
    """ Returns a randomly generated pipe. """
    # y of gap between upper and lower pipe
    gap_y = random.randrange(0, int(BASE_Y * 0.6 - PIPE_GAP_SIZE))
    gap_y += int(BASE_Y * 0.2)
    pipe_height = IMAGES['pipe'][0].get_height()
    pipe_x = SCREEN_WIDTH + 10

    return [
        {'x': pipe_x, 'y': gap_y - pipe_height},  # upper pipe
        {'x': pipe_x, 'y': gap_y + PIPE_GAP_SIZE},  # lower pipe
    ]


def show_score(score):
    """ Displays score in center of screen. """
    score_digits = [int(x) for x in list(str(score))]
    total_width = 0  # total width of all numbers to be printed

    for digit in score_digits:
        total_width += IMAGES['numbers'][digit].get_width()

    x_offset = (SCREEN_WIDTH - total_width) / 2

    for digit in score_digits:
        SCREEN.blit(IMAGES['numbers'][digit], (x_offset, SCREEN_HEIGHT * 0.1))
        x_offset += IMAGES['numbers'][digit].get_width()


def check_crash(player, upper_pipes, lower_pipes):
    """ Returns True if player colliders with base or pipes. """
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASE_Y - 1:
        return [True, True]
    else:
        player_rect = pygame.Rect(player['x'], player['y'], player['w'], player['h'])
        pipe_w = IMAGES['pipe'][0].get_width()
        pipe_h = IMAGES['pipe'][0].get_height()

        for up_pipe, low_pipe in zip(upper_pipes, lower_pipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(up_pipe['x'], up_pipe['y'], pipe_w, pipe_h)
            lPipeRect = pygame.Rect(low_pipe['x'], low_pipe['y'], pipe_w, pipe_h)

            # player and upper/lower pipe hitmasks
            p_hitmask = HITMASKS['player'][pi]
            up_hitmask = HITMASKS['pipe'][0]
            low_hitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            up_collide = pixel_collision(player_rect, uPipeRect, p_hitmask, up_hitmask)
            low_collide = pixel_collision(player_rect, lPipeRect, p_hitmask, low_hitmask)

            if up_collide or low_collide:
                return [True, False]

    return [False, False]


def pixel_collision(rect1, rect2, hitmask1, hitmask2):
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


def get_hitmask(image):
    """ Returns a hitmask using an image's alpha. """
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


if __name__ == '__main__':
    main()
