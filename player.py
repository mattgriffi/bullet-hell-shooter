# My name
# Final project for ECE102
# Started 9/05/2016     Due 12/08/2016
#
# Player class

import math
import os.path
import powerups
import pygame

from mylibrary import MyLibrary as ml
from bullets import PlayerBullet


class Player(pygame.sprite.Sprite):
    def __init__(self) -> pygame.sprite.Sprite:
        pygame.sprite.Sprite.__init__(self)
        self.health = ml.get_upgrade_values('Max Health')
        self.hitbox_width = 5
        self.move_speed = float(ml.get_upgrade_values('Movement Speed'))
        self.shift_speed = ml.normalize_target_fps(2)
        self.diagonal_move_speed = 0
        self.invincibility_duration = 1  # Seconds of invulnerability after taking damage
        self.last_hit_time = -999
        self.hit_toggle_time = ml.time()
        self.invincibility_active = False

        # Shooting
        self.firing_timer = ml.time()

        # Set up image, rect, and mask
        self.image_path = os.path.join('graphics', 'player.png')
        self.homing_image_path = os.path.join('graphics', 'player_homing.png')
        self.invisible_image_path = os.path.join('graphics', 'player_invisible.png')
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.homing_image = pygame.image.load(self.homing_image_path).convert_alpha()
        self.invisible_image = pygame.image.load(self.invisible_image_path).convert_alpha()
        self.image_original = self.image
        # Even width prevents proper centering of hitbox and mouse movement
        assert self.image.get_width() % 2, "Player image width must be odd."
        self.x = ml.window_width / 2
        self.y = ml.window_height - 100
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.mask = pygame.mask.from_surface(self.image, 250)
        self.mask_original = self.mask
        self.hitbox = pygame.Rect(self.rect.centerx, self.rect.centerx,
                                  self.hitbox_width, self.hitbox_width)
        # Create mask for hitbox to deal with enemy collision
        self.hitbox_mask = pygame.mask.Mask(self.rect.size)
        self.rect.topleft = 0, 0
        top_left = self.rect.centerx - self.hitbox_width // 2, \
            self.rect.centery - self.hitbox_width // 2
        for x in range(self.hitbox_width):
            current_x = top_left[0] + x
            for y in range(self.hitbox_width):
                current_y = top_left[1] + y
                self.hitbox_mask.set_at((current_x, current_y), 1)
        self.rect.center = self.x, self.y

        # Powerups
        self.shield_active = False
        self.shield = None
        self.heal_amount = 1
        self.homing_shots_active = False
        self.homing_shots_activation_time = None
        self.toggle_time = None

        # Add sprite to group
        self.add(ml.player_group)

        ml.update_player_data(self)
        ml.update_player_health()

    def update(self, up: bool, left: bool, down: bool, right: bool,
               mouse_move: bool, shift: bool):
        self.move(up, left, down, right, mouse_move, shift)
        self.shoot()
        self.damage_animation()
        self.update_powerups()
        self.check_collision()

    def update_move_speed(self):
        self.move_speed = ml.normalize_target_fps(
                float(ml.get_upgrade_values('Movement Speed')))
        self.diagonal_move_speed = self.move_speed * math.sin(math.pi / 4)

    def damage(self, damage: int):
        if damage > 0 and not self.shield_active and \
                                ml.time() - self.last_hit_time > self.invincibility_duration:
            self.health -= damage
            self.invincibility_active = True
            self.last_hit_time = ml.time()
            self.hit_toggle_time = ml.time()
        # Heal
        elif damage < 0:
            self.health -= damage
        if self.health > ml.get_upgrade_values('Max Health'):
            self.health = ml.get_upgrade_values('Max Health')
        ml.update_player_health()

    def damage_animation(self):
        """Flashes the player sprite to show invincibility frames. This method must be called
        before update_powerups() so it doesn't override self.homing_image"""
        if ml.time() - self.last_hit_time < self.invincibility_duration:
            if ml.time() - self.hit_toggle_time > 0.05:
                if self.image in (self.image_original, self.homing_image):
                    self.hit_toggle_time = ml.time()
                    self.image = self.invisible_image
                else:
                    self.hit_toggle_time = ml.time()
                    if self.homing_shots_active:
                        self.image = self.homing_image
                    else:
                        self.image = self.image_original
        else:
            # update_powerups() will set self.image to homing_image if necessary
            self.invincibility_active = False
            self.image = self.image_original

    def set_coords(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y

    def shoot(self):
        if ml.time() - self.firing_timer >= (1 / ml.get_upgrade_values('Attack Speed')):
            shot_angles = ml.multi_shot_angles(
                    ml.get_upgrade_values('Multi Shot'), 90, 10)
            for i in range(ml.get_upgrade_values('Multi Shot')):
                PlayerBullet(self.rect.centerx, self.rect.y,
                             ml.get_upgrade_values('Bullet Speed'),
                             ml.get_upgrade_values('Damage'),
                             shot_angles[i], self.homing_shots_active)
            self.firing_timer = ml.time()

    def move(self, up: bool, left: bool, down: bool, right: bool,
             mouse_move: bool, shift: bool):
        """Move player sprite based on boolean inputs. Also moves the hitbox."""

        self.update_move_speed()

        if shift:
            self.move_speed = self.shift_speed
            self.diagonal_move_speed = self.move_speed * math.sin(math.pi / 4)

        # Diagonal motion
        if not mouse_move:
            if up and right and not (down or left):
                self.x += self.diagonal_move_speed
                self.y -= self.diagonal_move_speed
            elif up and left and not (down or right):
                self.x -= self.diagonal_move_speed
                self.y -= self.diagonal_move_speed
            elif down and right and not (up or left):
                self.x += self.diagonal_move_speed
                self.y += self.diagonal_move_speed
            elif down and left and not (up or right):
                self.x -= self.diagonal_move_speed
                self.y += self.diagonal_move_speed

            # Non-diagonal motion
            else:
                if up and not down:
                    self.y -= self.move_speed
                elif left and not right:
                    self.x -= self.move_speed
                elif down and not up:
                    self.y += self.move_speed
                elif right and not left:
                    self.x += self.move_speed

        # Mouse movement
        else:
            pos = pygame.mouse.get_pos()
            distance_x = pos[0] - self.rect.centerx
            distance_y = pos[1] - self.rect.centery
            distance_r = math.hypot(distance_x, distance_y)
            angle = math.atan2(distance_y, distance_x)
            if distance_r <= self.move_speed:
                self.x, self.y = pos
            else:
                self.x += self.move_speed * math.cos(angle)
                self.y += self.move_speed * math.sin(angle)

        self.rect.center = self.x, self.y

        # Prevent movement beyond window bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.centerx
        if self.rect.right > ml.window_width:
            self.rect.right = ml.window_width
            self.x = self.rect.centerx
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.centery
        if self.rect.bottom > ml.window_height:
            self.rect.bottom = ml.window_height
            self.y = self.rect.centery

        self.hitbox.center = self.rect.center

    def check_collision(self):
        """Check and deal with collision between Player and anything else."""

        # Check collision with enemies
        # Check rect collision first
        if not self.shield_active:  # Disable collision when shield is on
            enemies_hit = pygame.sprite.spritecollide(self, ml.enemy_group, False)
            if enemies_hit:
                # Change mask to hitbox mask before checking collision
                self.mask = self.hitbox_mask
                for enemy in enemies_hit:
                    if not enemy.invincible:
                        # Check mask collision
                        enemy.update_mask()  # proper mask for rotating enemies
                        if pygame.sprite.collide_mask(self, enemy):
                            self.damage(enemy.get_damage())
                # Change mask back to normal
                self.mask = self.mask_original

        # Check collision with enemy bullets
        enemy_bullets_hit = pygame.sprite.spritecollide(self,
                                                        ml.enemy_bullet_group, False)
        if enemy_bullets_hit:
            for enemy_bullet in enemy_bullets_hit:
                # Hitbox collision
                if self.hitbox.colliderect(enemy_bullet.get_mask_rect()):
                    self.damage(enemy_bullet.get_damage())
                    enemy_bullet.kill()

        # Check collision with powerups
        powerups_hit = pygame.sprite.spritecollide(self, ml.powerup_group, False)
        if powerups_hit:
            for powerup in powerups_hit:
                # Mask collision
                if pygame.sprite.collide_mask(self, powerup):
                    if isinstance(powerup, powerups.HomingShots):
                        self.homing_shots_active = True
                        self.homing_shots_activation_time = ml.time()
                        self.image = self.homing_image
                        self.toggle_time = ml.time()
                        powerup.kill()
                    elif isinstance(powerup, powerups.Shield):
                        if not self.shield_active:
                            self.shield = powerups.ShieldEffect()
                        else:
                            self.shield.reset_duration()
                        powerup.kill()
                    elif isinstance(powerup, powerups.Bomb):
                        for enemy in ml.enemy_group.sprites():
                            enemy.damage(ml.get_upgrade_values('Bomb Damage'))
                        powerup.kill()
                    elif isinstance(powerup, powerups.Heal):
                        if self.health < ml.get_upgrade_values('Max Health'):
                            self.damage(-self.heal_amount)
                        if self.health > ml.get_upgrade_values('Max Health'):
                            self.health = ml.get_upgrade_values('Max Health')
                        powerup.kill()
                    elif isinstance(powerup, powerups.Bonus):
                        ml.change_score(500)
                        powerup.kill()

    def update_powerups(self):
        # Update shield
        if self.shield and not self.shield.alive():
            self.shield_active = False
            self.shield = None
        elif self.shield:
            self.shield_active = True

        # Update homing shots
        if self.homing_shots_active:
            if ml.time() - self.homing_shots_activation_time >= \
                    ml.get_upgrade_values('Homing Duration'):
                self.homing_shots_active = False
                self.image = self.image_original
            if not self.invincibility_active:
                self.image = self.homing_image
            # Flicker sprite color when Homing duration is low
            if ml.time() - self.homing_shots_activation_time > \
                    ml.get_upgrade_values('Homing Duration') - 1:
                if ml.time() - self.toggle_time > 0.15:
                    if self.image == self.image_original:
                        self.toggle_time = ml.time()
                        self.image = self.homing_image
                    else:
                        self.toggle_time = ml.time()
                        self.image = self.image_original
