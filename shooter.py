# My name
# Final project for ECE102
# Started 9/05/2016     Due 12/08/2016

import cProfile
import logging
import os.path
import random
import sys
import time

import pygame
from pygame.locals import *

import bosses
import player
import powerups
from mylibrary import MyLibrary as ml

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)  # Disable annoying logging
# logging.disable(logging.INFO)  # Disable all logging
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center game window

# Toggle debug hotkeys and profiling
debug = False
frame_timer = False
profiling = False

FPS = 60
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 900

player_move_up = False
player_move_down = False
player_move_right = False
player_move_left = False
shift_pressed = False
mouse_movement_active = True
game_running = False

button_width = 225
button_height = 55
button_font_size = 26

# Set up pygame
pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF)
pygame.display.set_caption('ECE102 Final Project')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

cursor = pygame.image.load(os.path.join('graphics', 'cursor.png'))
cursor_rect = pygame.Rect(0, 0, cursor.get_width(), cursor.get_height())

start_time = time.time()


def main():

    # Hide cursor (replaced by custom image)
    pygame.mouse.set_visible(False)

    # Set up and load things when the game first runs
    ml.set_window_data(window)
    ml.loading_screen()
    pygame.display.update()
    ml.set_fps_clock(clock)
    ml.set_framerate(FPS)
    ml.load_images()
    if debug:
        logging.info('Loading time: %f' % (time.time() - start_time))

    while True:
        # Run main game loop
        if profiling:
            cProfile.run('run_game()')
        else:
            run_game()

        # run_game() returns when player dies
        game_over()


def run_game():
    """Runs the game."""
    global game_running

    # Create groups
    player_group = pygame.sprite.GroupSingle()
    player_bullet_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    enemy_bullet_group = pygame.sprite.Group()
    powerup_group = pygame.sprite.Group()
    powerup_effect_group = pygame.sprite.Group()
    boss_part_group = pygame.sprite.OrderedUpdates()

    # Set up MyLibrary data
    ml.set_sprite_groups(player_group, player_bullet_group, enemy_group,
                         enemy_bullet_group, powerup_group, powerup_effect_group,
                         boss_part_group)
    ml.reset_upgrades()
    ml.set_score(0)

    # Display the main menu
    main_menu()

    # Spawn player sprite
    player.Player()

    game_start_time = ml.time()
    boss_spawn_delay = 5
    current_boss = 0
    final_boss_dead = None
    boss_list = [bosses.StarBurst, bosses.Doppelganger, bosses.Ring]
    game_running = True

    while True:  # Main game loop

        # frame timer
        start = time.time()

        # Deal with all in-game events
        check_for_events()

        # Check if player is alive
        # TODO temporary for presentation
        if ml.player.health <= 0:
            ml.player.damage(-999)
            ml.change_score(-2500)
            # return

        # Clear window
        window.fill(BLACK)

        # Spawn powerups
        powerups.PowerUp.spawn_random((random.randint(30, window.get_width() - 30), -50))

        # Spawn bosses
        if ml.time() - game_start_time > boss_spawn_delay:
            if not enemy_group.sprites() and not final_boss_dead:
                try:
                    boss_list[current_boss]()
                except IndexError:
                    final_boss_dead = ml.time()
                current_boss += 1
        if final_boss_dead and ml.time() - final_boss_dead > 5:
            return

        # Update all Sprites
        player_group.update(player_move_up, player_move_left, player_move_down,
                            player_move_right, mouse_movement_active, shift_pressed)
        player_bullet_group.update()
        powerup_effect_group.update()
        enemy_group.update()
        boss_part_group.update()
        powerup_group.update()
        enemy_bullet_group.update()

        # Draw all Sprites (in order of increasing priority)
        player_bullet_group.draw(window)
        powerup_group.draw(window)
        enemy_group.draw(window)
        boss_part_group.draw(window)
        player_group.draw(window)
        powerup_effect_group.draw(window)
        enemy_bullet_group.draw(window)
        ml.draw_interface(window)

        if shift_pressed:
            draw_hitbox()
        draw_cursor()

        pygame.display.update()
        if frame_timer:
            print(time.time() - start)
        ml.tick()


def terminate():
    """Quit pygame and close the window."""
    logging.debug('Terminating program')
    pygame.display.quit()  # Close window faster
    pygame.quit()
    sys.exit()


def draw_cursor():
    cursor_rect.center = pygame.mouse.get_pos()
    window.blit(cursor, cursor_rect)


def draw_hitbox():
    window.blit(cursor, ml.player.hitbox)


