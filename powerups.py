# My name
# Final project for ECE102
# Started 9/05/2016     Due 12/08/2016
#
# Powerup classes

import math
import os.path
import pygame
import random

from mylibrary import MyLibrary as ml


class PowerUp(pygame.sprite.Sprite):
    spawn_timer = ml.time()

    def __init__(self, start_point, target_point, image_name) -> pygame.sprite.Sprite:
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = start_point
        self.falling_speed = ml.normalize_target_fps(1)
        self.homing_speed = ml.normalize_target_fps(4)
        self.from_spawn_speed = ml.normalize_target_fps(7)
        self.homing_distance = 75
        self.moving_from_spawn = True
        self.target_point = target_point

        # Set up image, rect, and mask
        self.image_path = os.path.join('graphics', image_name)
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = self.x, self.y

        # Add sprite to group
        self.add(ml.powerup_group)

    def update(self):
        self.move()
        self.out_of_bounds()
        self.update_rect()

    def move(self):
        distance = ml.distance_to_point(self.rect.center, ml.player.rect.center)
        if distance < self.homing_distance:
            angle = ml.angle_to_point(self.rect.center, ml.player.rect.center)
            self.x, self.y, _ = ml.move_point(self, ml.player.rect.center,
                                              self.homing_speed, angle, 5)
        elif self.moving_from_spawn:
            if self.x == self.target_point[0] and self.y == self.target_point[1]:
                self.moving_from_spawn = False
            else:
                self.x, self.y, _ = ml.move_point(self, self.target_point,
                                                  self.from_spawn_speed, 0, 360)
        else:
            self.y += self.falling_speed

    def update_rect(self):
        self.rect.center = self.x, self.y

    def out_of_bounds(self):
        if self.x < - 100 or \
                        self.x > ml.window_width + 100 or \
                        self.y < - 100 or \
                        self.y > ml.window_height + 100:
            self.kill()

    @staticmethod
    def spawn_random(start_point):
        if ml.time() - PowerUp.spawn_timer > ml.get_upgrade_values('Powerup Interval'):
            PowerUp.spawn_timer = ml.time()
            powerup = random.randint(0, 4)
            if powerup == 0:
                HomingShots(start_point, start_point)
            elif powerup == 1:
                Shield(start_point, start_point)
            elif powerup == 2:
                Heal(start_point, start_point)
            elif powerup == 3:
                Bomb(start_point, start_point)

    @staticmethod
    def spawn(powerup: str, start_point, radius=0, number=1):
        """powerup must be a string matching the name of the class of the powerup that
        should be spawned. point will be the center of the spawned powerup. If defined, radius
        will cause the powerup to quickly move to a random point within radius of point. number
        controls how many powerups of the given type will be spawned at once."""
        for _ in range(number):
            base_x, base_y = start_point
            angle = random.uniform(0, 2 * math.pi)
            random_radius = random.uniform(-radius, radius)
            target_x = base_x + random_radius * math.cos(angle)
            target_y = base_y + random_radius * math.sin(angle)
            eval(powerup)(start_point, (target_x, target_y))


class Bonus(PowerUp):
    def __init__(self, start_point, target_point) -> PowerUp:
        self.image_name = 'bonus_powerup.png'
        super().__init__(start_point, target_point, self.image_name)


class HomingShots(PowerUp):
    def __init__(self, start_point, target_point) -> PowerUp:
        self.image_name = 'homing_powerup.png'
        super().__init__(start_point, target_point, self.image_name)


class Shield(PowerUp):
    def __init__(self, start_point, target_point) -> PowerUp:
        self.image_name = 'shield_powerup.png'
        super().__init__(start_point, target_point, self.image_name)


class Heal(PowerUp):
    def __init__(self, start_point, target_point) -> PowerUp:
        self.image_name = 'heal_powerup.png'
        super().__init__(start_point, target_point, self.image_name)


class Bomb(PowerUp):
    def __init__(self, start_point, target_point) -> PowerUp:
        self.image_name = 'bomb_powerup.png'
        super().__init__(start_point, target_point, self.image_name)


