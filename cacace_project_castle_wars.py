import os
import pygame
import sys
import math
import random
import pickle
from constants_castle_wars import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # in order to get relative paths

# general initialization
pygame.init()

frame_counter = 0
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Castle Wars")

# loading and scaling of static images + font
font_path = os.path.join(BASE_DIR, "assets", "TrajanPro-Bold.otf")
font = pygame.font.Font(font_path, font_size)  # we import the font

background_image_path = os.path.join(BASE_DIR, "assets", "backies.png")
background_image = pygame.image.load(background_image_path)
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

sign_path = os.path.join(BASE_DIR, "assets", "button1_0.png")
sign_image = pygame.image.load(sign_path)
sign_image = pygame.transform.scale(sign_image, (200, 80))

hover_path = os.path.join(BASE_DIR, "assets", "button1_1.png")
hover_image = pygame.image.load(hover_path)

sing_path = os.path.join(BASE_DIR, "assets", "button2_0.png")
sing_image = pygame.image.load(sing_path)
sing_image = pygame.transform.scale(sing_image, (200, 80))

title_path = os.path.join(BASE_DIR, "assets", "name.png")
title_image = pygame.image.load(title_path)
title_image = pygame.transform.scale(title_image, (630, 70))

barracks1_image_path = os.path.join(BASE_DIR, "assets", "barracks1.png")
barracks1_image = pygame.image.load(barracks1_image_path)
barracks2_image_path = os.path.join(BASE_DIR, "assets", "barracks2.png")
barracks2_image = pygame.image.load(barracks2_image_path)
barracks1_image = pygame.transform.scale(barracks1_image, (barracks_width, barracks_height))
barracks1_image = pygame.transform.flip(barracks1_image, True, False)  # barracks1 gets flipped
barracks2_image = pygame.transform.scale(barracks2_image, (barracks_width, barracks_height))
mine1_image_path = os.path.join(BASE_DIR, "assets", "mine1.png")
mine1_image = pygame.image.load(mine1_image_path)
mine2_image_path = os.path.join(BASE_DIR, "assets", "mine2.png")
mine2_image = pygame.image.load(mine2_image_path)
mine1_image = pygame.transform.scale(mine1_image, (mine_width, mine_height))
mine2_image = pygame.transform.scale(mine2_image, (mine_width, mine_height))

# sprite groups
arrow_1_group = pygame.sprite.Group()
archer_1_group = pygame.sprite.Group()
arrow_2_group = pygame.sprite.Group()
archer_2_group = pygame.sprite.Group()
knight_1_group = pygame.sprite.Group()
knight_2_group = pygame.sprite.Group()
worker_1_group = pygame.sprite.Group()
worker_2_group = pygame.sprite.Group()
king_group = pygame.sprite.Group()
queen_group = pygame.sprite.Group()
towerarrows1_group = pygame.sprite.Group()
towerarrows2_group = pygame.sprite.Group()


class Button:
    """Since there are many buttons both in the game itself and in the menu, we created a Button class in order to avoid
    redundancies in the code"""
    def __init__(self, x, y, size, text=""):
        self.text = text
        self.size = size
        self.normal = pygame.transform.scale(sing_image, self.size)
        self.hover = pygame.transform.scale(hover_image, self.size)
        # when the pointer is on top of the button, the button changes color
        self.rect = self.normal.get_rect(topleft=(x, y))
        self.font = pygame.font.Font(font_path, 30)

    def draw(self, surface):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            surface.blit(self.hover, (self.rect.left + 3, self.rect.top + 2))
        else:
            surface.blit(self.normal, self.rect.topleft)
        text_surface = self.font.render(self.text, True, GOLD)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False


class Player:
    """In this class we introduce the player. This is useful for differentiating between player1 and player2,
    it helps us load the images and define the logic for each player."""
    def __init__(self, who):
        self.who = who  # can be 1 or 2
        self.resources = INIT_RESOURCES
        self.monarch_spawned = False  # to make sure we can only have one monarch per player

        if who == 1:  # the paths to the sprites for player1 and player2
            self.assets = {
                "tower": os.path.join("assets", "tower_player_1"),
                "archer": os.path.join("assets", "new_elf_archer"),
                "knight": os.path.join("assets", "new_elf_green_knight"),
                "wall": os.path.join("assets", "wall_player_1"),
                "worker": os.path.join("assets", "new_green_ogre"),
                "monarch": os.path.join("assets", "new_king")
            }

        elif who == 2:
            self.assets = {
                "tower": os.path.join("assets", "tower_player_2"),
                "archer": os.path.join("assets", "new_girlie_red_archer"),
                "knight": os.path.join("assets", "new_girlie_with_sword"),
                "wall": os.path.join("assets", "wall_player_2"),
                "worker": os.path.join("assets", "new_red_troll"),
                "monarch": os.path.join("assets", "new_queen")
            }


class Coin(pygame.sprite.Sprite):
    """This is mainly for aesthetic purposes. The coin animation is on top of the screen. Below that, we keep track
    of the player's resources"""
    def __init__(self, x, y, player):
        super().__init__()
        self.player = player
        self.size = COIN_SIZE
        self.assets = []
        self.frame_index = 0  # image starts from frame 0
        self.load_assets()
        self.image = self.assets[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [x, y]
        if self.player.who == 1:
            self.flip = True  # to maintain symmetry
        else:
            self.flip = False
        self.update_time = pygame.time.get_ticks()
        self.animation_speed = ANIMATION_SPEED

    def load_and_scale(self, file_path):  # we load the image of the sprite and scale it to the size we want
        image = pygame.image.load(file_path).convert_alpha()
        return pygame.transform.smoothscale(image, self.size)

    def load_assets(self):
        assets_folder = os.path.join(BASE_DIR, "assets", "coin")
        # the path to the folder of the sprite

        for i in range(1, 31):  # we have 30 frames
            file_path = os.path.join(assets_folder, f"Gold_{i}.png")
            self.assets.append(self.load_and_scale(file_path))

    def update_animation(self):
        if self.frame_index >= len(self.assets):
            self.frame_index = 0  # once we reach the last frame, we go back to frame 0
        self.image = self.assets[self.frame_index]
        if self.flip:  # we animate the flipping
            self.image = pygame.transform.flip(self.image, True, False)
        current_time = pygame.time.get_ticks()
        if current_time - self.update_time > self.animation_speed * 3:  # we update the frame_index
            self.update_time = current_time
            self.frame_index += 1


class HealthBar:
    """We create a healthbar class in order to avoid redundancies. Each fighter has a healthbar, and we also have
    one for the tower and the wall"""
    def __init__(self, x, y, w, h, max_HP, HP, player):
        self.player = player  # in order to avoid confusion, player1 HP is green and player2 HP is red
        self.x, self.y = x, y
        self.w, self.h, = w, h
        self.max_HP = max_HP
        self.HP = HP
        self.invisible = False
        if self.player.who == 1:
            self.color = GREEN
            self.flip = False
        else:
            self.color = MAROON
            self.flip = True

    def draw_health_bar(self, surface):
        ratio = self.HP / self.max_HP
        if not self.invisible:
            pygame.draw.rect(surface, (104, 87, 76), (self.x, self.y, self.w, self.h))  # background rect
            if self.flip:
                pygame.draw.rect(surface, self.color,
                                 (self.x + self.w - self.w * ratio, self.y, self.w * ratio, self.h))
            else:  # HP rect
                pygame.draw.rect(surface, self.color,
                                 (self.x, self.y, self.w * ratio, self.h))
            pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.w, self.h), 2)  # border
        else:
            return