def main_menu():
    """Shows the main menu."""

    global game_running
    button_x = (window.get_width() / 2) - (button_width / 2)
    top_button_y = (window.get_height() / 2) + (window.get_height() / 10)
    button_spacing = 15

    # Menu buttons
    if not game_running:
        start_game_text = 'Start Game'
        title_y = 150
        title_font = pygame.font.Font(ml.font, 90)
        title1 = title_font.render('ECE102', True, WHITE)
        title1_rect = pygame.Rect(ml.window_width / 2 - title1.get_width() / 2, title_y,
                                  title1.get_width(), title1.get_height())
        title2 = title_font.render('Final Project', True, WHITE)
        title2_rect = pygame.Rect(ml.window_width / 2 - title2.get_width() / 2, 0,
                                  title2.get_width(), title2.get_height())
        
        title2_rect.y = title_y + title1.get_height() + 25

    else:
        start_game_text = 'Continue'
    start_game_button = ml.get_button_surface(button_width, button_height,
                                              start_game_text, button_font_size, WHITE)
    start_game_button_rect = pygame.Rect(button_x, top_button_y, button_width, button_height)
    high_scores_button = ml.get_button_surface(button_width, button_height,
                                               'High Scores', button_font_size, WHITE)
    high_scores_button_rect = pygame.Rect(button_x, top_button_y +
                                          button_height + button_spacing,
                                          button_width, button_height)
    options_button = ml.get_button_surface(button_width, button_height,
                                           'Options', button_font_size, WHITE)
    option_button_rect = pygame.Rect(
            button_x, top_button_y + 2 * button_height + 2 * button_spacing,
            button_width, button_height)
    quit_button = ml.get_button_surface(button_width, button_height,
                                        'Quit Game', button_font_size, WHITE)
    quit_button_rect = pygame.Rect(button_x, top_button_y + 3 * button_height +
                                   3 * button_spacing,
                                   button_width, button_height)

    # Draw menu, wait for, and deal with choice
    while True:
        for event in pygame.event.get():

            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if game_running:
                        return
                    else:
                        terminate()
                elif event.key in (K_SPACE,):
                    return

            # Check if player clicked a button
            if event.type == MOUSEBUTTONUP:
                # Player clicks Start Game
                # noinspection PyArgumentList
                if start_game_button_rect.collidepoint(event.pos):
                    return
                # Player clicks Quit Game
                elif quit_button_rect.collidepoint(event.pos):
                    terminate()
                # Player clicks Options
                elif option_button_rect.collidepoint(event.pos):
                    options()
                # Player clicks High Scores
                elif high_scores_button_rect.collidepoint(event.pos):
                    highscores()

        # Clear the window
        window.fill(BLACK)

        # Draw buttons
        window.blit(start_game_button, start_game_button_rect)
        window.blit(high_scores_button, high_scores_button_rect)
        window.blit(options_button, option_button_rect)
        window.blit(quit_button, quit_button_rect)

        if not game_running:
            window.blit(title1, title1_rect)
            window.blit(title2, title2_rect)

        draw_cursor()
        pygame.display.update()
        clock.tick(FPS)


def highscores():
    """Show the highscores screen"""
    x_margin = 150
    top_scores = ml.get_highscores()[:8]
    pygame.event.clear()
    window.fill((0, 0, 0))
    score_font = pygame.font.Font(ml.font, 28)
    high_scores_title_font = pygame.font.Font(ml.font, 48)
    score_name_surfaces = []
    score_score_surfaces = []
    # Score display
    for score in top_scores:
        score_name_surfaces.append(score_font.render('%s:'
                                                     % score[0],
                                                     True, WHITE))
    for score in top_scores:
        score_score_surfaces.append(score_font.render(str(score[1]),
                                                      True, WHITE))
    high_scores_title = high_scores_title_font.render('High Scores', True, WHITE)

    # Back button
    back_button = ml.get_button_surface(button_width, button_height,
                                        'Back', button_font_size, WHITE)
    back_button_rect = pygame.Rect(x_margin, window.get_height() - 200,
                                   button_width, button_height)

    while True:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            # Escape closes the highscores screen
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
            # Player clicked Back button
            elif event.type == MOUSEBUTTONUP:
                # noinspection PyArgumentList
                if back_button_rect.collidepoint(event.pos):
                    return

        window.fill(BLACK)
        # Draw the scores
        for i, surface in enumerate(score_name_surfaces):
            window.blit(surface, (x_margin, 125 + (button_height + 15) * i))
        for i, surface in enumerate(score_score_surfaces):
            window.blit(score_score_surfaces[i],
                        (window.get_width() - x_margin - surface.get_width(),
                         125 + (button_height + 15) * i))
        window.blit(back_button, back_button_rect)
        window.blit(high_scores_title,
                    ((window.get_width() / 2) - (high_scores_title.get_width() / 2), 30))

        draw_cursor()
        pygame.display.update()
        clock.tick(FPS)