class ShieldEffect(pygame.sprite.Sprite):
    """Circular shield that follows the player while shield is active
    and deletes enemy bullets that hit it"""

    def __init__(self) -> pygame.sprite.Sprite:
        pygame.sprite.Sprite.__init__(self)
        self.spawn_time = ml.time()
        self.spawn_tick = ml.ticks
        self.duration = ml.get_upgrade_values('Shield Duration')
        self.image_path = os.path.join('graphics', 'shield.png')
        self.image = pygame.image.load(self.image_path)
        self.image_original = pygame.image.load(self.image_path)
        self.shield_mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.add(ml.powerup_effect_group)

        # Animation
        self.animation_duration = 0.2
        self.duration_ticks = ml.get_upgrade_values('Shield Duration') * ml.framerate
        # 1 animation stage per frame
        self.animation_stages = int(ml.framerate * self.animation_duration)
        self.stage_duration = self.animation_duration / self.animation_stages
        self.stage_width = self.image.get_width() / self.animation_stages
        self.stage_height = self.image.get_height() / self.animation_stages
        self.stage_images = []
        for count in range(self.animation_stages):
            self.stage_images.append(pygame.transform.smoothscale(self.image_original,
                (int(self.stage_width * count), int(self.stage_height * count))))
        self.stage = 0
        self.ticks_elapsed = 0

        # Set up bar
        self.bar_image_path = os.path.join('graphics', 'shield_bar.png')
        self.bar_image = pygame.image.load(self.bar_image_path)
        assert self.bar_image.get_width() % 2, 'bar_image width must be odd.'
        self.bar_image_original = self.bar_image
        self.bar_stage_images = [self.bar_image]
        # Create list of bar surfaces with decreasing widths
        for i in range(self.bar_image.get_width() // 2):
            self.bar_stage_images.append(
                    pygame.transform.smoothscale(self.bar_image_original,
                                                 (self.bar_stage_images[i].get_width() - 2,
                                                  self.bar_image.get_height())
                                                 ))
        self.bar_stage_images.append(
                pygame.transform.smoothscale(self.bar_image_original,
                                             (0, self.bar_image.get_height())))
        self.bar_stage_duration = (self.duration * ml.framerate) / \
            len(self.bar_stage_images)
        self.next_bar_image = None
        self.bar = ShieldBar()

    def update(self):
        self.update_duration()
        self.animate()
        self.update_bar()
        self.move()
        self.check_collision()
        self.ticks_elapsed += 1

    def update_bar(self):
        current_frame = int(self.ticks_elapsed // self.bar_stage_duration)
        try:
            # This will raise IndexError during the shield's ending animation
            self.next_bar_image = self.bar_stage_images[current_frame]
        except IndexError:
            pass

        self.bar.update_image(self.next_bar_image)
        self.bar.move()

    def update_duration(self):
        self.duration = ml.get_upgrade_values('Shield Duration')
        self.bar_stage_duration = (self.duration * ml.framerate) / \
            len(self.bar_stage_images)

    def animate(self):
        """Plays the start or end animation based on elapsed time and duration.
        Also kills shield when end animation has finished."""
        if ml.time() - self.spawn_time > self.duration and \
                self.stage > 0:
            self.stage -= 1
            self.image = self.stage_images[self.stage]
        elif ml.time() - self.spawn_time < self.animation_duration and \
                self.stage < len(self.stage_images):
            self.image = self.stage_images[self.stage]
            self.stage += 1
        else:
            self.image = self.image_original
        if self.stage == 0:
            self.bar.kill()
            self.kill()
        self.rect = self.image.get_rect()

    def reset_duration(self):
        if not ml.time() - self.spawn_time > self.duration:
            self.duration = ml.get_upgrade_values('Shield Duration')
        self.spawn_tick = ml.ticks
        self.bar_stage_duration = (ml.get_upgrade_values('Shield Duration') *
                                   ml.framerate) / len(self.bar_stage_images)
        self.ticks_elapsed = 0
        self.spawn_time = ml.time()

    def move(self):
        self.rect.center = ml.player.rect.center

    def check_collision(self):
        # Shield and enemy bullet
        # Check rect collision first
        enemy_bullets_hit = pygame.sprite.spritecollide(self, ml.enemy_bullet_group, False)
        if enemy_bullets_hit:
            for enemy_bullet in enemy_bullets_hit:
                # Check mask collision
                if pygame.sprite.collide_mask(self, enemy_bullet):
                    enemy_bullet.kill()


class ShieldBar(pygame.sprite.Sprite):
    """Bar below the player to show shield duration.
    This is only a separate class so that Sprite handles the blitting
    and collision."""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_path = os.path.join('graphics', 'shield_bar.png')
        self.image = pygame.image.load(self.image_path)
        self.image_original = self.image
        # Game crashes if this doesn't have a mask
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.add(ml.powerup_effect_group)

    def update(self):
        pass

    def update_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()

    def move(self):
        self.rect.centerx = ml.player.rect.centerx
        self.rect.centery = ml.player.rect.bottom
