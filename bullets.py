# My name
# Final project for ECE102
# Started 9/05/2016     Due 12/08/2016
#
# Class for enemy bullets


import math
import pygame
import random

from mylibrary import MyLibrary as ml


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, damage, angle, homing_shots) -> pygame.sprite.Sprite:
        pygame.sprite.Sprite.__init__(self)

        self.move_speed = ml.normalize_target_fps(float(speed))
        self.damage = damage
        self.current_angle = ml.normalize_angle(angle)
        self.angle_r = math.radians(angle)
        self.turning_rate = ml.normalize_target_fps(3.5)
        self.homing = homing_shots

        # Set up image, rect, and mask
        if self.homing:
            self.image = ml.get_bullet_image('homing')
        else:
            self.image = ml.get_bullet_image('player')
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.original_image = self.image
        # self.image = pygame.transform.rotate(self.image, angle)
        self.x = x
        self.y = y
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.x, self.y
        self.mask = pygame.mask.from_surface(self.image)

        # Add sprite to group
        self.add(ml.player_bullet_group)

    def update(self):
        self.move()
        self.update_rect()
        self.out_of_bounds()
        self.check_collision()

    def move(self):
        # Homing shots
        if ml.enemy_group.sprites() and self.homing:
            closest_enemy = ml.closest_sprite_in_group(self, ml.enemy_group)
            if closest_enemy:
                self.x, self.y, self.current_angle = ml.move_point(self,
                                                                   closest_enemy.rect.center,
                                                                   self.move_speed,
                                                                   self.current_angle,
                                                                   self.turning_rate)
            else:
                self.x += self.move_speed * math.cos(math.radians(self.current_angle))
                self.y -= self.move_speed * math.sin(math.radians(self.current_angle))

        # Non-homing shots
        else:
            self.x += self.move_speed * math.cos(math.radians(self.current_angle))
            self.y -= self.move_speed * math.sin(math.radians(self.current_angle))

    def update_rect(self):
        self.rect.center = self.x, self.y

    def out_of_bounds(self):
        if self.x < - 100 or \
                        self.x > ml.window_width + 100 or \
                        self.y < - 100 or \
                        self.y > ml.window_height + 100:
            self.kill()

    def check_collision(self):
        # Check and deal with collision between PlayerBullet and Enemy
        # Check rect collision first
        enemies_hit = pygame.sprite.spritecollide(self, ml.enemy_group, False)
        if enemies_hit:
            for enemy in enemies_hit:
                if not enemy.invincible:
                    # Check mask collision
                    enemy.update_mask()
                    if pygame.sprite.collide_mask(self, enemy):
                        enemy.damage(self.damage)
                        self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, bullet_data, angle) -> pygame.sprite.Sprite:
        pygame.sprite.Sprite.__init__(self)

        self.infinite_explosion = bullet_data.infinite_explosion

        self.original_bullet_data = bullet_data
        self.despawn_range = 200

        self.original_parent = bullet_data.original_parent
        if bullet_data.random_speed != (0, 0):
            a, b = bullet_data.random_speed
            self.move_speed = ml.normalize_target_fps(random.uniform(a, b))
        else:
            self.move_speed = bullet_data.speed
        self.damage = bullet_data.damage
        self.angle = angle  # normalized by FiringData
        self.angle_r = math.radians(angle)
        if bullet_data.random_duration == (0, 0):
            self.duration = bullet_data.duration
        else:
            a, b = bullet_data.random_duration
            self.duration = random.uniform(a, b)
        self.homing_shots_active = bullet_data.homing
        self.turning_rate = bullet_data.turning_rate
        if bullet_data.exploding:
            self.exploding = True
            self.exploding_list = bullet_data.exploding[:]
            self.exploding_bullet_data, self.exploding_firing_data = self.exploding_list[0]
            if not self.infinite_explosion:
                del self.exploding_list[0]
        else:
            self.exploding = False
        self.spawn_time = ml.time()
        self.diag_move_x = self.move_speed * math.cos(math.radians(self.angle))
        self.diag_move_y = self.move_speed * math.sin(math.radians(self.angle))

        # Set up image, rect, and mask
        if bullet_data.homing:
            self.image = ml.get_bullet_image('homing')
        elif bullet_data.exploding:
            self.image = ml.get_bullet_image('exploding')
        else:
            self.image = ml.get_bullet_image('enemy')
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        if bullet_data.coords:
            self.x, self.y = bullet_data.coords
        else:
            self.x, self.y = bullet_data.parent.rect.center
        self.spawn_point = self.x, self.y
        self.spiral = bullet_data.spiral
        self.radial_growth = bullet_data.radial_growth
        self.radius = 0
        self.rect.center = self.x, self.y
        self.mask = pygame.mask.from_surface(self.image, 250)
        self.mask_rect = self.mask.get_bounding_rects()[0]  # Set in get_mask_rect()

        # Add to group
        self.add(ml.enemy_bullet_group)

    def get_damage(self) -> int:
        return self.damage

    def update(self):
        self.check_duration()
        # self.out_of_bounds()
        self.move()
        self.update_rect()

    def move(self):
        if self.homing_shots_active:
            self.x, self.y, self.angle = ml.move_point(self, ml.player.rect.center,
                                                       self.move_speed,
                                                       self.angle,
                                                       self.turning_rate)
        # Spiral shots
        elif self.spiral:
            self.x = self.spawn_point[0] + self.radius * math.cos(math.radians(self.angle))
            self.y = self.spawn_point[1] + self.radius * math.sin(math.radians(self.angle))
            self.radius += self.radial_growth
            self.angle += self.turning_rate
        # Normal shots
        else:
            self.x += self.diag_move_x
            self.y -= self.diag_move_y

    def get_mask_rect(self) -> pygame.Rect:
        """Calculate and return Rect of mask for hitbox collision."""
        return pygame.Rect(self.rect.x + self.mask_rect.x,
                           self.rect.y + self.mask_rect.y,
                           self.mask_rect.width,
                           self.mask_rect.height)

    def update_rect(self):
        self.rect.center = self.x, self.y

    def explode(self):
        self.exploding_firing_data.parent = self
        self.exploding_bullet_data.parent = self
        self.exploding_bullet_data.x, self.exploding_bullet_data.y = self.rect.center
        self.exploding_bullet_data.exploding = self.exploding_list[:]
        self.original_parent.shoot(-500, self.exploding_bullet_data,
                                   self.exploding_firing_data)
        self.kill()

    def check_duration(self):
        if ml.time() - self.spawn_time >= self.duration:
            if self.exploding:
                self.explode()
            self.kill()


