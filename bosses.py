# My name
# Final project for ECE102
# Started 9/05/2016     Due 12/08/2016
#
# Variety of enemy classes
# Enemy inherits pygame.sprite.Sprite

import enemy
import math
import os.path
import pygame

from bullets import BulletData, FiringData
from mylibrary import MyLibrary as ml

base_powerup_spawn = 5
starburst_health = 750
doppelganger_health = 600
ring_health = 750

class StarBurst(enemy.Enemy):
    def __init__(self) -> pygame.sprite.Sprite:
        # General data
        self.image_name = 'boss1.png'
        self.invisible_image_path = os.path.join('graphics', 'boss_invisible.png')
        self.boss_invisible_image = \
            pygame.image.load(self.invisible_image_path).convert_alpha()
        self.health = starburst_health
        self.collision_damage = 2
        self.move_speed = ml.normalize_target_fps(0)
        self.max_speed = ml.normalize_target_fps(3.5)
        self.turning_rate = ml.normalize_target_fps(0)
        self.max_turning_rate = ml.normalize_target_fps(1.4)

        self.name = 'Star Burst'

        super().__init__(ml.window_width / 2, self.move_speed, self.health,
                         self.collision_damage,
                         self.image_name, turning_rate=self.turning_rate,
                         y=350, boss=True, name=self.name)

        # Animation data
        self.rotation_angle = 0
        self.rotation_rate = ml.normalize_target_fps(0.5)

        # Phase data
        self.phase = 1
        self.phase_change_time = ml.time() - 2
        self.phase_change_delay = 5
        # These methods are called depending on the boss's current phase
        self.phase_method_list = [self.phase1, self.phase2, self.phase3, self.phase4]
        self.num_phases = len(self.phase_method_list)

        # Shooting data
        self.circle_timer = ml.time()
        self.circle_bd = BulletData(self, speed=2, duration=5.2)
        self.circle_fd = FiringData(aim=True, multi=36)
        self.ring_bd = BulletData(self, speed=4)
        self.ring_firing_speed = 30
        self.ring_fd = FiringData(firing_speed=self.ring_firing_speed, interval=180, multi=2,
                                  angle=0)
        self.ring_timer = ml.time()
        self.spiral_bd = BulletData(self, spiral=True, radial_growth=2.5,
                                    turning_rate=0.5)
        self.spiral_fd = FiringData(multi=18, interval=20)
        self.spiral_timer = ml.time()
        self.explode_shot_timer = ml.time()
        self.explode_bd = [(BulletData(self, speed=3),
                            FiringData(multi=36))]
        self.explode_shot_bd = BulletData(self, damage=2, speed=2,
                                          random_duration=(1.5, 3), exploding=self.explode_bd)
        self.explode_shot_fd = FiringData(firing_speed=0.5)
        self.circle_random_bd = BulletData(self, random_speed=(1, 5), duration=10)
        self.circle_random_fd = FiringData(firing_speed=15)
        self.circle_random_timer = ml.time()

    def update(self):
        # Call the appropriate method for each phase
        if ml.time() - self.phase_change_time > self.phase_change_delay:
            self.phase_method_list[self.phase - 1]()

        super().update()

    def setup_phase2(self):
        self.spawn_powerups(base_powerup_spawn)

    def setup_phase3(self):
        self.spawn_powerups(base_powerup_spawn * 2)

    def setup_phase4(self):
        self.spawn_powerups(base_powerup_spawn * 3)

    def kill(self):
        self.spawn_powerups(base_powerup_spawn * 4)
        super().kill()

    def phase1(self):
        self.circle_timer = self.shoot(self.circle_timer, self.circle_bd, self.circle_fd)
        if ml.time() - self.ring_timer >= 1 / self.ring_firing_speed:
            self.ring_fd.angle += 10
        self.ring_timer = self.shoot(self.ring_timer, self.ring_bd, self.ring_fd)

    def phase2(self):
        if ml.time() - self.spiral_timer >= self.spiral_fd.firing_speed:
            self.spiral_bd.turning_rate *= -1
        self.rotation_rate = ml.normalize_target_fps(1.5)
        self.spiral_timer = self.shoot(self.spiral_timer, self.spiral_bd, self.spiral_fd)
        self.explode_shot_timer = self.shoot(self.explode_shot_timer, self.explode_shot_bd,
                                             self.explode_shot_fd)

    def phase3(self):
        self.rotation_rate = ml.normalize_target_fps(3.5)
        self.explode_shot_fd.firing_speed = 3
        self.explode_shot_timer = self.shoot(self.explode_shot_timer, self.explode_shot_bd,
                                             self.explode_shot_fd)

    def phase4(self):
        self.rotation_rate = ml.normalize_target_fps(6)

        if self.move_speed >= self.max_speed:
            self.move_speed = self.max_speed
        else:
            self.move_speed += ml.normalize_target_fps(0.015)

        if self.turning_rate >= self.max_turning_rate:
            self.turning_rate = self.max_turning_rate
        else:
            self.turning_rate += ml.normalize_target_fps(0.005)

        self.circle_random_timer = self.shoot(self.circle_random_timer, self.circle_random_bd,
                                              self.circle_random_fd)
        self.move()

    def animate(self):
        start_rect_center = self.rect.center
        self.rotation_angle += self.rotation_rate
        self.rotation_angle = ml.normalize_angle(self.rotation_angle)

        if ml.time() - self.phase_change_time < self.phase_change_delay:
            self.invincible = True
            self.image = pygame.transform.rotate(self.boss_invisible_image,
                                                 self.rotation_angle)
        else:
            self.invincible = False
            self.image = pygame.transform.rotate(self.image_original, self.rotation_angle)

        self.rect = self.image.get_rect()
        self.rect.center = start_rect_center


