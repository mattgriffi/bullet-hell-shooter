# My name
# Final project for ECE102
# Started 9/05/2016     Due 12/08/2016
#
# Enemy class for inheritance by all enemies
# All enemies are Sprites

import math
import os.path
import powerups
import pygame
import random

from mylibrary import MyLibrary as ml
from bullets import EnemyBullet


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, move_speed, health, collision_damage,
                 image_name, turning_rate=0, current_angle=270, y=0, boss=False,
                 name='') -> pygame.sprite.Sprite:
        pygame.sprite.Sprite.__init__(self)

        self.image_path = os.path.join('graphics', image_name)
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image_original = self.image
        self.move_speed = move_speed
        self.turning_rate = turning_rate
        self.current_angle = ml.normalize_angle(current_angle)
        self.health = health
        self.max_health = health
        self.invincible = False
        self.collision_damage = collision_damage
        self.firing_timer = ml.time() - random.uniform(0, 2.0)
        self.spawn_time = ml.time()
        self.spawn_tick = ml.ticks
        self.is_boss = boss
        self.name = name
        self.phase = 1
        self.num_phases = None
        self.phase_change_time = ml.time()

        # Set up image, rect, and mask
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = x, self.y
        self.mask = pygame.mask.from_surface(self.image)

        # Add sprite to group
        self.add(ml.enemy_group)

        if self.is_boss:
            ml.update_boss_data(self.max_health, self.health, self.name)

    def update(self):
        if self.is_boss:
            self.change_phase()
        self.check_health()
        self.update_rect()
        self.animate()
        self.out_of_bounds()
        self.attack()

    def attack(self):
        pass

    def change_phase(self):
        if self.max_health - self.health > self.phase * (self.max_health / self.num_phases):
            self.phase += 1
            self.phase_change_time = ml.time()
            eval('self.setup_phase' + str(self.phase))()

    def spawn_powerups(self, bonus):
        powerups.PowerUp.spawn('Bonus', self.rect.center,
                               radius=100,
                               number=bonus)
        powerups.PowerUp.spawn('Heal', self.rect.center)

    def setup_phase1(self):
        pass

    def setup_phase2(self):
        pass

    def setup_phase3(self):
        pass

    def setup_phase4(self):
        pass

    def damage(self, damage: int):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        if self.is_boss:
            ml.update_boss_data(self.max_health, self.health, self.name)

    def get_damage(self) -> int:
        return self.collision_damage

    def update_rect(self):
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y

    def animate(self):
        """To be overridden by enemies that need to animate."""
        pass

    def update_mask(self):
        if self.image != self.image_original:
            self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        """If a turning rate is defined, the enemy will home on the player. Otherwise, it will
        move in a straight line at its current angle."""
        if self.turning_rate:
            self.x, self.y, self.current_angle = \
                ml.move_point(self, ml.player.rect.center,
                              self.move_speed,
                              self.current_angle,
                              self.turning_rate)
        else:
            self.x += self.move_speed * math.cos(math.radians(self.current_angle))
            self.y -= self.move_speed * math.sin(math.radians(self.current_angle))

    def out_of_bounds(self):
        if not self.is_boss:
            if self.x > ml.window_width + 100 or \
                            self.x < -self.rect.width - 100 or \
                            self.y > ml.window_height + 100:
                self.kill()

    def check_health(self):
        if self.health <= 0:
            if self.is_boss:
                ml.update_boss_data(self.max_health, 0, self.name)
            self.kill()
            ml.boss_part_group.empty()

    @staticmethod
    def shoot(timer, bullet_data, firing_data, burst_counter=0):
        # TODO clean up shoot() documentation
        """
        All-encompassing method for shooting. Mix and match arguments to achieve desired
        patterns.

        -- timer should be a time from ml.time().
        -- firing_speed limits the rate.
        If the shoot is successful, returns the current ml.time() to reset the timer, otherwise
        returns the original timer.

        -- interval is the angular gap between multi-shot bullets.

        -- angle determines the angle that the bullet is first fired at. If not defined, firing
        angle will be random from 0 to 360. If defined, aim will override angle.

        -- random_arc modifies the angle of the shot by
        random.uniform(-random_arc, random_arc).

        -- burst, if greater than 0, sets method to burst mode. It will shoot a number of
        times equal to burst with burst_delay time between each shot. In burst mode,
        firing_speed acts as the delay, in seconds, between bursts, rather than the number
        of attacks per second. burst_counter keeps track of how far through the burst it has
        gotten. In burst mode, method will return 2 values. The first will be a ml.time().
        If the burst has completed, it will return a new ml.time(), otherwise it will return
        the original timer. The second value will be the incremented counter, or 0 if the
        burst has finished. The new burst counter should be passed back in the next time the
        method is called.

        See enemybullet.BulletData for further documentation.

        Usage:
        self.timer = self.omni_shot(args)

        Burst mode:
        self.timer, self.burst_counter = self.omni_shot(args)

        """
        parent = bullet_data.parent
        firing_speed = firing_data.firing_speed
        interval = firing_data.interval
        aim = firing_data.aim
        multi = firing_data.multi
        random_arc = firing_data.random_arc
        burst = firing_data.burst
        burst_delay = firing_data.burst_delay
        counter = burst_counter
        angle = firing_data.angle

        if burst:

            if aim:
                shot_angle = ml.angle_to_point(parent.rect.center, ml.player.rect.center)
            elif angle is None:
                shot_angle = random.uniform(0, 360)
            else:
                shot_angle = angle

            if counter < burst and ml.time() - timer >= burst_delay:

                shot_angles = ml.multi_shot_angles(multi, shot_angle, interval)
                for arc_shot in range(multi):
                    EnemyBullet(bullet_data,
                                angle=shot_angles[arc_shot] +
                                random.uniform(-random_arc, random_arc)
                                )

                return ml.time(), counter + 1

            else:
                # Reset counter
                if ml.time() - timer >= firing_speed:
                    counter = 0

                return timer, counter

        elif ml.time() - timer >= (1 / firing_speed):

            if aim:
                shot_angle = ml.angle_to_point(parent.rect.center, ml.player.rect.center)
            elif angle is None:
                shot_angle = random.uniform(0, 360)
            else:
                shot_angle = angle

            shot_angles = ml.multi_shot_angles(multi, shot_angle, interval)
            for arc_shot in range(multi):
                EnemyBullet(bullet_data,
                            angle=shot_angles[arc_shot] +
                            random.uniform(-random_arc, random_arc),
                            )

            return ml.time()

        return timer