class FiringData(object):
    def __init__(self, firing_speed=1, interval=10, angle=None,
                 aim=False, multi=1, random_arc=0,
                 burst=0, burst_delay=0):
        """This class is for storing data to be passed to Enemy.shoot()"""
        self.firing_speed = firing_speed
        self.interval = interval
        self.aim = aim
        self.multi = multi
        self.random_arc = random_arc
        self.burst = burst
        self.burst_delay = burst_delay
        self.angle = angle


class BulletData(object):
    def __init__(self, original_parent, parent=None, coords=None, damage=1, speed=0,
                 random_speed=(0, 0), duration=5, random_duration=(0, 0),
                 homing=False, turning_rate=0, spiral=False, radial_growth=0, exploding=None,
                 infinite_explosion=False):
        """
        This class is for storing data that will be passed to EnemyBullets
        through Enemy.shoot()

        -- coords is a 2-tuple of the coordinates to spawn the bullet at. This should
        usually be the center of the shooting sprite.

        -- random_speed, if defined, will be passed to random.uniform() to determine the
        speed of the bullets, and will override speed.

        -- random_duration, if defined, will be passed to random.uniform() to determine the
        duration of the bullets. random_duration overrides duration.

        -- homing and turning_rate must both be defined for bullets to home on player.

        -- exploding should be a list of tuples: (BulletData, FiringData). Each tuple in the
        list represents one stage of explosion. If infinite_explosion is set to True on both
        the original BulletData and the BulletData of the exploding tuple, the first tuple
        of exploding will be used for every explosion, and it will not stop until the
        bullets are killed by an outside force. Note: infinite_explosion WILL lag unless it is
        either only spawning 1 bullet to replace the one exploding, or if something else is
        killing the bullets.

        -- spiral will set the bullet to spiral mode. In spiral mode, turning_rate will
        determine the speed that the bullet spirals outward from its spawn point. spiral
        overrides homing. radial_growth is the amount that the radius of the spiral will
        increase by each frame.

        """
        self.original_parent = original_parent
        if parent:
            self.parent = parent
        else:
            self.parent = self.original_parent
        self.coords = coords
        self.damage = damage
        self.random_speed = random_speed
        self.speed = ml.normalize_target_fps(speed)
        self.duration = duration
        self.random_duration = random_duration
        self.homing = homing
        self.turning_rate = ml.normalize_target_fps(turning_rate)
        self.exploding = exploding
        self.infinite_explosion = infinite_explosion
        self.spiral = spiral
        self.radial_growth = ml.normalize_target_fps(radial_growth)