class Doppelganger(enemy.Enemy):
    def __init__(self) -> pygame.sprite.Sprite:
        # General data
        self.image_name = 'enemy_clone.png'
        self.invisible_image_path = os.path.join('graphics', 'enemy_clone_invisible.png')
        self.boss_invisible_image = \
            pygame.image.load(self.invisible_image_path).convert_alpha()
        self.health = doppelganger_health
        self.collision_damage = 1
        self.move_speed = ml.normalize_target_fps(0)
        self.turning_rate = ml.normalize_target_fps(2)
        self.base_turning_rate = ml.normalize_target_fps(2)

        self.name = 'Doppelganger'

        super().__init__(ml.window_width / 2, self.move_speed, self.health,
                         self.collision_damage,
                         self.image_name, turning_rate=self.turning_rate,
                         y=300, boss=True, name=self.name)

        # Phase data
        self.phase_change_time = ml.time() - 2
        self.phase_change_delay = 5
        # Phase 4
        self.moving_x = True
        self.moving_y = False
        self.circle_bd = BulletData(self, speed=2.5, duration=8)
        self.circle_fd = FiringData(aim=True, multi=36)
        # Phase 3
        self.move_speed_scale = ml.normalize_target_fps(800)
        self.min_move_speed = ml.normalize_target_fps(3)
        self.max_move_speed = ml.normalize_target_fps(13)
        self.movement_angle = self.current_angle
        # Phase 2
        self.phase2_bd = None
        self.phase2_fd = FiringData(firing_speed=1.2, aim=True, multi=3)
        self.phase2_timer = ml.time()
        self.phase2spread_bd = BulletData(self, speed=4)
        self.phase2spread_fd = FiringData(firing_speed=0.7, interval=8, aim=True, multi=9)
        self.phase2spread_timer = ml.time()
        self.phase2arc_bd = BulletData(self, speed=3)
        self.phase2arc_fd = FiringData(firing_speed=0.7,
                                       angle=None, burst=9, burst_delay=0.1)
        self.phase2arc_timer = ml.time()
        self.phase2arc_counter = 0
        self.phase2arc2_timer = ml.time()
        self.phase2arc2_counter = 0
        # Phase 1
        self.phase1homing_bd = BulletData(self, speed=5, duration=7, homing=True,
                                          turning_rate=1.7)
        self.phase1homing_fd = FiringData(firing_speed=0.15, interval=180, angle=0, multi=2)
        self.phase1homing_timer = ml.time()
        self.phase1_timer = ml.time()
        self.phase1explode_bd = BulletData(self, speed=10)
        self.phase1explode_fd = FiringData(interval=180, angle=0, multi=2)
        self.phase1explode = [(self.phase1explode_bd, self.phase1explode_fd)]
        self.phase1_bd = None
        self.phase1_fd = None

        # These methods are called depending on the boss's current phase
        self.phase_method_list = [self.phase1, self.phase2, self.phase3, self.phase4]
        self.num_phases = len(self.phase_method_list)

        # Shooting data
        self.mine_timer = ml.time()
        self.mine_explosion_bd = BulletData(self, speed=5)
        self.mine_explosion_fd = FiringData(interval=36, angle=45, multi=10, aim=True)
        self.mine_explosion_data = (self.mine_explosion_bd, self.mine_explosion_fd)
        self.mine_bd = BulletData(self, duration=2, damage=2,
                                  exploding=[self.mine_explosion_data])
        self.mine_fd = FiringData()

        self.test_timer = ml.time()

    def update(self):
        # Call the appropriate method for each phase
        if ml.time() - self.phase_change_time > self.phase_change_delay:
            self.phase_method_list[self.phase - 1]()

        super().update()

    def setup_phase2(self):
        self.spawn_powerups(base_powerup_spawn * 3)

    def setup_phase3(self):
        self.spawn_powerups(base_powerup_spawn * 4)

    def setup_phase4(self):
        self.spawn_powerups(base_powerup_spawn * 5)

    def kill(self):
        self.spawn_powerups(base_powerup_spawn * 6)
        super().kill()

    def phase2(self):
        # Mirror player movement
        rotation_rate = 15
        if not self.current_angle % rotation_rate:
            self.current_angle -= self.current_angle % rotation_rate
        mirror_point = ml.player.rect.centerx * -1 + ml.window_width, \
            ml.player.rect.centery * -1 + ml.window_height
        self.x, self.y, _ = ml.move_point(self, mirror_point, 20, 0, 360)
        # Rotate if player moves above/below
        if self.y > ml.player.rect.centery:
            if self.current_angle != 90 and self.x > ml.player.rect.centerx:
                self.current_angle -= rotation_rate
            elif self.current_angle != 90 and self.x < ml.player.rect.centerx:
                self.current_angle += rotation_rate
        else:
            if self.current_angle != 270 and self.x > ml.player.rect.centerx:
                self.current_angle += rotation_rate
            elif self.current_angle != 270 and self.x < ml.player.rect.centerx:
                self.current_angle -= rotation_rate

        # Shoot
        self.phase1homing_timer = self.shoot(self.phase1homing_timer, self.phase1homing_bd,
                                             self.phase1homing_fd)
        bullet_speed = 7
        distance = abs(ml.player.rect.centery - self.rect.centery)
        duration_f = distance / bullet_speed
        duration_s = duration_f / ml.normalize_target_fps(60)
        self.phase1_bd = BulletData(self, speed=bullet_speed, duration=duration_s,
                                    exploding=self.phase1explode)
        self.phase1_fd = FiringData(firing_speed=2, angle=self.current_angle)

        self.phase1_timer = self.shoot(self.phase1_timer, self.phase1_bd, self.phase1_fd)

    def phase3(self):
        self.turning_rate = ml.normalize_target_fps(10)
        # Match the player's speed
        self.move_speed = ml.normalize_target_fps(
                float(ml.get_upgrade_values('Movement Speed')) - 1)
        # Keep the boss positioned above the player
        above_player = (ml.player.rect.centerx, ml.player.rect.centery - 350)
        self.x, self.y, self.movement_angle = ml.move_point(self, above_player,
                                                            self.move_speed,
                                                            self.movement_angle,
                                                            self.turning_rate)
        # Keep boss on screen
        if self.rect.centery < 0:
            self.y = 0
        # Face the player
        self.current_angle = ml.angle_to_point(self.rect.center, ml.player.rect.center)

        # Shoot
        self.phase2_bd = BulletData(self, coords=self.rect.center, speed=7)
        self.phase2_timer = self.shoot(self.phase2_timer, self.phase2_bd, self.phase2_fd)
        self.phase2spread_timer = self.shoot(self.phase2spread_timer, self.phase2spread_bd,
                                             self.phase2spread_fd)
        # Left arc
        self.phase2arc_bd.coords = self.rect.midleft
        self.phase2arc_fd.angle = ml.burst_angles(20, 180, 10)[self.phase2arc_counter]
        self.phase2arc_timer, self.phase2arc_counter = \
            self.shoot(self.phase2arc_timer, self.phase2arc_bd, self.phase2arc_fd,
                       self.phase2arc_counter)
        # Right arc
        self.phase2arc_bd.coords = self.rect.midright
        self.phase2arc_fd.angle = ml.burst_angles(20, 0, -10)[self.phase2arc2_counter]
        self.phase2arc2_timer, self.phase2arc2_counter = \
            self.shoot(self.phase2arc2_timer, self.phase2arc_bd, self.phase2arc_fd,
                       self.phase2arc2_counter)

    def phase4(self):
        # Scale speed with distance
        # move_speed_scale reduces the effect of distance, causing acceleration sooner
        distance = ml.distance_to_point(self.rect.center, ml.player.rect.center)
        try:
            self.move_speed = self.move_speed_scale / distance
        except ZeroDivisionError:
            pass
        if self.move_speed > self.max_move_speed:
            self.move_speed = self.max_move_speed
        elif self.move_speed < self.min_move_speed:
            self.move_speed = self.min_move_speed
        # Scale turning_rate with move_speed
        self.base_turning_rate = 4
        self.turning_rate = self.base_turning_rate * \
            (self.min_move_speed / self.move_speed)

        # Drop mines
        self.mine_timer = self.shoot(self.mine_timer, self.mine_bd, self.mine_fd)

        # Move
        self.move()

    def phase1(self):
        self.move_speed = 2
        # After y is lined up, turn toward player and starting moving on the y axis
        if self.moving_x and \
                abs(self.x - ml.player.rect.centerx) <= \
                self.move_speed + float(ml.get_upgrade_values('Movement Speed')):
            self.moving_x = False
            self.moving_y = True
            _ = self.shoot(-999, self.circle_bd, self.circle_fd)
        # After x is lined up, turn toward player and starting moving on the x axis
        if self.moving_y and \
                abs(self.y - ml.player.rect.centery) <= \
                self.move_speed + float(ml.get_upgrade_values('Movement Speed')):
            self.moving_x = True
            self.moving_y = False
            _ = self.shoot(-999, self.circle_bd, self.circle_fd)
        # Move until self.x lines up with player's x
        if self.rect.centerx != ml.player.rect.centerx and self.moving_x:
            self.x, self.y, self.current_angle = ml.move_point(self, (
                ml.player.rect.centerx, self.rect.centery
            ), self.move_speed, 0, 360)
        else:
            self.moving_x = False
            self.moving_y = True
        # Move until self.y lines up with player's y
        if self.rect.centery != ml.player.rect.centery and self.moving_y:
            self.x, self.y, self.current_angle = ml.move_point(self, (
                self.rect.centerx, ml.player.rect.centery
            ), self.move_speed, 0, 360)
        else:
            self.moving_x = True
            self.moving_y = False

    def animate(self):
        start_rect_center = self.rect.center
        self.current_angle = ml.normalize_angle(self.current_angle)

        if ml.time() - self.phase_change_time < self.phase_change_delay:
            self.invincible = True
            self.image = pygame.transform.rotate(self.boss_invisible_image,
                                                 self.current_angle)
        else:
            self.invincible = False
            self.image = pygame.transform.rotate(self.image_original, self.current_angle)

        self.rect = self.image.get_rect()
        self.rect.center = start_rect_center