def game_over():
    """Shows the game over screen. Saves player score."""
    global player_move_up, player_move_left, player_move_down, player_move_right, \
        mouse_movement_active, shift_pressed, game_running
    logging.debug('Game Over')
    pygame.time.wait(1000)
    x_margin = 150

    # Reset player movement and event queue
    player_move_up = False
    player_move_down = False
    player_move_right = False
    player_move_left = False
    game_running = False
    shift_pressed = False
    pygame.event.clear()

    ml.update_boss_data(1, 0, '')

    # Clear window
    window.fill(BLACK)

    # Add player's score
    font = pygame.font.Font(ml.font, 30)
    score_font = pygame.font.Font(ml.font, 50)
    message_surface = font.render('Your final score:', True, WHITE)
    score_surface = score_font.render(str(ml.score), True, WHITE)
    message2_surface = font.render('Would you like to save your score?', True, WHITE)
    message3_surface = font.render('Score saved!', True, WHITE)
    no_button = ml.get_button_surface(button_width, button_height,
                                      'No', button_font_size, WHITE)
    no_button_rect = pygame.Rect(x_margin, window.get_height() - 200,
                                 button_width, button_height)
    yes_button = ml.get_button_surface(button_width, button_height,
                                       'Yes', button_font_size, WHITE)
    yes_button_rect = pygame.Rect(window.get_width() - button_width - x_margin,
                                  window.get_height() - 200, button_width, button_height)

    while True:
        # Clear the window
        window.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            # Escape returns to main menu
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return

            elif event.type == MOUSEBUTTONUP:
                # noinspection PyArgumentList
                # No button returns to main menu
                if no_button_rect.collidepoint(event.pos):
                    return
                # Yes button asks player for their name, then adds to high score list
                elif yes_button_rect.collidepoint(event.pos):
                    player_name = ask_player_input('Please enter your name:')
                    # player_name is '' if player cancels input
                    if player_name:
                        window.blit(message3_surface,
                                    ((window.get_width() / 2) -
                                     (message3_surface.get_width() / 2),
                                     window.get_height() / 2 + 100))
                        logging.info('Saving score:   %s: %d' % (player_name, ml.score))
                        ml.add_highscore(player_name, ml.score)
                        pygame.display.update()
                        pygame.time.wait(1500)
                    return

        # Blit text and buttons
        window.blit(message_surface, (
            (window.get_width() / 2) - (message_surface.get_width() / 2),
            (window.get_height() / 2) - 150
        ))
        window.blit(score_surface, (
            (window.get_width() / 2) - (score_surface.get_width() / 2),
            (window.get_height() / 2) - 85
        ))
        window.blit(message2_surface, (
            (window.get_width() / 2) - (message2_surface.get_width() / 2),
            (window.get_height() / 2)
        ))
        window.blit(no_button, no_button_rect)
        window.blit(yes_button, yes_button_rect)

        draw_cursor()
        pygame.display.update()
        clock.tick(FPS)


def options():
    """Shows the options menu."""
    global mouse_movement_active
    x_margin = 150

    mouse_button_rect = pygame.Rect(window.get_width() - x_margin - button_width,
                                    (window.get_height() / 2) - 50, button_width,
                                    button_height)
    keyboard_button_rect = pygame.Rect(x_margin,
                                       (window.get_height() / 2) - 50, button_width,
                                       button_height)
    back_button = ml.get_button_surface(button_width, button_height,
                                        'Back', button_font_size, WHITE)
    back_button_rect = pygame.Rect(x_margin, window.get_height() - 200,
                                   button_width, button_height)

    while True:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            # Escape closes the highscores screen
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                    # Player clicked keyboard button
            elif event.type == MOUSEBUTTONUP:
                # noinspection PyArgumentList
                if keyboard_button_rect.collidepoint(event.pos):
                    mouse_movement_active = False
                elif mouse_button_rect.collidepoint(event.pos):
                    mouse_movement_active = True
                elif back_button_rect.collidepoint(event.pos):
                    return

        window.fill(BLACK)

        # Change button color to indicate which is active
        if mouse_movement_active:
            mouse_color = WHITE
            keyboard_color = GRAY
        else:
            keyboard_color = WHITE
            mouse_color = GRAY
        mouse_button = ml.get_button_surface(button_width, button_height,
                                             'Mouse', button_font_size, mouse_color)
        keyboard_button = ml.get_button_surface(button_width, button_height,
                                                'Keyboard', button_font_size, keyboard_color)

        window.blit(keyboard_button, keyboard_button_rect)
        window.blit(mouse_button, mouse_button_rect)
        window.blit(back_button, back_button_rect)

        draw_cursor()
        pygame.display.update()
        clock.tick(FPS)


