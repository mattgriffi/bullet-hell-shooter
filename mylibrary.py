# My name
# Final project for ECE102
# Started 9/05/2016     Due 12/08/2016
#
# My library for miscellaneous functions, data storage/distribution,
# interface drawing, and more.
# I couldn't think of a better name for this module

import collections
import decimal
import math
import operator
import os.path
import pygame


class MyLibrary(object):
    pygame.init()

    player_group = None
    player_bullet_group = None
    enemy_group = None
    enemy_bullet_group = None
    powerup_group = None
    powerup_effect_group = None
    boss_part_group = None

    window = None
    window_width = None
    window_height = None
    clock = None
    ticks = 0
    framerate = 60  # Should be set with set_framerate()
    font = os.path.join('font', 'Orbitron Black.ttf')
    interface_font = pygame.font.Font(font, 24)
    boss_name_font = pygame.font.Font(font, 26)
    health_bar_path = os.path.join('graphics', 'health_bar.png')
    health_bar_empty_path = os.path.join('graphics', "health_bar_empty.png")
    fps_display = False

    player = None
    player_health = None
    health_bar_image = None
    health_bar_empty_image = None
    health_bar_list = None
    health_bar_rect_list = None
    boss_health_bar_image = None
    boss_base_bar_image = None
    boss_name_surface = None
    score_surface = None
    bullets = None
    laser_list = None

    boss_health = 0
    max_boss_health = 0
    boss_name = ''

    score = 0

    # OrderedDict for storing upgrade data
    decimal.getcontext().prec = 5
    upgrades = collections.OrderedDict()
    upgrades['Damage'] = {
        'current':   decimal.Decimal(3).normalize(),
        'default':   decimal.Decimal(3).normalize(),
        'increase':  decimal.Decimal(0.5).normalize(),
        'level':     1,
        'cost':      200,
        'base cost': 200
    }
    upgrades['Attack Speed'] = {
        'current':   decimal.Decimal(2).normalize(),
        'default':   decimal.Decimal(2).normalize(),
        'increase':  decimal.Decimal(0.2).normalize(),
        'level':     1,
        'cost':      200,
        'base cost': 200
    }
    upgrades['Bullet Speed'] = {
        'current':   decimal.Decimal(5).normalize(),
        'default':   decimal.Decimal(5).normalize(),
        'increase':  decimal.Decimal(0.5).normalize(),
        'level':     1,
        'cost':      100,
        'base cost': 100
    }
    upgrades['Multi Shot'] = {
        'current':   3,
        'default':   3,
        'increase':  2,
        'level':     1,
        'cost':      5000,
        'base cost': 5000
    }
    upgrades['Max Health'] = {
        'current':   5,
        'default':   5,
        'increase':  1,
        'level':     1,
        'cost':      300,
        'base cost': 300
    }
    upgrades['Movement Speed'] = {
        'current':   decimal.Decimal(3).normalize(),
        'default':   decimal.Decimal(3).normalize(),
        'increase':  decimal.Decimal(0.2).normalize(),
        'level':     1,
        'cost':      500,
        'base cost': 500
    }
    upgrades['Homing Duration'] = {
        'current':   5,
        'default':   5,
        'increase':  2,
        'level':     2,
        'cost':      200,
        'base cost': 200
    }
    upgrades['Shield Duration'] = {
        'current':   5,
        'default':   5,
        'increase':  2,
        'level':     2,
        'cost':      250,
        'base cost': 250
    }
    upgrades['Bomb Damage'] = {
        'current':   25,
        'default':   25,
        'increase':  25,
        'level':     1,
        'cost':      300,
        'base cost': 300
    }
    upgrades['Powerup Interval'] = {
        'current':   decimal.Decimal(15).normalize(),
        'default':   decimal.Decimal(15).normalize(),
        'increase':  decimal.Decimal(-1).normalize(),
        'level':     1,
        'cost':      300,
        'base cost': 300
    }

    @staticmethod
    def set_score(new_score: int):
        MyLibrary.score = new_score
        MyLibrary.score_surface = MyLibrary.interface_font.render('Score: %d'
                                                        % MyLibrary.score,
                                                        True, (255, 255, 255))

    @staticmethod
    def change_score(change_amount: int):
        MyLibrary.score += change_amount
        MyLibrary.score_surface = MyLibrary.interface_font.render('Score: %d'
                                                        % MyLibrary.score,
                                                        True, (255, 255, 255))

    @staticmethod
    def loading_screen():
        """Draws the text 'loading' to the screen. Stays until screen is cleared."""
        loading_font = pygame.font.Font(MyLibrary.font, 50)
        loading_surface = loading_font.render('Loading...', True,
                                                          (255, 255, 255))
        loading_rect = pygame.Rect((0, 0),
                                   (loading_surface.get_width(), loading_surface.get_height()))
        loading_rect.center = MyLibrary.window_width / 2, MyLibrary.window_height / 2
        MyLibrary.window.blit(loading_surface, loading_rect)

    @staticmethod
    def load_images():
        """This method must be called after the pygame display mode has been set."""
        # Health bars
        MyLibrary.health_bar_image = pygame.image.load(
                MyLibrary.health_bar_path).convert_alpha()
        MyLibrary.health_bar_empty_image = \
            pygame.image.load(MyLibrary.health_bar_empty_path).convert_alpha()
        MyLibrary.boss_health_bar_image_path = os.path.join('graphics', 'boss_health_bar.png')
        MyLibrary.boss_health_bar_image = \
            pygame.image.load(MyLibrary.boss_health_bar_image_path).convert_alpha()
        MyLibrary.boss_base_bar_image = pygame.transform.smoothscale(
                MyLibrary.boss_health_bar_image,
                (
                    MyLibrary.window_width - 50, MyLibrary.health_bar_image.get_height()
                ))
        # Bullets
        homing_bullet_image_path = os.path.join('graphics', 'guy_fieri.png')
        exploding_bullet_image_path = os.path.join('graphics', 'guy_fieri.png')
        enemy_bullet_image_path = os.path.join('graphics', 'guy_fieri.png')
        player_bullet_image_path = os.path.join('graphics', 'guy_fieri.png')

        MyLibrary.bullets = {
            'homing':    pygame.image.load(homing_bullet_image_path).convert_alpha(),
            'exploding': pygame.image.load(exploding_bullet_image_path).convert_alpha(),
            'enemy':     pygame.image.load(enemy_bullet_image_path).convert_alpha(),
            'player':    pygame.image.load(player_bullet_image_path).convert_alpha()
        }
        # Laser beam # TODO make take less RAM
        laser_image_path = os.path.join('graphics', 'laser_blue.png')
        laser_original = pygame.image.load(laser_image_path).convert_alpha()
        MyLibrary.laser_list = [pygame.transform.rotate(laser_original, i / 2)
                      for i in range(0, 360)]

    @staticmethod
    def get_laser_image(angle):
        # TODO load laser image in ML
        a = MyLibrary.normalize_angle(angle - 1)
        if a > 180:
            a -= 180
        laser_angle = int(2 * (a - (a % 0.5)))
        return MyLibrary.laser_list[laser_angle]

    @staticmethod
    def get_bullet_image(bullet_type: str):
        """Returns the proper image for bullets. This prevents images from being loaded
        every time a new bullet is spawned.
        Valid types: homing, exploding, enemy, player """
        return MyLibrary.bullets[bullet_type]

    @staticmethod
    def update_player_health():
        """Updates the player health bar, which is drawn with draw_interface()"""
        # Add filled health bars
        MyLibrary.health_bar_list = \
            [MyLibrary.health_bar_image] * MyLibrary.player.health
        # Fill the rest with empty health bars
        for _ in range(MyLibrary.get_upgrade_values('Max Health') -
                               MyLibrary.player.health):
            MyLibrary.health_bar_list.append(MyLibrary.health_bar_empty_image)
        # Set up Rects for drawing health bars
        first_rect = pygame.Rect(0, 0, MyLibrary.health_bar_image.get_width(),
                                 MyLibrary.health_bar_image.get_height())
        MyLibrary.health_bar_rect_list = [first_rect]
        for i in range(MyLibrary.get_upgrade_values('Max Health')):
            MyLibrary.health_bar_rect_list.append(pygame.Rect(
                    pygame.Rect(MyLibrary.health_bar_rect_list[i].x +
                                MyLibrary.health_bar_image.get_width() - 15,
                                0,
                                MyLibrary.health_bar_image.get_width(),
                                MyLibrary.health_bar_image.get_height())
            ))

    @staticmethod
    def draw_interface(surface):
        """Draws the in game interface, including player health, boss health, boss name, score,
        and fps display. Draws to surface."""

        # Player Health
        for i, health_bar in enumerate(MyLibrary.health_bar_list):
            surface.blit(health_bar, MyLibrary.health_bar_rect_list[i])

        # Boss health
        if MyLibrary.boss_health > 0:
            if MyLibrary.boss_health > 0:
                surface.blit(MyLibrary.boss_health_bar_image, (
                    0 + (MyLibrary.window_width / 2) - (
                        MyLibrary.boss_health_bar_image.get_width() / 2), 50))

        # Boss name
        if MyLibrary.boss_health > 0:
            surface.blit(MyLibrary.boss_name_surface,
                         ((surface.get_width() / 2) -
                          (MyLibrary.boss_name_surface.get_width() / 2),
                          30))

        # Score
        surface.blit(MyLibrary.score_surface, (0, MyLibrary.health_bar_image.get_height() + 5))

        # FPS display
        if MyLibrary.fps_display:
            clock_surface = MyLibrary.interface_font.render('FPS: %.2f'
                                                            % MyLibrary.get_fps(),
                                                            True, (255, 255, 255))
            surface.blit(clock_surface, (0, MyLibrary.health_bar_image.get_height() + 60))

        # Timer display
        if MyLibrary.fps_display:
            timer_surface = MyLibrary.interface_font.render('Time: %.2f' % MyLibrary.time(),
                                                            True, (255, 255, 255))
            surface.blit(timer_surface, (0, MyLibrary.health_bar_image.get_height() + 90))

    @staticmethod
    def update_boss_data(max_health: int, health: int, name: str):
        """Updates the boss health and name. Resizes the boss health bar. This is all drawn
        with draw_interface."""
        MyLibrary.boss_name = name
        MyLibrary.boss_health = health
        # Scale health bar horizontally
        boss_health_bar_width = int(MyLibrary.boss_base_bar_image.get_width() *
                                    (health / max_health))
        MyLibrary.boss_health_bar_image = pygame.transform.smoothscale(
                MyLibrary.boss_base_bar_image, (
                    boss_health_bar_width, MyLibrary.boss_base_bar_image.get_height()
                ))
        MyLibrary.boss_name_surface = MyLibrary.boss_name_font.render(
                str(MyLibrary.boss_name), True,
                (255, 255, 255))

    @staticmethod
    def toggle_fps_display():
        MyLibrary.fps_display = not MyLibrary.fps_display

    @staticmethod
    def add_highscore(name: str, score: int):
        high_scores_file = open('highscores.txt', 'a')
        high_scores_file.write('%s~%d\n' % (name, score))
        high_scores_file.close()

    @staticmethod
    def get_highscores() -> list:
        # Returns a list of name + score lists
        high_scores_file = open('highscores.txt')
        high_scores_list_dirty = high_scores_file.readlines()
        high_scores_file.close()
        high_scores_list_clean = []
        # Split names from scores
        for score in high_scores_list_dirty:
            high_scores_list_clean.append(score.split('~'))
        # Remove newlines
        for i in high_scores_list_clean:
            i[1] = int(i[1].rstrip())
        # Sort descending
        high_scores_list_clean.sort(key=operator.itemgetter(1), reverse=True)

        return high_scores_list_clean

    @staticmethod
    def set_window_data(window):
        MyLibrary.window = window
        MyLibrary.window_width = MyLibrary.window.get_width()
        MyLibrary.window_height = MyLibrary.window.get_height()

    @staticmethod
    def set_fps_clock(clock: pygame.time.Clock):
        MyLibrary.clock = clock

    @staticmethod
    def get_fps() -> float:
        """This returns the current framerate that the game is running at. If the target
        framerate is needed, use MyLibrary.framerate"""
        return MyLibrary.clock.get_fps()

    @staticmethod
    def set_framerate(framerate: int):
        """Set the intended framerate of the game.
        framerate will be passed to pygame.time.Clock whenever
        MyLibrary.tick() is called."""
        MyLibrary.framerate = framerate

    @staticmethod
    def normalize_target_fps(num):
        return num * (60 / MyLibrary.framerate)

    @staticmethod
    def tick():
        """Mirrors the pygame.time.Clock.tick() method. Ticks the pygame.time.Clock at
        framerate while counting total ticks. Calls to pygame.time.Clock's built in tick()
        method will not increase this tick count. This method should not be called from
        menu screens, and should be called exactly once per game loop cycle.
        Set the framerate with set_framerate()
        Set the clock with set_fps_clock() """
        MyLibrary.clock.tick(MyLibrary.framerate)
        MyLibrary.ticks += 1

    @staticmethod
    def time() -> float:
        """Mirrors the time.time() method.
        Returns float representing the virtual time in seconds. Virtual time mimics
        real time, but scales with the FPS. This can be used to tie things
        to framerate instead of epoch time, preventing certain things from running
        relatively faster when the rest of the game is lagging.
        Note: If this method is called more than once per frame, it will return the same
        value every time."""
        return MyLibrary.ticks / MyLibrary.framerate

    @staticmethod
    def get_upgrade_values(upgrade: str):
        return MyLibrary.upgrades[upgrade]['current']

    @staticmethod
    def get_upgrade_amount(upgrade: str):
        return MyLibrary.upgrades[upgrade]['increase']

    @staticmethod
    def get_upgrade_cost(upgrade: str) -> int:
        return MyLibrary.upgrades[upgrade]['cost']

    @staticmethod
    def purchase_upgrade(upgrade: str):
        """If player has enough score, increases upgrade value, level, and cost.
        Removes cost from score."""
        if MyLibrary.score >= MyLibrary.upgrades[upgrade]['cost']:
            MyLibrary.change_score(-MyLibrary.upgrades[upgrade]['cost'])
            MyLibrary.upgrades[upgrade]['current'] += MyLibrary.upgrades[upgrade]['increase']
            MyLibrary.upgrades[upgrade]['level'] += 1
            # Double price each time
            MyLibrary.upgrades[upgrade]['cost'] = \
                int(MyLibrary.upgrades[upgrade]['base cost'] * \
                math.pow(2, MyLibrary.upgrades[upgrade]['level'] - 1))

            if upgrade == 'Max Health':
                MyLibrary.player.damage(-1)
                MyLibrary.update_player_health()

    @staticmethod
    def reset_upgrades():
        """Resets upgrade data to default."""
        for key in MyLibrary.upgrades:
            MyLibrary.upgrades[key]['current'] = MyLibrary.upgrades[key]['default']
            MyLibrary.upgrades[key]['level'] = 1
            MyLibrary.upgrades[key]['cost'] = MyLibrary.upgrades[key]['base cost']

    @staticmethod
    def update_player_data(player):
        """Updates stored player data for use by other modules."""
        MyLibrary.player = player

    @staticmethod
    def set_sprite_groups(player_group, player_bullet_group, enemy_group, enemy_bullet_group,
                          powerup_group, powerup_effect_group, boss_part_group):
        """Gives MyLibrary access to Sprite groups."""
        MyLibrary.player_group = player_group
        MyLibrary.player_bullet_group = player_bullet_group
        MyLibrary.enemy_group = enemy_group
        MyLibrary.enemy_bullet_group = enemy_bullet_group
        MyLibrary.powerup_group = powerup_group
        MyLibrary.powerup_effect_group = powerup_effect_group
        MyLibrary.boss_part_group = boss_part_group

    @staticmethod
    def multi_shot_angles(number_of_shots: int, base_angle: float,
                          angle_increment: float) -> list:
        """Example result with base_angle = 90, angle_increment = 10:
        [90, 100, 80, 110, 70, 120, 60, 130, ...]"""
        shot_angles = [base_angle]
        for i in range(number_of_shots):
            shot_angles.append(shot_angles[i] + ((i + 1) * angle_increment * math.pow(-1, i)))
        return shot_angles

    @staticmethod
    def burst_angles(number_of_shots: int, base_angle: float, angle_increment: float) -> list:
        """Example result with base_angle = 90, angle_increment = 10:
        [90, 100, 110, 120, 130, ...]"""
        return [base_angle + angle_increment * i for i in range(number_of_shots)]

    @staticmethod
    def closest_sprite_in_group(sprite, group,
                                ignore_invincible=True) -> pygame.sprite.Sprite:
        """Returns the Sprite in given group that is closest to given Sprite."""
        target_sprite = None
        shortest_distance = 99999999
        for group_sprite in group.sprites():
            distance_r = MyLibrary.distance_to_point(sprite.rect.center,
                                                     group_sprite.rect.center)
            # Overwrite the stored sprite if one is closer
            if distance_r < shortest_distance and ignore_invincible \
                    and not group_sprite.invincible:
                target_sprite = group_sprite
                shortest_distance = distance_r
            elif distance_r < shortest_distance and not ignore_invincible:
                target_sprite = group_sprite
                shortest_distance = distance_r

        return target_sprite

    @staticmethod
    def get_button_surface(width: int, height: int, text: str,
                           font_size: int, color, y_offset: int = 3) -> pygame.Surface:
        """Returns a button surface with the specified dimensions, text, and color."""
        button_surface = pygame.Surface((width, height))
        button_font = pygame.font.Font(MyLibrary.font, font_size)
        button_surface.fill(color)
        fill_rect = pygame.Rect((2, 2), (width - 4, height - 4))
        button_surface.fill((0, 0, 0), fill_rect)
        button_font_surface = button_font.render(text, True, color)
        button_surface.blit(button_font_surface, (
            (button_surface.get_width() / 2) - (button_font_surface.get_width() / 2),
            (button_surface.get_height() / 2) -
            (button_font_surface.get_height() / 2) + y_offset
        ))
        return button_surface

    @staticmethod
    def distance_to_point(point1: tuple, point2: tuple) -> float:
        """Returns the distance between two points."""
        distance_x = point2[0] - point1[0]
        distance_y = point2[1] - point1[1]
        return math.hypot(distance_x, distance_y)

    @staticmethod
    def angle_to_point(point1: tuple, point2: tuple) -> float:
        distance_x = point2[0] - point1[0]
        distance_y = point2[1] - point1[1]
        angle = math.degrees(math.atan2(-distance_y, distance_x))
        return MyLibrary.normalize_angle(angle)

    @staticmethod
    def normalize_angle(angle: float):
        """angle should be in degrees. Returns the co-terminal angle between 0 and 360."""
        new_angle = angle
        while new_angle < 0:
            new_angle += 360
        while new_angle > 360:
            new_angle -= 360
        return new_angle

    @staticmethod
    def move_curve(x: float, distance: float, func: callable) -> tuple:
        """Moves a point a certain distance along a given curve. func should be a
        mathematical func that takes x as input and returns y. Returns the resulting x,
        y coordinates after the movement as floats. A positive distance moves right, negative
        distance moves left. """
        increment = 0.005
        if distance < 0:
            increment *= -1
        elif distance == 0:
            return x, func(x)
        # Approximate movement along a curve by summing the lengths of line
        # segments with length increment and comparing against given distance
        d_list = []
        next_point_x = x
        next_point = None
        while abs(sum(d_list)) < abs(distance):
            start_x = next_point_x
            start_y = func(start_x)
            new_start = start_x, start_y
            next_point_x = start_x + increment
            next_point_y = func(next_point_x)
            next_point = next_point_x, next_point_y
            segment_length = MyLibrary.distance_to_point(new_start, next_point)
            d_list.append(segment_length)
        return next_point

    @staticmethod
    def move_point(homing_sprite, point: tuple,
                   move_speed: float, current_angle: float, turning_rate: float):
        """Returns a 3-tuple of floats representing the new x, y coordinates and the facing
        angle of homing_sprite after calculating movement toward point. If
        turning_rate is 360 or greater, turning speed will be infinite. If turning_rate is
        0, the sprite will move in a straight line at current_angle. """
        distance_r = MyLibrary.distance_to_point(homing_sprite.rect.center, point)
        target_angle = MyLibrary.angle_to_point(homing_sprite.rect.center, point)

        if turning_rate >= 360 and distance_r <= move_speed:
            return point[0], point[1], target_angle

        new_angle = current_angle

        # Turn toward the player (this took 2.5 hours to come up with)
        if abs(current_angle - target_angle) <= turning_rate:
            new_angle = target_angle
        elif turning_rate != 0:
            if target_angle < current_angle - 180:
                new_angle = current_angle + turning_rate
            elif target_angle > current_angle + 180:
                new_angle = current_angle - turning_rate
            elif target_angle > current_angle:
                new_angle = current_angle + turning_rate
            elif target_angle < current_angle:
                new_angle = current_angle - turning_rate

        # Move
        new_x = homing_sprite.x + (move_speed * math.cos(math.radians(new_angle)))
        new_y = homing_sprite.y - (move_speed * math.sin(math.radians(new_angle)))
        return new_x, new_y, MyLibrary.normalize_angle(new_angle)

    @staticmethod
    def bounce_angle():
        """Returns the new angle of a projectile that has bounced off of a circle."""
        # TODO implement bounce_angle()
        # This works for a bullet bouncing off the outside of a stationary circle
        # All angles are with respect to x-axis and in degrees
        # a = angle from center of circle to point of collision
        # b = angle of movement of a projectile when it hits the circle
        # bounce_angle = 2a - b - 180
        pass