class Ring(enemy.Enemy):
    def __init__(self) -> pygame.sprite.Sprite:
        # General data
        self.image_name = 'ring.png'
        self.invisible_image_path = os.path.join('graphics', 'ring_invisible.png')
        self.boss_invisible_image = \
            pygame.image.load(self.invisible_image_path).convert_alpha()
        self.health = ring_health
        self.collision_damage = 1
        self.move_speed = ml.normalize_target_fps(0)
        self.turning_rate = ml.normalize_target_fps(2)
        self.base_turning_rate = ml.normalize_target_fps(2)

        self.name = 'Ring'

        super().__init__(ml.window_width / 2, self.move_speed, self.health,
                         self.collision_damage,
                         self.image_name, turning_rate=self.turning_rate,
                         y=300, boss=True, name=self.name)

        # Spawn parts (in draw order)
        self.ring1 = BossPart('ring1_red.png')
        self.ring2 = BossPart('ring2_red.png')
        self.part_color = 'red'

        # Phase data
        self.phase_change_time = ml.time() - 2
        self.phase_change_delay = 5
        self.phase1_delay = self.phase_change_delay - 2
        self.circle_angle = 90
        # self.shield_radius = (self.shield.get_mask_rect().width / 2) - 6

        # Phase 1
        phase1_firing_speed = 1
        self.phase1bd = BulletData(self, speed=4)
        # angle will be modified in phase1()
        self.phase1fd = FiringData(firing_speed=phase1_firing_speed, multi=9)
        self.phase1timer1 = ml.time() + self.phase1_delay
        self.phase1timer2 = ml.time() + self.phase1_delay
        self.phase1timer3 = ml.time() + self.phase1_delay + (1 / (2 * phase1_firing_speed))
        self.phase1timer4 = ml.time() + self.phase1_delay + (1 / (2 * phase1_firing_speed))
        # Phase 2
        self.phase2exbd = BulletData(self, speed=5, random_duration=(1.2, 1.5),
                                     infinite_explosion=True)
        self.phase2exfd = FiringData(aim=True)
        self.phase2ex = [(self.phase2exbd, self.phase2exfd)]
        self.phase2bd = BulletData(self, speed=3, duration=2, exploding=self.phase2ex,
                                   infinite_explosion=True)
        self.phase2fd = FiringData(firing_speed=0.2, aim=True)
        self.phase2timer = ml.time()
        self.shot_alive = False
        # Fake exploding data to make the bullets orange
        self.fakebd = BulletData(self, duration=0)
        self.fakefd = FiringData()
        self.fakeex = [(self.fakebd, self.fakefd)]
        self.phase2minionbd = BulletData(self, duration=0.5, turning_rate=6,
                                         spiral=True, radial_growth=3, exploding=self.fakeex)
        self.phase2minionfd = FiringData(firing_speed=5, interval=45, multi=8, aim=True)
        self.phase2minion_timer = ml.time()
        # Phase 3
        self.phase3exbd = BulletData(self, speed=8, homing=True, turning_rate=0.6)
        self.phase3exfd = FiringData(aim=True)
        self.phase3ex = [(self.phase3exbd, self.phase3exfd)]
        self.phase3bd = BulletData(self, speed=6, duration=0.4, exploding=self.phase3ex)
        self.phase3fd = FiringData(firing_speed=0.6, multi=5, interval=35)
        self.phase3timer = ml.time()
        self.phase3minionbd1 = BulletData(self, speed=5, homing=True, turning_rate=0.4)
        self.phase3minionbd2 = BulletData(self, speed=5, homing=True, turning_rate=0.4)
        self.phase3minionfd = FiringData(firing_speed=0.5, aim=True)
        self.phase3miniontimer1 = ml.time()
        self.phase3miniontimer2 = ml.time()
        # Phase 4
        self.laser_damage = 2

        # These methods are called depending on the boss's current phase
        self.phase_method_list = [self.phase1, self.phase2, self.phase3, self.phase4]
        self.num_phases = len(self.phase_method_list)

        self.test_timer = ml.time()

    def update(self):
        # Call the appropriate method for each phase
        if ml.time() - self.phase_change_time > self.phase_change_delay:
            self.phase_method_list[self.phase - 1]()

        super().update()

        # animate_parts() must be called after super().update() to ensure proper coords
        self.animate_parts()

    def phase1(self):
        angle = 270  # ml.angle_to_point(self.rect.center, ml.player.rect.center)
        self.x, self.y, _ = ml.move_point(self, ml.player.rect.center, 1, 0, 360)
        self.phase1fd.angle = angle
        self.phase1timer1 = self.shoot(self.phase1timer1, self.phase1bd, self.phase1fd)
        self.phase1fd.angle = angle + 180
        self.phase1timer2 = self.shoot(self.phase1timer2, self.phase1bd, self.phase1fd)
        self.phase1fd.angle = angle + 90
        self.phase1timer3 = self.shoot(self.phase1timer3, self.phase1bd, self.phase1fd)
        self.phase1fd.angle = angle - 90
        self.phase1timer4 = self.shoot(self.phase1timer4, self.phase1bd, self.phase1fd)

    def setup_phase2(self):
        # Minion 1
        self.minion1 = BossPart('mini_ring.png')
        self.minion1part = BossPart('mini_ring_orange.png')
        self.minion1.x, self.minion1.y = self.rect.centerx, self.rect.centery - 100
        self.minion1.move((self.minion1.x, self.minion1.y))
        self.minion1part.move((self.minion1.x, self.minion1.y))
        self.phase2minionbd.parent = self.minion1
        self.minion1.current_angle = ml.angle_to_point(self.rect.center,
                                                       ml.player.rect.center) + 180

        self.spawn_powerups(base_powerup_spawn * 5)

    def phase2(self):
        # Move boss and shoot
        self.x, self.y, _ = ml.move_point(self, ml.player.rect.center, 0.7, 0, 360)
        self.phase2timer = self.shoot(self.phase2timer, self.phase2bd, self.phase2fd)

        # Control minion
        self.minion1.x, self.minion1.y, self.minion1.current_angle =\
            ml.move_point(self.minion1, ml.player.rect.center, 7,
                          self.minion1.current_angle, 0.8)
        self.minion1part.animate(angle_change=15)
        self.minion1part.x, self.minion1part.y = self.minion1.x, self.minion1.y
        self.phase2minion_timer = self.shoot(self.phase2minion_timer, self.phase2minionbd,
                                             self.phase2minionfd)
        # Bounce off walls
        if self.minion1.rect.left < 0:
            self.minion1.rect.left = 0
            self.minion1.x = self.minion1.rect.centerx
            self.minion1.current_angle = 180 - self.minion1.current_angle
        elif self.minion1.rect.right > ml.window_width:
            self.minion1.rect.right = ml.window_width
            self.minion1.x = self.minion1.rect.centerx
            self.minion1.current_angle = 180 - self.minion1.current_angle
        elif self.minion1.rect.top < 0:
            self.minion1.rect.top = 0
            self.minion1.y = self.minion1.rect.centery
            self.minion1.current_angle = 360 - self.minion1.current_angle
        elif self.minion1.rect.bottom > ml.window_height:
            self.minion1.rect.bottom = ml.window_height
            self.minion1.y = self.minion1.rect.centery
            self.minion1.current_angle = 360 - self.minion1.current_angle
        self.minion1.current_angle = ml.normalize_angle(self.minion1.current_angle)

    def setup_phase3(self):
        ml.enemy_bullet_group.empty()
        self.minion1.kill()
        self.minion1part.kill()
        self.circle_angle = 90
        self.circle_angle_change = 0.8
        self.minion_angle = 0
        self.phase3miniontimer1 = ml.time() + self.phase_change_delay
        self.phase3miniontimer2 = ml.time() + self.phase_change_delay + 0.3
        # Minion 2
        self.minion2 = BossPart('mini_ring.png')
        self.minion2part = BossPart('mini_ring_purple.png')
        self.minion2.x, self.minion2.y = self.rect.centerx - 100, self.rect.centery
        self.minion2.move((self.minion2.x, self.minion2.y))
        self.minion2part.move((self.minion2.x, self.minion2.y))
        self.phase3minionbd1.parent = self.minion2
        # Minion 3
        self.minion3 = BossPart('mini_ring.png')
        self.minion3part = BossPart('mini_ring_purple.png')
        self.minion3.x, self.minion3.y = self.rect.centerx + 100, self.rect.centery
        self.minion3.move((self.minion3.x, self.minion3.y))
        self.minion3part.move((self.minion3.x, self.minion3.y))
        self.phase3minionbd2.parent = self.minion3

        self.spawn_powerups(base_powerup_spawn * 6)

    def phase3(self):
        # Move boss in semicircle around player
        radius = 350
        self.circle_angle += self.circle_angle_change
        circle_x = ml.player.rect.centerx + radius * math.cos(math.radians(self.circle_angle))
        circle_y = ml.player.rect.centery - radius * math.sin(math.radians(self.circle_angle))
        target_point = circle_x, circle_y
        if not 30 < self.circle_angle < 150:
            self.circle_angle_change *= -1
        self.x, self.y, _ = ml.move_point(self, target_point, 20, 0, 360)

        # Boss shoot
        self.phase3fd.angle = self.circle_angle
        self.phase3timer = self.shoot(self.phase3timer, self.phase3bd, self.phase3fd)

        # Minion control
        self.minion2part.animate(angle_change=15)
        self.minion3part.animate(angle_change=15)
        self.minion_angle = ml.normalize_angle(self.minion_angle + 1)
        radius = 200
        circle_x = ml.player.rect.centerx + radius * math.cos(math.radians(self.minion_angle))
        circle_y = ml.player.rect.centery - radius * math.sin(math.radians(self.minion_angle))
        minion2_point = circle_x, circle_y
        angle = self.minion_angle + 180
        circle_x = ml.player.rect.centerx + radius * math.cos(math.radians(angle))
        circle_y = ml.player.rect.centery - radius * math.sin(math.radians(angle))
        minion3_point = circle_x, circle_y
        self.minion2.x, self.minion2.y, _ = ml.move_point(self.minion2, minion2_point,
                                                          20, 0, 360)
        self.minion3.x, self.minion3.y, _ = ml.move_point(self.minion3, minion3_point,
                                                          20, 0, 360)
        self.minion2part.move((self.minion2.x, self.minion2.y))
        self.minion3part.move((self.minion3.x, self.minion3.y))
        self.phase3miniontimer1 = self.shoot(self.phase3miniontimer1, self.phase3minionbd1,
                                             self.phase3minionfd)
        self.phase3miniontimer2 = self.shoot(self.phase3miniontimer2, self.phase3minionbd2,
                                             self.phase3minionfd)
        
    def setup_phase4(self):
        self.minion3.kill()
        self.minion3part.kill()
        self.laser = BossPart('laser_blue.png')
        self.laser.y = -1000
        
        self.minion1.add(ml.boss_part_group)
        self.minion1part.add(ml.boss_part_group)
        self.minion1.move((self.rect.centerx, self.rect.centery - 100))
        self.minion1part.move((self.rect.centerx, self.rect.centery - 100))
        self.minion2.move((self.rect.centerx - 100, self.rect.centery))
        self.minion2part.move((self.rect.centerx - 100, self.rect.centery))
        self.minion3 = BossPart('mini_ring.png')
        self.minion3part = BossPart('mini_ring_red.png')
        self.minion3.move((self.rect.centerx + 100, self.rect.centery))
        self.minion3part.move((self.rect.centerx + 100, self.rect.centery))

        self.phase1fd.multi = 6
        self.phase1fd.interval = 15
        self.phase1fd.firing_speed = 0.5
        self.phase1bd.parent = self.minion3
        self.phase1bd.speed = 3.5
        self.phase1timer1 = ml.time() + self.phase_change_delay
        self.phase1timer2 = ml.time() + self.phase_change_delay
        self.phase1timer3 = ml.time() + self.phase_change_delay + (1 / (2 * 0.5))
        self.phase1timer4 = ml.time() + self.phase_change_delay + (1 / (2 * 0.5))

        self.phase2minionbd.parent = self.minion1
        self.minion1.current_angle = ml.angle_to_point(self.rect.center,
                                                       ml.player.rect.center) + 180

        self.minion_angle = 90
        self.phase3minionbd1.turning_rate = 0.9

        self.spawn_powerups(base_powerup_spawn * 7)

    def phase4(self):
        # Move boss in circle around center of window
        window_center = ml.window_width / 2, ml.window_height / 2
        radius = 200
        self.circle_angle += 0.5
        circle_x = ml.window_width / 2 + \
                   radius * math.cos(math.radians(self.circle_angle))
        circle_y = ml.window_height / 2 + \
                   radius * math.sin(math.radians(self.circle_angle))
        target_point = circle_x, circle_y
        self.x, self.y, _ = ml.move_point(self, target_point, 999, 0, 360)
        # Laser
        self.laser.change_image(image=ml.get_laser_image(ml.angle_to_point(self.rect.center,
                                                                           window_center)))
        self.laser.move(window_center)
        if ml.time() - self.phase_change_time > self.phase_change_delay + 2:
            self.collide_parts()
        
        # Minions
        self.minion1part.animate(angle_change=15)
        self.minion2part.animate(angle_change=15)
        self.minion3part.animate(angle_change=15)
        # minion3
        self.minion3.x, self.minion3.y, _ = ml.move_point(self.minion3, ml.player.rect.center,
                                                          1, 0, 360)
        self.phase1fd.angle = 0
        self.phase1timer1 = self.shoot(self.phase1timer1, self.phase1bd, self.phase1fd)
        self.phase1fd.angle = 180
        self.phase1timer2 = self.shoot(self.phase1timer2, self.phase1bd, self.phase1fd)
        self.phase1fd.angle = 90
        self.phase1timer3 = self.shoot(self.phase1timer3, self.phase1bd, self.phase1fd)
        self.phase1fd.angle = 270
        self.phase1timer4 = self.shoot(self.phase1timer4, self.phase1bd, self.phase1fd)
        # minion1
        self.minion1.x, self.minion1.y, self.minion1.current_angle = \
            ml.move_point(self.minion1, ml.player.rect.center, 5,
                          self.minion1.current_angle, 0.5)
        self.phase2minion_timer = self.shoot(self.phase2minion_timer, self.phase2minionbd,
                                             self.phase2minionfd)
        # Bounce off walls
        if self.minion1.rect.left < 0:
            self.minion1.rect.left = 0
            self.minion1.x = self.minion1.rect.centerx
            self.minion1.current_angle = 180 - self.minion1.current_angle
        elif self.minion1.rect.right > ml.window_width:
            self.minion1.rect.right = ml.window_width
            self.minion1.x = self.minion1.rect.centerx
            self.minion1.current_angle = 180 - self.minion1.current_angle
        elif self.minion1.rect.top < 0:
            self.minion1.rect.top = 0
            self.minion1.y = self.minion1.rect.centery
            self.minion1.current_angle = 360 - self.minion1.current_angle
        elif self.minion1.rect.bottom > ml.window_height:
            self.minion1.rect.bottom = ml.window_height
            self.minion1.y = self.minion1.rect.centery
            self.minion1.current_angle = 360 - self.minion1.current_angle
        self.minion1.current_angle = ml.normalize_angle(self.minion1.current_angle)
        # minion2
        self.minion_angle = ml.normalize_angle(self.minion_angle + 1)
        radius = 250
        circle_x = ml.player.rect.centerx + radius * math.cos(math.radians(self.minion_angle))
        circle_y = ml.player.rect.centery - radius * math.sin(math.radians(self.minion_angle))
        minion2_point = circle_x, circle_y
        self.minion2.x, self.minion2.y, _ = ml.move_point(self.minion2, minion2_point,
                                                          20, 0, 360)
        self.minion2part.move((self.minion2.x, self.minion2.y))
        self.phase3miniontimer1 = self.shoot(self.phase3miniontimer1, self.phase3minionbd1,
                                             self.phase3minionfd)
        # Move parts
        self.minion1part.move((self.minion1.x, self.minion1.y))
        self.minion2part.move((self.minion2.x, self.minion2.y))
        self.minion3part.move((self.minion3.x, self.minion3.y))

    def animate_parts(self):
        self.ring1.animate(angle_change=7)
        self.ring2.animate(angle_change=-7)
        self.ring1.move(self.rect.center)
        self.ring2.move(self.rect.center)
        
        if self.phase == 1 and self.part_color != 'red':
            self.ring1.change_image('ring1_red.png')
            self.ring2.change_image('ring2_red.png')
            self.part_color = 'red'
        elif self.phase == 2 and self.part_color != 'orange':
            self.ring1.change_image('ring1_orange.png')
            self.ring2.change_image('ring2_orange.png')
            self.part_color = 'orange'
        elif self.phase == 3 and self.part_color != 'purple':
            self.ring1.change_image('ring1_purple.png')
            self.ring2.change_image('ring2_purple.png')
            self.part_color = 'purple'
        elif self.phase == 4 and self.part_color != 'blue':
            self.ring1.change_image('ring1_blue.png')
            self.ring2.change_image('ring2_blue.png')
            self.part_color = 'blue'

    def collide_parts(self):
        self.laser.update_mask()
        if pygame.sprite.collide_mask(self.laser, ml.player):
            ml.player.damage(self.laser_damage)

    def animate(self):
        start_rect_center = self.rect.center
        self.current_angle = ml.normalize_angle(self.current_angle)

        if ml.time() - self.phase_change_time < self.phase_change_delay:
            self.invincible = True
            self.image = pygame.transform.rotate(self.boss_invisible_image,
                                                 self.current_angle)
        else:
            self.invincible = False
            self.image = pygame.transform.rotate(self.image_original, self.current_angle)

        self.rect = self.image.get_rect()
        self.rect.center = start_rect_center

    def kill(self):
        self.spawn_powerups(base_powerup_spawn * 8)
        super().kill()