def upgrade_screen():
    """Shows the upgrade screen."""
    from collections import OrderedDict
    upgrade_list = list(ml.upgrades.keys())
    button_gap = 50
    button_x_list = []
    x_margin = 150
    y_start = 125
    u_button_width = 240
    u_button_height = 75
    name_font_size = 22
    score_margin = 10
    score_font = pygame.font.Font(ml.font, 36)
    value_font = pygame.font.Font(ml.font, 28)
    upgrades_title_font = pygame.font.Font(ml.font, 48)
    upgrades_title = upgrades_title_font.render('Upgrades', True, WHITE)
    continue_button = ml.get_button_surface(button_width, button_height,
                                            'Continue', button_font_size, WHITE)
    continue_button_rect = pygame.Rect(window.get_width() - button_width - x_margin,
                                       window.get_height() - 75 -
                                       continue_button.get_height(),
                                       button_width, button_height)

    # Creates list with x coordinates alternating between left and right side of window
    for i in range(len(upgrade_list)):
        if i % 2 == 0:
            button_x_list.append(x_margin)
        else:
            button_x_list.append(window.get_width() - x_margin - u_button_width)

    # Example output: [200, 200, 270, 270, 340, 340, 410, 410, 480, 480]
    button_y_list = [y_start]
    for i in range(len(upgrade_list) - 1):
        if i % 2 == 0:
            button_y_list.append(button_y_list[i])
        else:
            button_y_list.append(button_y_list[i] + button_gap + u_button_height)

    # Build list of Rects from those x and y coordinates
    button_rect_list = []
    for i, j in enumerate(upgrade_list):
        button_rect_list.append(pygame.Rect((button_x_list[i], button_y_list[i]),
                                            (u_button_width, u_button_height)))

    # Loop
    while True:
        # Clear the window
        window.fill(BLACK)

        # Show the current score in bottom-left corner
        score_surface = score_font.render('Score: %d' % (ml.score), True, WHITE)
        window.blit(score_surface, (
            score_margin,
            window.get_height() - score_margin - score_surface.get_height()
        ))

        # Build a list of button surfaces with upgrade names  and values
        button_surfaces = OrderedDict()
        offset = int(-1 * (u_button_height / 4))
        for upgrade in upgrade_list:
            # Create button with upgrade name on it
            button_surfaces[upgrade] = ml.get_button_surface(u_button_width, u_button_height,
                                                             upgrade, name_font_size, WHITE,
                                                             offset)
            value = str(ml.get_upgrade_values(upgrade))
            value_surface = value_font.render(value, True, WHITE)
            # Add the text for the current value of each upgrade
            button_surfaces[upgrade].blit(value_surface, (
                (button_surfaces[upgrade].get_width() / 2) - (value_surface.get_width() / 2),
                button_surfaces[upgrade].get_height() - value_surface.get_height() -
                (button_surfaces[upgrade].get_height() / 20)
            ))

        # Handle mouse-over
        pos = pygame.mouse.get_pos()
        for i, rect in enumerate(button_rect_list):
            if rect.collidepoint(pos):
                # Draw upgrade amount next to upgrade value
                upgrade_amount_surface = value_font.render(
                        ('+' if ml.get_upgrade_amount(upgrade_list[i]) >= 0 else '')
                        + str(ml.get_upgrade_amount(upgrade_list[i])),
                        True, GREEN)
                button_surfaces[upgrade_list[i]].blit(upgrade_amount_surface, (
                    button_surfaces[upgrade_list[i]].get_width() -
                    upgrade_amount_surface.get_width() - 10,
                    button_surfaces[upgrade_list[i]].get_height() -
                    upgrade_amount_surface.get_height() -
                    (button_surfaces[upgrade_list[i]].get_height() / 20)
                ))

                # Draw upgrade cost next to score
                cost_surface = score_font.render('-%d' % ml.get_upgrade_cost(upgrade_list[i]),
                                                 True, RED)
                window.blit(cost_surface, (
                    score_surface.get_width() + score_margin + 10,
                    window.get_height() - score_margin - cost_surface.get_height()
                ))

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            # Escape  or space closes the upgrades screen
            elif event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_SPACE):
                    return
            # Check for click on each button
            elif event.type == MOUSEBUTTONUP:
                for i, rect in enumerate(button_rect_list):
                    if rect.collidepoint(event.pos):
                        ml.purchase_upgrade(upgrade_list[i])
                        break
                # noinspection PyArgumentList
                if continue_button_rect.collidepoint(event.pos):
                    return

        # Draw title
        window.blit(upgrades_title, ((window.get_width() / 2) -
                                     (upgrades_title.get_width() / 2),
                                     30))

        # Draw all of the buttons
        for count, button in enumerate(button_surfaces):
            window.blit(button_surfaces[button], button_rect_list[count])
        window.blit(continue_button, continue_button_rect)

        draw_cursor()
        pygame.display.update()
        clock.tick(FPS)