class Wall(pygame.sprite.Sprite):
    """This class handles the wall"""
    def __init__(self, x, y, player):
        super().__init__()
        self.player = player
        self.x = x
        self.y = y
        self.size = WALL_WIDTH, WALL_HEIGHT
        self.max_HP = WALL_HEALTH
        self.HP = WALL_HEALTH
        self.assets = []
        self.frame_index = 0  # starts from frame 0
        self.load_assets()
        self.image = self.assets[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [x, y]
        if self.player.who == 1:
            self.health_bar_x = 475  # position of the healthbar on the screen
        else:
            self.health_bar_x = 1050
        self.health_bar_y = 170
        self.health_bar = HealthBar(self.health_bar_x, self.health_bar_y, 185, 25, self.max_HP, self.HP, self.player)

    def load_and_scale(self, file_path):
        image = pygame.image.load(file_path).convert_alpha()
        return pygame.transform.smoothscale(image, self.size)

    def load_assets(self):
        assets_folder = self.player.assets["wall"]

        for i in range(3):
            file_path = os.path.join(assets_folder, f"wall_{i}.png")
            self.assets.append(self.load_and_scale(file_path))

    def update(self):
        self.health_bar.HP = self.HP  # the healthbar animation
        if self.HP >= 400:  # we animate the wall according to damage
            self.frame_index = 0
            self.image = self.assets[self.frame_index]
        elif self.HP < 400 and self.HP > 150:
            self.frame_index = 1
            self.image = self.assets[self.frame_index]
        elif self.HP <= 150 and self.HP > 0:
            self.frame_index = 2
            self.image = self.assets[self.frame_index]
        elif self.HP <= 0:
            self.HP = 0
            self.kill()  # the wall disappears once it is destroyed


class Tower(pygame.sprite.Sprite):
    """This class handles the tower"""
    def __init__(self, x, y, player):
        super().__init__()
        self.player = player
        self.x = x
        self.y = y
        self.size = TOWER_WIDTH, TOWER_HEIGHT
        self.max_HP = TOWER_HEALTH
        self.HP = TOWER_HEALTH
        self.assets = []
        self.frame_index = 0
        self.load_assets()
        self.image = self.assets[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [x, y]
        self.flip = True if self.player.who == 1 else False  # player 1 tower is flipped
        if self.player.who == 1:
            self.health_bar_x = 230  # position of the healthbar on the screen
            self.flip = True
        else:
            self.health_bar_x = 1295
            self.flip = False
        self.health_bar_y = 170
        self.health_bar = HealthBar(self.health_bar_x, self.health_bar_y, 185, 25, self.max_HP, self.HP, self.player)
        self.cooldown_timer_1 = 0  # the cooldown is frame-based rather than turn-based
        self.cooldown_timer_2 = 0
        self.arrows_1 = []  # keeps track of the arrows shot by the tower in order to allow cooldown
        self.arrows_2 = []
        self.cooldown = TOWER_COOLDOWN  # cooldown period in frames

    def cooling_down_1(self):
        if len(self.arrows_1) == 1:  # tower can shoot one arrow at a time
            self.cooldown_timer_1 += 1  # the timer starts after the arrow is shot
            if self.cooldown_timer_1 >= self.cooldown:
                self.arrows_1.clear()  # allows the tower to shoot again
                self.cooldown_timer_1 = 0  # reset timer

    def cooling_down_2(self):
        if len(self.arrows_2) == 1:
            self.cooldown_timer_2 += 1
            if self.cooldown_timer_2 >= self.cooldown:
                self.arrows_2.clear()
                self.cooldown_timer_2 = 0

    def shoot_arrow(self):
        arrow = TowerArrow(self.rect.x + (100 if self.player.who == 1 else -100),
                           self.rect.y + 150, self.player)  # we define an arrow and where it spawns
        if self.player.who == 1:
            if len(self.arrows_1) < 1:  # can only shoot one at a time
                towerarrows1_group.add(arrow)  # arrow is added to the group so that it can be drawn and animated
                self.arrows_1.append(arrow)  # appended to the list for the cooldown and initial condition
                arrow.shoot()  # the arrow is shot
        else:
            if len(self.arrows_2) < 1:
                towerarrows2_group.add(arrow)
                self.arrows_2.append(arrow)
                arrow.shoot()

    def load_and_scale(self, file_path):
        image = pygame.image.load(file_path).convert_alpha()
        if self.player.who == 2:
            return pygame.transform.smoothscale(image, self.size)
        else:
            image = pygame.transform.smoothscale(image, self.size)
            return pygame.transform.flip(image, True, False)

    def load_assets(self):
        assets_folder = self.player.assets["tower"]

        for i in range(3):
            file_path = os.path.join(assets_folder, f"tower_{i}.png")
            self.assets.append(self.load_and_scale(file_path))

    def update(self):
        if self.player.who == 1:
            self.cooling_down_1()
        else:
            self.cooling_down_2()
        self.image = self.assets[self.frame_index]
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        self.health_bar.HP = self.HP
        if self.HP >= 400:  # same as Wall
            self.frame_index = 0
            self.image = self.assets[self.frame_index]
        elif self.HP < 400 and self.HP > 150:
            self.frame_index = 1
            self.image = self.assets[self.frame_index]
        elif self.HP <= 150 and self.HP > 0:
            self.frame_index = 2
            self.image = self.assets[self.frame_index]
        elif self.HP <= 0:
            self.HP = 0
            self.kill()


class Character(pygame.sprite.Sprite):
    """This class introduces characters. We define it in order to avoid redundancies"""
    def __init__(self, x, y, player, size, assets_folder, speed, max_hp):
        super().__init__()
        self.player = player
        self.size = size
        self.assets_folder = assets_folder  # changes depending on character
        self.speed = speed
        self.max_HP = max_hp
        self.HP = max_hp
        self.alive = True  # character starts alive
        self.walking = False
        self.animation_speed = ANIMATION_SPEED
        self.update_time = pygame.time.get_ticks()
        self.assets = {"idle": [], "walking": [], "attacking": [], "dead": []}  # the four states
        self.load_assets()
        self.action = "idle"  # character starts idle
        self.frame_index = 0
        self.image = self.assets[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [x, y]
        if self.player.who == 1:
            self.flip = False  # player2 starts flipped
        else:
            self.flip = True
        self.direction = -1 if self.flip else 1

    def load_and_scale(self, file_path):
        image = pygame.image.load(file_path).convert_alpha()
        return pygame.transform.smoothscale(image, self.size)

    def load_assets(self):
        idle_path = os.path.join(self.assets_folder, "0.png")
        self.assets["idle"].append(self.load_and_scale(idle_path))

        name_of_sprites = {"walking": 1, "attacking": 3, "dead": 5}
        for action, prefix in name_of_sprites.items():
            for i in range(10):
                file_path = os.path.join(self.assets_folder, f"{prefix}_{i}.png")
                self.assets[action].append(self.load_and_scale(file_path))

    def is_alive(self):  # checks the character's health
        if self.HP <= 0:
            self.HP = 0
            self.alive = False

    def die(self):  # death of character
        if self.action != "dead":
            self.action = "dead"
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.assets["dead"]) - 1:
            self.kill()  # kills the sprite once the animation is over
        self.update_animation()

    def still(self):
        self.action = "idle"
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.assets[self.action][self.frame_index]
        self.update_animation()

    def walk(self):
        if self.action != "walking":
            self.action = "walking"
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            self.image = self.assets[self.action][self.frame_index]
        self.update_animation()


class Worker(Character):
    """This class deals with the workers, a type of character"""
    def __init__(self, x, y, player):
        super().__init__(x, y, player, WORKER_SIZE, player.assets["worker"], WORKER_SPEED, WORKER_MAX_HP)
        self.player = player
        self.repairing_wall = False
        self.repairing_tower = False
        self.working = False
        self.going_to_mine = False
        self.going_to_tower = False
        self.going_to_wall = False

    def load_assets(self):
        self.assets = {"idle": [], "walking": [], "repairing": [], "dead": []}
        assets_folder = self.player.assets["worker"]

        idle_path = os.path.join(assets_folder, "0.png")
        self.assets["idle"].append(self.load_and_scale(idle_path))

        name_of_sprites = {"walking": 1, "repairing": 3, "dead": 5}
        for action, prefix in name_of_sprites.items():
            for i in range(10):
                file_path = os.path.join(assets_folder, f"{prefix}_{i}.png")
                self.assets[action].append(self.load_and_scale(file_path))

    def repair(self):
        if self.action != "repairing":
            self.action = "repairing"
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            self.image = self.assets[self.action][self.frame_index]
            self.update_animation()

    def go_to_mine(self):
        self.going_to_mine = True
        self.flip = True if self.player.who == 1 else False
        self.direction = -1 if self.player.who == 1 else 1
        self.walking = True
        self.going_to_tower = False
        self.going_to_wall = False
        self.repairing_wall = False
        self.repairing_tower = False

    def mine(self):
        if self.player.who == 1:
            condition = self.rect.x > 20
        else:
            condition = self.rect.x < 1580
        if condition:  # the worker walks to the mine
            self.walk()
            self.rect.x += self.speed * self.direction
        else:  # the worker starts mining
            self.walking = False
            self.still()
            self.working = True
            self.player.resources += 0.01

    def stop_repair(self):
        if self.player.who == 1:
            if self.repairing_tower:
                building = tower_1
            elif self.repairing_wall:
                building = wall_1
        else:
            if self.repairing_tower:
                building = tower_2
            elif self.repairing_wall:
                building = wall_2
        if building.HP >= building.max_HP:
            self.still()

    def go_to_tower(self):
        if self.player.who == 1:
            t = tower_1
        else:
            t = tower_2
        if self.rect.x <= t.rect.x:
            self.flip = False
            self.direction = 1
        else:
            self.flip = True
            self.direction = -1
        self.going_to_tower = True
        self.walking = True
        self.working = False
        self.going_to_mine = False
        self.going_to_wall = False
        self.repairing_wall = False
        self.repairing_tower = False

    def fix_tower(self):
        d = random.randint(0, 70)  # makes it so that the workers aren't on top of each other
        if self.player.who == 1:
            c_range = range(tower_1.rect.x, tower_1.rect.x + d)
            t = tower_1
        else:
            c_range = range(tower_2.rect.x - d, tower_2.rect.x)
            t = tower_2
        if self.rect.x in c_range:  # if it is in range, it starts repairing
            if self.walking and self.going_to_tower:
                self.walking = False
                self.going_to_tower = False
                self.still()
                if t.HP < t.max_HP and t.HP > 0:  # it can only repair if there is damage and the tower is up
                    self.repairing_tower = True
        else:  # worker walks to the tower
            self.walk()
            self.rect.x += (self.speed * self.direction)

    def fixing(self):  # starts the animation and adds HP to the building being fixed
        t = tower_1 if self.player.who == 1 else tower_2
        w = wall_1 if self.player.who == 1 else wall_2
        if self.repairing_tower and t.HP > 0:
            self.repair()
            t.HP += 0.05
        elif self.repairing_tower and t.HP <= 0:
            self.repairing_tower = False
            self.still()
        if self.repairing_wall and w.HP > 0:
            self.repair()
            w.HP += 0.05
        elif self.repairing_wall and w.HP <= 0:
            self.repairing_wall = False
            self.still()

    def go_to_wall(self):
        self.flip = False if self.player.who == 1 else True
        self.going_to_tower = False
        self.walking = True
        self.working = False
        self.going_to_mine = False
        self.going_to_wall = True
        self.repairing_wall = False
        self.repairing_tower = False

    def fix_wall(self):
        d = random.randint(0, 50)
        if self.player.who == 1:
            c_range = range(wall_1.rect.x - d, wall_1.rect.x)
            w = wall_1
            self.direction = 1
        else:
            c_range = range(wall_2.rect.x, wall_2.rect.x + d)
            w = wall_2
            self.direction = -1
        if self.rect.x in c_range:
            if self.walking and self.going_to_wall:
                self.walking = False
                self.going_to_wall = False
                self.still()
                if w.HP < w.max_HP and w.HP > 0:
                    self.repairing_wall = True
        else:
            self.walk()
            self.rect.x += self.speed * self.direction

    def update(self):
        self.is_alive()  # we check whether the character is alive
        if not self.alive:
            self.die()  # other we kill it
            return  # if the character is dead, no point in continuing the update
        if self.player.who == 1:
            if self.going_to_mine:
                self.mine()
            if self.going_to_tower:
                self.fix_tower()
            if self.repairing_tower:
                self.fixing()
                self.stop_repair()
            if self.going_to_wall:
                self.fix_wall()
            if self.repairing_wall:
                self.fixing()
                self.stop_repair()
        if self.player.who == 2:
            if self.going_to_mine:
                self.mine()
            if self.going_to_tower:
                self.fix_tower()
            if self.repairing_tower:
                self.fixing()
                self.stop_repair()
            if self.going_to_wall:
                self.fix_wall()
            if self.repairing_wall:
                self.fixing()
                self.stop_repair()
        self.update_animation()

    def update_animation(self):
        if self.frame_index >= len(self.assets[self.action]):
            self.frame_index = 0
        self.image = self.assets[self.action][self.frame_index]
        if self.flip:  # dynamic flipping
            self.image = pygame.transform.flip(self.image, True, False)
        if self.player.who == 1:
            if self.rect.x <= 20:
                self.image.set_alpha(0)  # worker sprite is invisible while in the mine
            else:
                self.image.set_alpha(255)
        else:
            if self.rect.x >= 1580:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
        current_time = pygame.time.get_ticks()
        if current_time - self.update_time > self.animation_speed:
            self.update_time = current_time
            self.frame_index += 1


class Fighter(Character):
    """This class introduces the fighter, a type of character"""
    def __init__(self, x, y, player, size, assets_folder, speed, max_hp):
        super().__init__(x, y, player, size, assets_folder, speed, max_hp)
        self.player = player
        self.assets = {"idle": [], "walking": [], "attacking": [], "dead": []}
        self.load_assets()
        self.attacking = False
        self.attacking_characters = False
        self.walking_to_barracks = False
        self.walking_to_enemy = False
        self.enemy_1 = None
        self.enemy_2 = None
        self.health_bar = HealthBar(self.rect.x, self.rect.y + 100, 138, 15, self.max_HP, self.HP, self.player)

    def return_to_barracks(self):  # fighter returns to barracks (or close to them)
        d = random.randint(0, 50)
        if self.player.who == 1:
            c_range = range(150 - d, 150 + d)
            self.direction = -1
        else:
            c_range = range(1400 - d, 1400 + d)
            self.direction = 1
        if self.rect.x in c_range:  # waits in barracks
            self.walking_to_barracks = False
            self.walking = False
            self.flip = False if self.player.who == 1 else True
            self.still()
            self.attacking = False
        else:  # walks to barracks
            self.flip = True if self.player.who == 1 else False
            self.walking = True
            self.attacking = False
            self.walk()
            if self.rect.x > 0 and self.rect.x < 1600:
                self.rect.x += self.speed*self.direction

    def find_closest_enemy(self):
        closest_enemy = None
        min_dist = float("inf")  # infinity
        if self.player.who == 1:
            enemy_groups = [archer_2_group, knight_2_group]
        else:
            enemy_groups = [archer_1_group, knight_1_group]
        for group in enemy_groups:
            for enemy in group:
                d = abs(self.rect.x - enemy.rect.x)  # distance between fighter and enemy
                if d < min_dist:  # always true
                    min_dist = d
                    closest_enemy = enemy
        if self.player.who == 1:
            if closest_enemy:
                if wall_2.HP <= 0 or closest_enemy.rect.x <= (wall_2.rect.x - 50):
                    return closest_enemy
                else:
                    return None  # can only attack enemies wen the wall is down or they're outside
        else:
            if closest_enemy:
                if wall_1.HP <= 0 or closest_enemy.rect.x >= (wall_1.rect.x + 50):
                    return closest_enemy
                else:
                    return None

    def stop_attack_1(self):  # if the enemy is dead, stop the attack
        if self.enemy_1 and self.enemy_1.HP <= 0:
            self.enemy_1 = None
            self.walking_to_barracks = True

    def stop_attack_2(self):
        if self.enemy_2 and self.enemy_2.HP <= 0:
            self.enemy_2 = None
            self.walking_to_barracks = True

    def check_range_1(self):  # if the enemy is no longer within range, stop the attack
        if self.enemy_1:
            d = abs(self.rect.x - self.enemy_1.rect.x)
            if d > self.range and self.attacking_characters:
                self.attacking = False
                self.still()

    def check_range_2(self):
        if self.enemy_2:
            d = abs(self.rect.x - self.enemy_2.rect.x)
            if d > self.range and self.attacking_characters:
                self.attacking = False
                self.still()

    def attack_character(self):
        self.enemy_1 = self.find_closest_enemy()
        self.enemy_2 = self.find_closest_enemy()
        opponent = self.enemy_1 if self.player.who == 1 else self.enemy_2
        if opponent:
            d = random.randint(0, self.range)
            if opponent.rect.x < self.rect.x:
                self.flip = True
                self.direction = -1
                c_range = range(opponent.rect.x, opponent.rect.x + d)
            else:
                self.flip = False
                self.direction = 1
                c_range = range(opponent.rect.x - d, opponent.rect.x)
            if self.rect.x in c_range:  # attack the enemy
                self.walking_to_enemy = False
                self.walking = False
                self.attacking = True
                self.attacking_characters = True
            else:  # walk to the enemy
                self.walking = True
                self.walking_to_enemy = True
                self.walk()
                self.rect.x += self.speed * self.direction
        else:  # if a viable enemy is not found, nothing happens
            self.walking_to_enemy = False
            self.walking = False
            self.still()

    def update_animation(self):
        if self.frame_index >= len(self.assets[self.action]):
            self.frame_index = 0
        self.image = self.assets[self.action][self.frame_index]
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        current_time = pygame.time.get_ticks()
        if current_time - self.update_time > self.animation_speed:
            self.update_time = current_time
            self.frame_index += 1


class Monarch(Fighter):
    """The ultimate objective of the game is to kill them"""
    def __init__(self, x, y, player):
        super().__init__(x, y, player, MONARCH_SIZE, player.assets["monarch"], MONARCH_SPEED, MONARCH_MAX_HP)
        self.player = player

    def walk_1(self):  # freely walk by pressing keys
        keys = pygame.key.get_pressed()
        self.walking = False
        if self.rect.x < 1600:  # walk within bounds of the screen
            if keys[pygame.K_LALT]:
                self.flip = False
                self.walking = True
                self.rect.x += self.speed
        if self.rect.x > 0:
            if keys[pygame.K_LCTRL]:
                self.flip = True
                self.walking = True
                self.rect.x -= self.speed
        if self.walking:
            self.walk()
        if not (keys[pygame.K_LALT] or keys[pygame.K_LCTRL]):
            self.still()

    def walk_2(self):
        keys = pygame.key.get_pressed()
        self.walking = False
        if self.rect.x < 1600:
            if keys[pygame.K_RIGHT]:
                self.flip = False
                self.walking = True
                self.rect.x += self.speed
        if self.rect.x > 0:
            if keys[pygame.K_LEFT]:
                self.flip = True
                self.walking = True
                self.rect.x -= self.speed
        if self.walking:
            self.walk()
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self.still()

    def update(self):
        self.is_alive()  # we check whether the character is alive
        if not self.alive:
            self.die()
            return
        self.health_bar.x = self.rect.x  # the healthbar needs to move with the character
        self.health_bar.y = self.rect.y + 100
        self.health_bar.HP = self.HP
        if self.player.who == 1:
            self.walk_1()
        if self.player.who == 2:
            self.walk_2()
        self.update_animation()


class Knight(Fighter):
    """Subclass of fighter"""
    def __init__(self, x, y, player):
        super().__init__(x, y, player, KNIGHT_SIZE, player.assets["knight"], KNIGHT_SPEED, KNIGHT_MAX_HP)
        self.player = player
        self.cost = KNIGHT_COST
        self.range = KNIGHT_RANGE
        self.attacking_monarch = False
        self.walking_to_monarch = False

    def collision(self):  # defines the collisions
        hits = {}
        monarch_hits = {}
        if self.player.who == 1:
            if self.attacking_characters:  # since we use different keys to attack army and monarchs
                # it also makes sure that if we're attacking an army member and a monarch walks within
                # range of collision, the damage is not registered
                hits = pygame.sprite.groupcollide(knight_1_group, archer_2_group, False, False)
                hits.update(pygame.sprite.groupcollide(knight_1_group, knight_2_group, False, False))
            elif self.attacking_monarch:
                monarch_hits = pygame.sprite.groupcollide(knight_1_group, queen_group, False, False)
        else:
            if self.attacking_characters:
                hits = pygame.sprite.groupcollide(knight_2_group, archer_1_group, False, False)
                hits.update(pygame.sprite.groupcollide(knight_2_group, knight_1_group, False, False))
            elif self.attacking_monarch:
                monarch_hits = pygame.sprite.groupcollide(knight_2_group, king_group, False, False)

        for knight, targets in hits.items():
            for target in targets:
                target.HP -= 0.05
                target.is_alive()
                target.update_animation()
        for knight, targets in monarch_hits.items():
            for target in targets:
                target.HP -= 0.05
                target.is_alive()
                target.update_animation()

    def attack(self):
        if self.action != "attacking":
            self.action = "attacking"
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            self.image = self.assets[self.action][self.frame_index]
        self.collision()  # we verify whether there's been a collision
        self.update_animation()

    def retreat(self):
        self.walking = True
        self.walking_to_barracks = True
        self.walking_to_enemy = False
        self.attacking = False

    def attack_enemy(self):
        self.walking_to_enemy = True
        self.walking = True
        self.walking_to_barracks = False
        self.attacking = False
        self.attacking_monarch = False

    def go_to_monarch(self):
        self.walking_to_monarch = True
        self.walking_to_enemy = False
        self.walking = True
        self.walking_to_barracks = False
        self.attacking = False
        self.attacking_characters = False

    def attack_monarch(self):  # knights are the only ones who can
        self.enemy_1 = next(iter(queen_group), None)  # single item in group
        self.enemy_2 = next(iter(king_group), None)
        enemy = self.enemy_1 if self.player.who == 1 else self.enemy_2
        if enemy:
            d = random.randint(0, self.range)
            if enemy.rect.x < self.rect.x:
                self.flip = True
                self.direction = -1
                c_range = range(enemy.rect.x, enemy.rect.x + d)
            else:
                self.flip = False
                self.direction = 1
                c_range = range(enemy.rect.x - d, enemy.rect.x)
            if self.rect.x in c_range:  # if in range, attack
                self.walking_to_monarch = False
                self.walking = False
                self.attacking = True
                self.attacking_monarch = True
            else:  # walk to within range
                self.walking = True
                self.walking_to_monarch = True
                self.walk()
                self.rect.x += self.speed * self.direction

        else:  # if the monarch isn't viable, it can't be attacked
            self.walking_to_monarch = False
            self.walking = False
            self.still()

    def update(self):
        self.is_alive()  # we check whether the character is alive
        if not self.alive:
            self.die()
            return
        self.health_bar.x = self.rect.x  # the healthbar needs to move with the character
        self.health_bar.y = self.rect.y + 100
        self.health_bar.HP = self.HP
        if self.player.who == 1:
            self.stop_attack_1()
            if self.walking_to_enemy:
                self.attack_character()
            if self.walking_to_monarch:
                self.attack_monarch()
            if self.attacking:
                self.attack()
                self.check_range_1()
            if self.walking_to_barracks:
                self.return_to_barracks()
        if self.player.who == 2:
            self.stop_attack_2()
            if self.walking_to_enemy:
                self.attack_character()
            if self.walking_to_monarch:
                self.attack_monarch()
            if self.attacking:
                self.attack()
                self.check_range_2()
            if self.walking_to_barracks:
                self.return_to_barracks()
        self.update_animation()


class Archer(Fighter):
    """This class deals with the archer"""
    def __init__(self, x, y, player):
        super().__init__(x, y, player, ARCHER_SIZE, player.assets["archer"], ARCHER_SPEED, ARCHER_MAX_HP)
        self.player = player
        self.cost = ARCHER_COST
        self.range = ARCHER_RANGE
        self.max_arrows = MAX_ARROWS
        self.cooldown_timer_1 = 0  # the cooldown is frame-based rather than turn-based
        self.cooldown_timer_2 = 0
        self.cooldown = ARCHER_ATTACK_COOLDOWN
        self.walking_to_target = False
        self.arrows_1 = []
        self.arrows_2 = []
        self.target_1 = None
        self.target_2 = None

    def cooling_down_1(self):  # this starts a long cooldown period when the archer has shot 3 arrows
        if len(self.arrows_1) == self.max_arrows:  # the logic is the same as the tower
            self.cooldown_timer_1 += 1
            if self.cooldown_timer_1 >= self.cooldown:
                self.arrows_1.clear()
                self.cooldown_timer_1 = 0

    def cooling_down_2(self):
        if len(self.arrows_2) == self.max_arrows:
            self.cooldown_timer_2 += 1
            if self.cooldown_timer_2 >= self.cooldown:
                self.arrows_2.clear()
                self.cooldown_timer_2 = 0

    def attack_1(self):
        last_arrow1_dead = len(self.arrows_1) == 0 or not self.arrows_1[-1].on_screen_1()
        if last_arrow1_dead and len(self.arrows_1) < self.max_arrows:
            if self.action != "attacking":
                self.action = "attacking"
                self.frame_index = 0
                self.update_time = pygame.time.get_ticks()
            if self.frame_index == 7:
                direction = -1 if self.flip else 1
                distance = 20 if self.flip else 80
                arrow_1 = Arrow(self.rect.x + distance * direction, self.rect.y + 60, self.player, direction)
                if self.attacking_characters:
                    arrow_1.attacking_characters = True
                arrow_1_group.add(arrow_1)
                arrow_1.shoot()
                self.arrows_1.append(arrow_1)
        else:
            self.still()

    def attack_2(self):
        last_arrow2_dead = len(self.arrows_2) == 0 or not self.arrows_2[-1].on_screen_2()
        if last_arrow2_dead and len(self.arrows_2) < self.max_arrows:
            if self.action != "attacking":
                self.action = "attacking"
                self.frame_index = 0
                self.update_time = pygame.time.get_ticks()
            if self.frame_index == 9:
                direction = -1 if self.flip else 1
                distance = 20 if self.flip else 80
                arrow_2 = Arrow(self.rect.x + distance * direction, self.rect.y + 60, self.player, direction)
                if self.attacking_characters:
                    arrow_2.attacking_characters = True
                arrow_2_group.add(arrow_2)
                arrow_2.shoot()
                self.arrows_2.append(arrow_2)
        else:
            self.still()

    def retreat(self):
        self.walking = True
        self.walking_to_barracks = True
        self.walking_to_target = False
        self.attacking = False

    def walk_to_target(self):
        self.walking_to_enemy = False
        self.walking = True
        self.walking_to_barracks = False
        self.walking_to_target = True
        self.attacking = False
        self.attacking_characters = False

    def reach_target(self, target):
        if target.HP > 0:
            d = random.randint(0, self.range)
            if self.player.who == 1:
                c_range = range(target.rect.x - d, target.rect.x)
                self.direction = 1
                self.flip = False
            else:
                c_range = range(target.rect.x, target.rect.x + d)
                self.direction = -1
                self.flip = True
            if self.rect.x in c_range:
                self.walking_to_target = False
                self.walking_to_barracks = False
                self.walking = False
                self.attacking = True
            else:
                self.walking = True
                self.walking_to_barracks = False
                self.walk()
                self.rect.x += self.speed * self.direction
        else:
            self.return_to_barracks()

    def pick_target_1(self):
        if self.target_1 == "wall_2" and wall_2.HP <= 0:
            self.target_1 = None
            self.walking_to_barracks = True
        if self.target_1 == "tower_2" and tower_2.HP <= 0:
            self.target_1 = None
            self.walking_to_barracks = True

    def pick_target_2(self):
        if self.target_2 == "wall_1" and wall_1.HP <= 0:
            self.target_2 = None
            self.walking_to_barracks = True
        if self.target_2 == "tower_1" and tower_1.HP <= 0:
            self.target_2 = None
            self.walking_to_barracks = True

    def attack_enemy(self):
        self.walking_to_enemy = True
        self.walking = True
        self.walking_to_barracks = False
        self.walking_to_target = False
        self.attacking = False

    def update(self):
        self.is_alive()  # we check whether the character is alive
        if not self.alive:
            self.die()
            return
        self.health_bar.x = self.rect.x  # the healthbar needs to move with the character
        self.health_bar.y = self.rect.y + 100
        self.health_bar.HP = self.HP
        if self.player.who == 1:
            self.stop_attack_1()
            self.pick_target_1()
            if self.walking_to_target:
                target = wall_2 if self.target_1 == "wall_2" else tower_2
                self.reach_target(target)
            if self.walking_to_enemy:
                self.attack_character()
            if self.attacking:
                self.attack_1()
                self.check_range_1()
                self.cooling_down_1()
            if self.walking_to_barracks:
                self.return_to_barracks()
        if self.player.who == 2:
            self.stop_attack_2()
            self.pick_target_2()
            if self.walking_to_target:
                target = wall_1 if self.target_2 == "wall_1" else tower_1
                self.reach_target(target)
            if self.walking_to_enemy:
                self.attack_character()
            if self.attacking:
                self.attack_2()
                self.check_range_2()
                self.cooling_down_2()
            if self.walking_to_barracks:
                self.return_to_barracks()
        self.update_animation()


class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, player, direction):
        super().__init__()
        self.size = ARROW_SIZE
        self.player = player
        self.path = os.path.join(BASE_DIR, "assets", "arrow_1.png") if self.player.who == 1 else os.path.join(
            BASE_DIR, "assets", "arrow_2.png")
        self.image_unscaled = pygame.image.load(self.path).convert_alpha()
        self.direction = direction
        self.speed_x = self.direction * ARROW_SPEED * math.cos(math.radians(15))
        self.speed_y = -ARROW_SPEED * math.sin(math.radians(15))
        self.rotation_angle = -math.degrees(math.atan2(self.speed_y, self.speed_x))
        self.image_scaled = pygame.transform.smoothscale(self.image_unscaled, self.size)
        if self.direction == -1:
            self.image_scaled = pygame.transform.flip(self.image_scaled, True, False)
        self.image = pygame.transform.rotate(self.image_scaled, self.rotation_angle +
                                             (180 if self.direction == -1 else 0))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [x, y]
        self.initial_x = self.rect.x
        self.update_time = pygame.time.get_ticks()
        self.shot = False
        self.dt = 0.2
        self.animation_speed = ANIMATION_SPEED
        self.damage = ARROW_DAMAGE
        self.attacking_characters = False

    def shoot(self):
        self.shot = True

    def on_screen_1(self):
        return self in arrow_1_group

    def on_screen_2(self):
        return self in arrow_2_group

    def collide(self):
        building_hits = {}
        hits = {}
        if self.player.who == 1:
            if self.attacking_characters:
                hits = pygame.sprite.groupcollide(arrow_1_group, archer_2_group, True, False)
                hits.update(pygame.sprite.groupcollide(arrow_1_group, knight_2_group, True, False))
            else:
                building_hits = pygame.sprite.groupcollide(arrow_1_group, buildings_2_group, True, False)
        else:
            if self.attacking_characters:
                hits = pygame.sprite.groupcollide(arrow_2_group, archer_1_group, True, False)
                hits.update(pygame.sprite.groupcollide(arrow_2_group, knight_1_group, True, False))
            else:
                building_hits = pygame.sprite.groupcollide(arrow_2_group, buildings_1_group, True, False)

        for arrow, targets in hits.items():
            for target in targets:
                target.HP -= arrow.damage
                target.is_alive()
                target.update_animation()
        for arrow, targets in building_hits.items():
            for target in targets:
                target.HP -= 5

    def update(self):
        if self.shot:  # we simulate parabolic motion
            self.rect.x += self.speed_x * self.dt
            self.rect.y += self.speed_y * self.dt + 0.5 * GRAVITY * self.dt ** 2
            self.speed_y += GRAVITY * self.dt
            self.collide()
            self.update_animation()
            if self.rect.y > (SCREEN_HEIGHT - 50) or self.rect.y < 0:  # the arrow is killed when out of bounds
                self.kill()

    def update_animation(self):
        self.rotation_angle = -math.degrees(math.atan2(self.speed_y, self.speed_x))
        self.image = pygame.transform.rotate(self.image_scaled, self.rotation_angle +
                                             (180 if self.direction == -1 else 0))
        self.rect = self.image.get_rect(center=self.rect.center)


class TowerArrow(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.size = TOWER_ARROW_SIZE
        self.player = player
        self.path = os.path.join(BASE_DIR, "assets", "arrow_1.png") if self.player.who == 1 else os.path.join(
            BASE_DIR, "assets", "arrow_2.png")
        self.image_unscaled = pygame.image.load(self.path).convert_alpha()
        self.direction = 1 if self.player.who == 1 else -1
        self.speed_x = self.direction * ARROW_SPEED * math.cos(math.radians(-15))
        self.speed_y = -ARROW_SPEED * math.sin(math.radians(-15))
        self.rotation_angle = -math.degrees(math.atan2(self.speed_y, self.speed_x))
        self.image_scaled = pygame.transform.smoothscale(self.image_unscaled, self.size)
        if self.direction == -1:
            self.image_scaled = pygame.transform.flip(self.image_scaled, True, False)
        self.image = pygame.transform.rotate(self.image_scaled, self.rotation_angle +
                                             (180 if self.direction == -1 else 0))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [x, y]
        self.update_time = pygame.time.get_ticks()
        self.shot = False
        self.animation_speed = ANIMATION_SPEED
        self.damage = TOWER_DAMAGE
        self.dt = 0.2

    def shoot(self):
        self.shot = True

    def collide(self):
        if self.player.who == 1:
            hits = pygame.sprite.groupcollide(towerarrows1_group, archer_2_group, True, False)
            hits.update(pygame.sprite.groupcollide(towerarrows1_group, knight_2_group, True, False))
            hits.update(pygame.sprite.groupcollide(towerarrows1_group, queen_group, True, False))
        else:
            hits = pygame.sprite.groupcollide(towerarrows2_group, archer_1_group, True, False)
            hits.update(pygame.sprite.groupcollide(towerarrows2_group, knight_1_group, True, False))
            hits.update(pygame.sprite.groupcollide(towerarrows2_group, king_group, True, False))

        for arrow, targets in hits.items():
            for target in targets:
                target.HP -= self.damage
                target.is_alive()
                target.update_animation()

    def update(self):
        if self.shot:  # we simulate parabolic motion
            self.rect.x += self.speed_x * self.dt
            self.rect.y += self.speed_y * self.dt + 0.5 * GRAVITY * self.dt ** 2
            self.speed_y += GRAVITY * self.dt
            self.collide()
            self.update_animation()
            if self.rect.y > (SCREEN_HEIGHT - 80) or self.rect.y < 0:  # the arrow is killed when out of bounds
                self.kill()

    def update_animation(self):
        self.rotation_angle = -math.degrees(math.atan2(self.speed_y, self.speed_x))
        self.image = pygame.transform.rotate(self.image_scaled, self.rotation_angle +
                                             (180 if self.direction == -1 else 0))
        self.rect = self.image.get_rect(center=self.rect.center)


def text(surface, text, x, y, color):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


class Menu:
    def __init__(self, pause_menu=False):
        self.font = pygame.font.Font(font_path, 50)
        self.pause_menu = pause_menu
        self.saved_game_exists = os.path.exists(SaveLoad.SAVE_FILE)
        if pause_menu:
            self.buttons = [
                Button(665, 750, (370, 148), "Save Game"),
                Button(665, 550, (370, 148), "Resume"),
                Button(665, 350, (370, 148), "Load Game"),
                Button(665, 170, (370, 148), "Start New Game")
            ]
        else:
            self.buttons = [
                Button(665, 170, (370, 148), "Start Game"),
                Button(665, 350, (370, 148), "Load Game")
            ]

    def run(self):
        while True:
            screen.blit(background_image, (0, 0))
            screen.blit(title_image, (535, 50))

            for button in self.buttons:
                button.draw(screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in self.buttons:
                    if button.is_clicked(event):
                        if button.text == "Start Game":
                            return "new_game"
                        elif button.text == "Save Game":
                            return "save"
                        elif button.text == "Resume":
                            return "resume"
                        elif button.text == "Load Game" and self.saved_game_exists:
                            return "load"
                        elif button.text == "Start New Game":
                            return "new_game"


class Game:
    def __init__(self):
        pygame.init()
        self.running = True
        self.paused = False
        self.game_over = False
        self.frame_counter = 0
        self.current_state = "game"
        self.pause_button = Button(10, 10, (200, 80), "BACK")
        self.player_1 = Player(1)
        self.player_2 = Player(2)
        self.font = pygame.font.Font(font_path, 50)
        self.setup_game()

    def spawn_unit(self, unit_class, group, player, x, y, cost, max_units=5):
        if player.resources >= cost and len(group) < max_units:
            unit = unit_class(x, y, player)
            group.add(unit)
            player.resources -= cost

    def setup_game(self):
        """Initialize game objects."""
        global tower_1, tower_2, wall_1, wall_2, buildings_1_group, buildings_2_group, coin_1, coin_2

        tower_1 = Tower(TOWER_1_X, TOWER_1_Y, self.player_1)
        tower_2 = Tower(TOWER_2_X, TOWER_2_Y, self.player_2)
        wall_1 = Wall(WALL_1_X, WALL_1_Y, self.player_1)
        wall_2 = Wall(WALL_2_X, WALL_2_Y, self.player_2)

        buildings_1_group = pygame.sprite.Group(wall_1, tower_1)
        buildings_2_group = pygame.sprite.Group(wall_2, tower_2)

        coin_1 = Coin(100, 180, self.player_1)
        coin_2 = Coin(1550, 180, self.player_2)

    def save_game_state(self):
        game_data = {
            "player_1_resources": self.player_1.resources,
            "player_2_resources": self.player_2.resources,
            "tower_1": {"x": tower_1.rect.x, "y": tower_1.rect.y, "HP": tower_1.HP},
            "tower_2": {"x": tower_2.rect.x, "y": tower_2.rect.y, "HP": tower_2.HP},
            "wall_1": {"x": wall_1.rect.x, "y": wall_1.rect.y, "HP": wall_1.HP},
            "wall_2": {"x": wall_2.rect.x, "y": wall_2.rect.y, "HP": wall_2.HP},
            "archer_1": [(a.rect.x, a.rect.bottom, a.HP, a.walking, a.attacking, a.direction, a.flip) for a in
                         archer_1_group],
            "archer_2": [(a.rect.x, a.rect.bottom, a.HP, a.walking, a.attacking, a.direction, a.flip) for a in
                         archer_2_group],
            "knight_1": [(k.rect.x, k.rect.bottom, k.HP, k.walking, k.attacking, k.direction, k.flip) for k in
                         knight_1_group],
            "knight_2": [(k.rect.x, k.rect.bottom, k.HP, k.walking, k.attacking, k.direction, k.flip) for k in
                         knight_2_group],
            "worker_1": [(w.rect.x, w.rect.bottom, w.HP, w.walking, w.working, w.direction, w.flip) for w in worker_1_group],
            "worker_2": [(w.rect.x, w.rect.bottom, w.HP, w.walking, w.working, w.direction, w.flip) for w in worker_2_group],
            "game_over": self.game_over,
        }
        SaveLoad.save_game(game_data)
        print("Game state saved successfully!")
        pygame.event.clear()

    def load_game_state(self):
        loaded_data = SaveLoad.load_game()
        if not loaded_data:  # Prevents a crash if no save file exists
            print("No saved game found!")
            return
        if loaded_data:
            print("Game state loaded.")
            self.running = True  # Ensure the game runs after loading
            self.player_1.resources = loaded_data["player_1_resources"]
            self.player_2.resources = loaded_data["player_2_resources"]

            tower_1.rect.x, tower_1.rect.y, tower_1.HP = (
                loaded_data["tower_1"]["x"],
                loaded_data["tower_1"]["y"],
                loaded_data["tower_1"]["HP"]
            )
            tower_2.rect.x, tower_2.rect.y, tower_2.HP = (
                loaded_data["tower_2"]["x"],
                loaded_data["tower_2"]["y"],
                loaded_data["tower_2"]["HP"]
            )

            wall_1.rect.x, wall_1.rect.y, wall_1.HP = (
                loaded_data["wall_1"]["x"],
                loaded_data["wall_1"]["y"],
                loaded_data["wall_1"]["HP"]
            )
            wall_2.rect.x, wall_2.rect.y, wall_2.HP = (
                loaded_data["wall_2"]["x"],
                loaded_data["wall_2"]["y"],
                loaded_data["wall_2"]["HP"]
            )

            self.game_over = loaded_data["game_over"]

            archer_1_group.empty()
            archer_2_group.empty()
            knight_1_group.empty()
            knight_2_group.empty()
            worker_1_group.empty()
            worker_2_group.empty()

            for archer_data in loaded_data["archer_1"]:
                archer = Archer(*archer_data[:2], self.player_1)
                archer.HP, archer.walking, archer.attacking, archer.direction, archer.flip = archer_data[2:]
                archer_1_group.add(archer)

            for archer_data in loaded_data["archer_2"]:
                archer = Archer(*archer_data[:2], self.player_2)
                archer.HP, archer.walking, archer.attacking, archer.direction, archer.flip = archer_data[2:]
                archer_2_group.add(archer)

            for knight_data in loaded_data["knight_1"]:
                knight = Knight(*knight_data[:2], self.player_1)
                knight.HP, knight.walking, knight.attacking, knight.direction, knight.flip = knight_data[2:]
                knight_1_group.add(knight)

            for knight_data in loaded_data["knight_2"]:
                knight = Knight(*knight_data[:2], self.player_2)
                knight.HP, knight.walking, knight.attacking, knight.direction, knight.flip = knight_data[2:]
                knight_2_group.add(knight)

            for worker_data in loaded_data["worker_1"]:
                worker = Worker(*worker_data[:2], self.player_1)
                worker.HP, worker.walking, worker.working, worker.direction, worker.flip = worker_data[2:]
                worker_1_group.add(worker)

            for worker_data in loaded_data["worker_2"]:
                worker = Worker(*worker_data[:2], self.player_2)
                worker.HP, worker.walking, worker.working, worker.direction, worker.flip = worker_data[2:]
                worker_2_group.add(worker)

    def restart_game(self):
        """Restart the game"""
        self.player1.reset()
        self.player2.reset()
        self.game_over = False

    def start_new_game(self):
        self.current_state = "game"
        self.running = True
        """Reset the game state and start a new game"""
        self.player_1.resources = INIT_RESOURCES
        self.player_2.resources = INIT_RESOURCES
        self.player_1.monarch_spawned = False
        self.player_2.monarch_spawned = False

        archer_1_group.empty()
        archer_2_group.empty()
        arrow_1_group.empty()
        arrow_2_group.empty()
        knight_1_group.empty()
        knight_2_group.empty()
        worker_1_group.empty()
        worker_2_group.empty()
        king_group.empty()
        queen_group.empty()

        global tower_1, tower_2, wall_1, wall_2
        tower_1 = Tower(TOWER_1_X, TOWER_1_Y, self.player_1)
        tower_2 = Tower(TOWER_2_X, TOWER_2_Y, self.player_2)
        wall_1 = Wall(WALL_1_X, WALL_1_Y, self.player_1)
        wall_2 = Wall(WALL_2_X, WALL_2_Y, self.player_2)

        global buildings_1_group, buildings_2_group
        buildings_1_group = pygame.sprite.Group()
        buildings_1_group.add(wall_1, tower_1)
        buildings_2_group = pygame.sprite.Group()
        buildings_2_group.add(wall_2, tower_2)

        self.paused = False
        self.game_over = False

    def toggle_pause(self):
        pause_menu = Menu(pause_menu=True)
        action = pause_menu.run()
        if action == "resume":
            self.paused = False  # Resume game
        elif action == "save":
            self.save_game_state()
        elif action == "load":
            self.load_game_state()
        elif action == "new_game":
            self.start_new_game()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False  # Graceful exit instead of sys.exit()

            if self.current_state == "game":
                self.handle_game_keys(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.pause_button.is_clicked(event):  # Handle pause button click
                    state = self.toggle_pause()
                    if state == "new_game":  # If a new game is started, restart the game loop
                        return  # Exit the current game loop and restart
                    elif state == "load":  # If "Load Game" is selected
                        self.load_game_state()  # Load the saved game

    def handle_game_keys(self, event):
        random_x_1 = random.randint(100, 200)
        random_y = random.randint(800, 860)
        random_x_2 = random.randint(1350, 1450)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.spawn_unit(Archer, archer_1_group, self.player_1, random_x_1, random_y, ARCHER_COST)
            elif event.key == pygame.K_m:
                self.spawn_unit(Archer, archer_2_group, self.player_2, random_x_2, random_y, ARCHER_COST)
            elif event.key == pygame.K_n:
                self.spawn_unit(Knight, knight_2_group, self.player_2, random_x_2, random_y, KNIGHT_COST)
            elif event.key == pygame.K_x:
                self.spawn_unit(Knight, knight_1_group, self.player_1, random_x_1, random_y, KNIGHT_COST)
            elif event.key == pygame.K_c:
                self.spawn_unit(Worker, worker_1_group, self.player_1, random_x_1, random_y, WORKER_COST)
            elif event.key == pygame.K_b:
                self.spawn_unit(Worker, worker_2_group, self.player_2, random_x_2, random_y, WORKER_COST)
            elif event.key == pygame.K_SPACE:
                tower_1.shoot_arrow()
            elif event.key == pygame.K_RETURN:
                tower_2.shoot_arrow()

            for worker_1 in worker_1_group:
                if event.key == pygame.K_q:
                    worker_1.go_to_mine()
                elif event.key == pygame.K_w:
                    if tower_1.HP > 0:
                        worker_1.go_to_tower()
                elif event.key == pygame.K_e:
                    if wall_1.HP > 0:
                        worker_1.go_to_wall()

            for worker_2 in worker_2_group:
                if event.key == pygame.K_p:
                    worker_2.go_to_mine()
                elif event.key == pygame.K_o:
                    if tower_2.HP > 0:
                        worker_2.go_to_tower()
                elif event.key == pygame.K_i:
                    if wall_2.HP > 0:
                        worker_2.go_to_wall()

            for archer_1 in archer_1_group:
                if event.key == pygame.K_d:
                    if wall_2.HP > 0:
                        archer_1.target_1 = "wall_2"
                        archer_1.walk_to_target()
                    elif wall_2.HP <= 0 and tower_2.HP > 0 and archer_1.target_1 is None:
                        archer_1.target_1 = "tower_2"
                        archer_1.walk_to_target()
                if event.key == pygame.K_a:
                    archer_1.retreat()
                elif event.key == pygame.K_f:
                    archer_1.attack_enemy()

            for knight_1 in knight_1_group:
                if event.key == pygame.K_s:
                    knight_1.retreat()
                elif event.key == pygame.K_1:
                    knight_1.attack_enemy()
                elif event.key == pygame.K_2:
                    knight_1.go_to_monarch()

            for archer_2 in archer_2_group:
                if event.key == pygame.K_j:
                    if wall_1.HP > 0:
                        archer_2.target_2 = "wall_1"
                        archer_2.walk_to_target()
                    elif wall_1.HP <= 0 and tower_1.HP > 0 and archer_2.target_2 is None:
                        archer_2.target_2 = "tower_1"
                        archer_2.walk_to_target()
                if event.key == pygame.K_l:
                    archer_2.retreat()
                elif event.key == pygame.K_h:
                    archer_2.attack_enemy()

            for knight_2 in knight_2_group:
                if event.key == pygame.K_k:
                    knight_2.retreat()
                elif event.key == pygame.K_0:
                    knight_2.attack_enemy()
                elif event.key == pygame.K_9:
                    knight_2.go_to_monarch()

    def update(self):
        if self.current_state == "game":
            archer_1_group.update()
            arrow_1_group.update()
            archer_2_group.update()
            arrow_2_group.update()
            knight_1_group.update()
            knight_2_group.update()
            worker_1_group.update()
            worker_2_group.update()
            buildings_1_group.update()
            buildings_2_group.update()
            coin_1.update_animation()
            coin_2.update_animation()
            king_group.update()
            queen_group.update()
            towerarrows1_group.update()
            towerarrows2_group.update()
            self.check_game_over()
            self.frame_counter += 1

    def draw(self):
        screen.fill(BLACK)
        screen.blit(background_image, (0, 0))
        screen.blit(barracks1_image, (150, SCREEN_HEIGHT - 100 - barracks_height))
        screen.blit(mine1_image, (15, SCREEN_HEIGHT - 100 - mine_height))
        screen.blit(barracks2_image, (SCREEN_WIDTH - 150 - barracks_width, SCREEN_HEIGHT - 100 - barracks_height))
        screen.blit(mine2_image, (SCREEN_WIDTH - mine_width - 15, SCREEN_HEIGHT - 100 - mine_height))
        screen.blit(coin_1.image, coin_1.rect)
        screen.blit(coin_2.image, coin_2.rect)
        screen.blit(sign_image, (50, 250))
        screen.blit(title_image, (535, 15))
        text(screen, "Archer: £5, Z", 75, 270, GOLD)
        text(screen, "A, D, F", 115, 295, GOLD)
        screen.blit(sign_image, (270, 250))
        text(screen, "Knight: £5, X", 295, 270, GOLD)
        text(screen, "1, 2, S", 345, 295, GOLD)
        screen.blit(sign_image, (490, 250))
        text(screen, "WORKER: £2, C", 510, 270, GOLD)
        text(screen, "Q, W, E", 555, 295, GOLD)
        screen.blit(sing_image, (1450, 250))
        text(screen, "Archer: £5, M", 1475, 270, GOLD)
        text(screen, "L, J, H", 1525, 295, GOLD)
        screen.blit(sing_image, (1230, 250))
        text(screen, "Knight: £5, N", 1255, 270, GOLD)
        text(screen, "0, 9, J", 1305, 295, GOLD)
        screen.blit(sing_image, (1010, 250))
        text(screen, "WORKER: £2, B", 1030, 270, GOLD)
        text(screen, "P, O, I", 1080, 295, GOLD)
        text(screen, "Tower 1 health", 230, 135, BLACK)
        text(screen, "Wall 1 health", 486, 135, BLACK)
        text(screen, "Wall 2 health", 1060, 135, BLACK)
        text(screen, "Tower 2 health", 1295, 135, BLACK)
        text(screen, f"{int(self.player_1.resources)}", 110, 200, BLACK)
        text(screen, f"{int(self.player_2.resources)}", 1560, 200, BLACK)

        self.check_monarch_spawn()

        for king in king_group:
            king.health_bar.draw_health_bar(screen)
        for queen in queen_group:
            queen.health_bar.draw_health_bar(screen)
        for archer in archer_1_group:
            archer.health_bar.draw_health_bar(screen)
        for archer in archer_2_group:
            archer.health_bar.draw_health_bar(screen)
        for knight in knight_1_group:
            knight.health_bar.draw_health_bar(screen)
        for knight in knight_2_group:
            knight.health_bar.draw_health_bar(screen)

        towerarrows1_group.draw(screen)
        towerarrows2_group.draw(screen)
        buildings_1_group.draw(screen)
        buildings_2_group.draw(screen)
        worker_1_group.draw(screen)
        worker_2_group.draw(screen)
        knight_1_group.draw(screen)
        knight_2_group.draw(screen)
        archer_1_group.draw(screen)
        arrow_1_group.draw(screen)
        archer_2_group.draw(screen)
        arrow_2_group.draw(screen)
        king_group.draw(screen)
        queen_group.draw(screen)
        self.pause_button.draw(screen)

        tower_1.health_bar.draw_health_bar(screen)
        tower_2.health_bar.draw_health_bar(screen)
        wall_1.health_bar.draw_health_bar(screen)
        wall_2.health_bar.draw_health_bar(screen)

        pygame.display.flip()

    def check_monarch_spawn(self):
        if tower_1.HP == 0 and not self.player_1.monarch_spawned:
            king_group.add(Monarch(TOWER_1_X, TOWER_1_Y, self.player_1))
            self.player_1.monarch_spawned = True
        if tower_2.HP == 0 and not self.player_2.monarch_spawned:
            queen_group.add(Monarch(TOWER_2_X, TOWER_2_Y, self.player_2))
            self.player_2.monarch_spawned = True

    def check_game_over(self):
        """Checks if a monarch is dead and ends the game."""
        for king in king_group:
            if not king.alive:  # If the king is dead, player 2 wins
                self.game_over_screen("Player 2 Wins!")
                self.game_over = True
                return
        for queen in queen_group:
            if not queen.alive:  # If the queen is dead, player 1 wins
                self.game_over_screen("Player 1 Wins!")
                self.game_over = True
                return

    def game_over_screen(self, winner_text):
        """Displays the game over screen when a monarch dies"""
        running = True
        while running:
            screen.blit(background_image, (0, 0))
            # Display winner text
            text_surface = self.font.render(winner_text, True, GOLD)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)
            self.pause_button.draw(screen)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and self.pause_button.is_clicked(event):
                    self.toggle_pause()
                    return

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            if not self.paused:
                self.update()
                self.draw()
            pygame.time.Clock().tick(60)


class SaveLoad:
    SAVE_FILE = "castle_wars.pkl"

    @staticmethod
    def save_game(data):
        with open(SaveLoad.SAVE_FILE, "wb") as file:
            pickle.dump(data, file)

    @staticmethod
    def load_game():
        if os.path.exists(SaveLoad.SAVE_FILE):
            with open(SaveLoad.SAVE_FILE, "rb") as file:
                return pickle.load(file)
        return None


if __name__ == "__main__":
    while True:
        menu = Menu()
        state = menu.run()

        if state == "game":
            game_instance = Game()
            game_instance.run()
        if state == "new_game":
            game_instance = Game()
            game_instance.start_new_game()
            game_instance.run()
        elif state == "load":
            game_instance = Game()
            game_instance.load_game_state()
            game_instance.run()