class BossPart(pygame.sprite.Sprite):
    """Class for parts of multi-part bosses."""
    def __init__(self, image_name):
        pygame.sprite.Sprite.__init__(self)
        self.image_path = os.path.join('graphics', image_name)
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image_original = self.image
        self.rect = self.image.get_rect()
        self.x, self.y = 0, 0
        self.mask = pygame.mask.from_surface(self.image)
        self.current_angle = 0
        self.add(ml.boss_part_group)

    def update(self):
        self.update_rect()

    def update_rect(self):
        self.rect.center = self.x, self.y

    def move(self, coords: tuple):
        """Moves the BossPart to the given coordinates (centered). All movement calculations
        must be done on the boss that spawns the part. """
        self.x, self.y = coords

    def change_image(self, image_name=None, image=None):
        """Changes image to the image of specified name in the 'graphics' folder."""
        start_point = self.rect.center
        if image:
            self.image = image
        else:
            self.image_path = os.path.join('graphics', image_name)
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.image_original = self.image
        self.rect = self.image.get_rect()
        self.rect.center = start_point
    
    def animate(self, new_angle=None, angle_change=0, scale_change=(0, 0)):
        """Transform the image of the BossPart. new_angle will rotate the image to the given
        angle. angle_change will increase the current angle of rotation. scale_change will
        resize the image to fit the rectangle of specified (w, h)"""
        start_point = self.rect.center
        if new_angle is not None:
            self.image = pygame.transform.rotate(self.image_original, new_angle)
        elif angle_change:
            self.current_angle += angle_change
            self.image = pygame.transform.rotate(self.image_original,
                                                 self.current_angle)
        if scale_change != (0, 0):
            self.image = pygame.transform.smoothscale(self.image_original, scale_change)
        self.rect = self.image.get_rect()
        self.rect.center = start_point

    def update_mask(self):
        """If the BossPart is being changed with change_image() or animate(), this should be
        called before any mask collisions are done."""
        self.mask = pygame.mask.from_surface(self.image)

    def get_mask_rect(self):
        return self.mask.get_bounding_rects()[0]