def ask_player_input(message: str, max_length=30) -> str:
    """Asks the player for text input, returns the string."""
    player_name_list = []  # List of single-char unicode Strings
    message_font = pygame.font.Font(ml.font, 40)
    name_font = pygame.font.Font(ml.font, 32)
    message_surface = message_font.render(message, True, WHITE)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                # Cancel if escape (return empty string)
                if event.key == K_ESCAPE:
                    return ''
                # Player done typing, return their name
                elif event.key == K_RETURN:
                    return ''.join(player_name_list)
                # Remove the last character if player hits backspace
                elif event.key == K_BACKSPACE:
                    player_name_list = player_name_list[:-1]
                # Build name from input
                elif len(player_name_list) <= max_length:
                    # Prevent ~ which is delimiter in highscores.txt
                    if event.key < 126 and event.key != 96:
                        player_name_list.append(event.unicode)  # Unicode handles shift

        # Clear screen
        window.fill(BLACK)

        # Draw message and show player input
        window.blit(message_surface, (
            (window.get_width() / 2) - (message_surface.get_width() / 2),
            (window.get_height() / 2) - 200
        ))
        name_surface = name_font.render(''.join(player_name_list), True, WHITE)
        window.blit(name_surface, (
            (window.get_width() / 2) - (name_surface.get_width() / 2),
            (window.get_height() / 2) - 200 + (message_surface.get_height() + 25)
        ))

        draw_cursor()
        pygame.display.update()
        clock.tick(FPS)


def check_for_events():
    """Event handling for player movement."""
    global player_move_up, player_move_left, player_move_down, player_move_right, \
        shift_pressed, mouse_movement_active

    for event in pygame.event.get():  # Any unhandled events are dropped

        if event.type == QUIT:
            terminate()

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                main_menu()
            elif event.key in (K_w, K_UP):
                player_move_up = True
                logging.debug('K_w down')
            elif event.key in (K_a, K_LEFT):
                player_move_left = True
                logging.debug('K_a down')
            elif event.key in (K_s, K_DOWN):
                player_move_down = True
                logging.debug('K_s down')
            elif event.key in (K_d, K_RIGHT):
                player_move_right = True
                logging.debug('K_d down')
            elif event.key in (K_LSHIFT,):
                shift_pressed = True
            elif event.key in (K_SPACE,):
                shift_pressed = False
                player_move_up = False
                player_move_down = False
                player_move_left = False
                player_move_right = False
                upgrade_screen()
            elif event.key in (K_m,):
                mouse_movement_active = not mouse_movement_active
            elif event.key in (K_F1,):
                ml.toggle_fps_display()

            # Debug hotkeys
            if debug:
                if event.key in (K_k,):
                    # Suicide
                    game_over()
                    run_game()
                elif event.key in (K_1,):
                    bosses.StarBurst()
                elif event.key in (K_2,):
                    bosses.Doppelganger()
                elif event.key in (K_3,):
                    bosses.Ring()
                elif event.key in (K_4,):
                    pass
                elif event.key in (K_z,):
                    # Kill all enemies and bullets
                    for enemy in ml.enemy_group.sprites():
                        enemy.damage(9999999999)
                    ml.enemy_bullet_group.empty()

        elif event.type == KEYUP:
            if event.key in (K_w, K_UP):
                player_move_up = False
                logging.debug('K_w up')
            elif event.key in (K_a, K_LEFT):
                player_move_left = False
                logging.debug('K_a up')
            elif event.key in (K_s, K_DOWN):
                player_move_down = False
                logging.debug('K_s up')
            elif event.key in (K_d, K_RIGHT):
                player_move_right = False
                logging.debug('K_d up')
            elif event.key in (K_LSHIFT,):
                shift_pressed = False


if __name__ == '__main__':
    main()
