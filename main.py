import pygame
import os
import sys, random

from classes import *
from DB import *

result = [0, 0, 0, 0]

shelters = [[[(170, 0), (45, 170)], [(420, 0), (45, 170)], [(170, 425), (45, 170)], [(420, 425), (45, 170)]],
            [[(200, 200), (100, 100)]],
            [[(200, 0), (50, 320)], [(380, 275), (50, 320)]]]

mods = [0, 0, 0]

def terminate():
    pygame.quit()
    sys.exit()

def start_screen(clock, intro_text, size):
    fon = pygame.transform.scale(load_image('start_screen.png'), size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                screen.fill("#000000")
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(30)

def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

def speed_to_xy(rx, ry, speed):
    try:
        k = speed / ((rx ** 2 + ry ** 2) ** 0.5)
    except ZeroDivisionError:
        k = 0
    return round(k * rx), round(k * ry)

def intersect(p11, p12, p21, p22):
    if p11[0] <= p21[0] <= p12[0] or p11[0] <= p22[0] <= p12[0]:
        if p11[1] <= p21[1] <= p12[1] or p11[1] <= p22[1] <= p12[1]:
            return True
    return False

class Board:
    def __init__(self, width, height, indentation, screen, xshift, yshift):
        self.size = self.width, self.height = width, height
        self.indentation = indentation
        self.screen = screen
        self.shift = (xshift, yshift)
        self.limitation = (
            self.indentation + xshift, self.indentation + yshift, self.width - self.indentation + xshift,
            self.height - self.indentation + yshift)
        self.all_shelters = random.choice(shelters)

    def render(self):
        self.screen.fill("#B22222", (self.shift[0], self.shift[1], self.width, self.height))  # кирпичный
        self.screen.fill("#FFCC00", (
            self.indentation + self.shift[0], self.indentation + self.shift[1], self.width - 2 * self.indentation,
            self.height - 2 * self.indentation))  # цвет Яндекс
        for shelter in self.all_shelters:
            pygame.draw.rect(self.screen, "#B22222", tuple([shelter[0][0] + self.shift[0], shelter[0][1]
                                                              + self.shift[1]] + [shelter[1][0], shelter[1][1]]))

    def clear(self):
        self.screen.fill("#FFCC00", (
            self.indentation + self.shift[0], self.indentation + self.shift[1], self.width - 2 * self.indentation,
            self.height - 2 * self.indentation))
        for shelter in self.all_shelters:
            pygame.draw.rect(self.screen, (255, 0, 0), tuple([shelter[0][0] + self.shift[0], shelter[0][1]
                                                              + self.shift[1]] + [shelter[1][0], shelter[1][1]]))

    def item_inside(self, pos, hitbox):
        a = self.limitation[0] < pos[0] and pos[0] + hitbox[0] < self.limitation[2] and self.limitation[1] < pos[
            1] and pos[1] + hitbox[1] < self.limitation[3]
        if a:
            for shelter in self.all_shelters:
                p11 = shelter[0]
                p12 = (shelter[1][0] + shelter[0][0], shelter[1][1] + shelter[0][1])
                p21 = (pos[0] - self.shift[0], pos[1] - self.shift[1])
                p22 = (pos[0] + hitbox[0] - self.shift[0], pos[1] + hitbox[1] - self.shift[1])
                if intersect(p11, p12, p21, p22):
                    return False
            return True
        return False

class Entity(pygame.sprite.Sprite):
    def __init__(self, speed, position, health, damage, board, image, color, *group):
        super().__init__(*group)
        self.image = load_image(image, color)
        self.speed = speed
        self.health = health
        self.damage = damage
        self.board = board
        self.rot = False

        self.max_health = health

        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.mask = pygame.mask.from_surface(self.image)

    def set_image(self, image):
        self.image = load_image(image)

    def get_hit(self, damage):
        self.health -= damage

    # moves
    def move_up(self):
        if self.board.item_inside([self.rect.x, self.rect.y - self.speed], (self.rect.width, self.rect.height)):
            self.rect.y -= self.speed

    def move_right(self):
        if self.board.item_inside([self.rect.x + self.speed, self.rect.y], (self.rect.width, self.rect.height)):
            self.rect.x += self.speed

    def move_down(self):
        if self.board.item_inside([self.rect.x, self.rect.y + self.speed], (self.rect.width, self.rect.height)):
            self.rect.y += self.speed

    def move_left(self):
        if self.board.item_inside([self.rect.x - self.speed, self.rect.y], (self.rect.width, self.rect.height)):
            self.rect.x -= self.speed

    def update(self):
        if self.health <= 0:
            self.kill()

class Enemy(Entity):
    def __init__(self, speed, position, hitbox, health, damage, board, image, color, *group):
        super().__init__(speed, position, health, damage, board, image, color, *group)
        self.speed_x, self.speed_y = speed_to_xy(hero.rect.x - self.rect.x, hero.rect.y - self.rect.y, speed)

        self.image = pygame.transform.scale(self.image, hitbox)
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.mask = pygame.mask.from_surface(self.image)

        self.damage += mods[0]
        self.health += mods[1]
        self.speed += mods[2]

    def is_alive(self):
        return self.health > 0

    def update(self):
        super().update()
        self.speed_x, self.speed_y = speed_to_xy(hero.rect.x - self.rect.x, hero.rect.y - self.rect.y, self.speed)
        if board.item_inside((self.rect.x, self.rect.y + self.speed_y), (self.rect.width, self.rect.height)):
            self.rect.y += self.speed_y
        if board.item_inside((self.rect.x + self.speed_x, self.rect.y), (self.rect.width, self.rect.height)):
            self.rect.x += self.speed_x

class Calwan(Enemy):
    def __init__(self, position, board, *group):
        super().__init__(3, position, (50, 50), 10, 2, board, "pen.png", -1, *group)

class BCalwan(Calwan):
    def __init__(self, pos, b, *g,):
        super().__init__(pos, b, *g)
        self.image = pygame.transform.scale(load_image("pen.png", -1), (75, 75))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.health = 20
        self.max_health = 20
        self.speed = 2
        self.damage = 3

        self.damage += mods[0]
        self.health += mods[1]
        self.speed += mods[2]

class SCalwan(Calwan):
    def __init__(self, pos, b, *g,):
        super().__init__(pos, b, *g)
        self.image = pygame.transform.scale(self.image, (25, 25))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.health = 5
        self.max_health = 5
        self.speed = 5
        self.damage = 5

        self.damage += mods[0]
        self.health += mods[1]
        self.speed += mods[2]

class Hero(Entity):
    def __init__(self, speed, position, health, damage, board, *group):
        super().__init__(speed, position, health, damage, board, "hero.png", None, *group)
        self.image = pygame.transform.scale(self.image, (45, 45))
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.rect.width = 45
        self.rect.height = 45
        self.weapon = []
        self.maxCountWeapons = 2
        self.spellRecharge = 0
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        super().update()
        if pygame.key.get_pressed()[pygame.K_w]:
            self.move_up()
        if pygame.key.get_pressed()[pygame.K_a]:
            self.move_left()
            if not self.rot:
                self.image = pygame.transform.flip(self.image, True, False)
                self.rot = True
        if pygame.key.get_pressed()[pygame.K_s]:
            self.move_down()
        if pygame.key.get_pressed()[pygame.K_d]:
            self.move_right()
            if self.rot:
                self.image = pygame.transform.flip(self.image, True, False)
                self.rot = False

        self.spellRecharge -= 1
        #self.health -= 1

    def change_weapon(self):
        if len(self.weapon) > 1:
            self.weapon = self.weapon[1:] + self.weapon[0]

    def attack(self):
        if len(self.weapon) != 0:
            self.weapon[0].shot()

class Bullet(Entity):
    def __init__(self, speed, position, health, damage, board, image, *group, mouse_x, mouse_y, sender='player'):
        super().__init__(speed, position, health, damage, board, image, None, *group)
        self.speed_x, self.speed_y = speed_to_xy(mouse_x - hero.rect.x, mouse_y - hero.rect.y, speed)
        self.alive = True
        self.image = pygame.transform.scale(self.image, (10, 10))
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.image.fill(pygame.Color("blue"))
        self.sender = sender

    def update(self):
        if board.item_inside((self.rect.x, self.rect.y), (self.rect.width, self.rect.height)):
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
        else:
            self.kill()

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('MEMErun')
    size = width, height = 800, 700
    screen = pygame.display.set_mode(size)

    all_sprites = pygame.sprite.Group()
    bullet_sprites = pygame.sprite.Group()
    enemies_sprites = pygame.sprite.Group()

    board = Board(700, 600, 10, screen, 50, 50)
    r = random.randint(1, 3)
    if r == 1:
        hero = Dodger(3, [600, 500], 900, 5, board, all_sprites)
    elif r == 2:
        hero = Warrior(3, [600, 500], 900, 5, board, all_sprites)
    else:
        hero = Priest(3, [600, 500], 900, 5, board, all_sprites)

    enemies = [BCalwan([100, 100], board, enemies_sprites), SCalwan([100, 300], board, enemies_sprites), Calwan([300, 100], board, enemies_sprites)]
    level = 1
    font = pygame.font.Font(None, 30)
    bullets = []
    board.render()

    clc = pygame.time.Clock()
    to_go = False
    running = True
    start_screen(clc, ["ЗАСТАВКА", "",
                  "Правила игры",
                  "WASD - перемещение",
                  "SPACE - стрельба", "RB - спелл", "R - призвать существ"], size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_RIGHT:
                    hero.spell()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    for e in enemies:
                        e.kill()
                    enemies = [BCalwan([100, 100], board, enemies_sprites), SCalwan([100, 300], board, enemies_sprites),
                               Calwan([300, 100], board, enemies_sprites)]
                    mods[0] += 0.2
                    mods[1] += 1
                    mods[2] += 0.1

                    hero.health += 180
                    if hero.health > hero.max_health:
                        hero.health = hero.max_health

                elif event.key == pygame.K_SPACE:
                    bullets.append(Bullet(8, (hero.rect.x, hero.rect.y), 1, hero.damage, board, "cartridge2.png", bullet_sprites,
                                          mouse_x=pygame.mouse.get_pos()[0], mouse_y=pygame.mouse.get_pos()[1]))
        #
        screen.fill(pygame.Color('black'))
        screen.fill("#444444", (0, 680, 500, 20))
        screen.fill("#FF0000", (0, 680, hero.health * (500 / hero.max_health), 20))
        #
        all_sprites.update()
        board.render()

        bullet_sprites.update()
        for enemy in enemies:
            if enemy.is_alive():
                if pygame.sprite.collide_mask(enemy, hero):
                    hero.get_hit(enemy.damage)
                enemy.update()
                for bullet in bullets:
                    if bullet.alive and intersect((enemy.rect.x, enemy.rect.y),
                                                  (enemy.rect.x + enemy.rect.width, enemy.rect.y + enemy.rect.height),
                                                  (bullet.rect.x, bullet.rect.y),
                                                  (bullet.rect.x + bullet.rect.width, bullet.rect.y + bullet.rect.height)):
                        enemy.health -= bullet.damage
                        result[1] += bullet.damage
                        bullet.alive = False
                        bullet.kill()
            else:
                enemies.remove(enemy)
                result[2] += 1
                enemy.kill()
        enemies_sprites.draw(screen)
        all_sprites.draw(screen)
        bullet_sprites.draw(screen)

        all_sprites.draw(screen)
        if not enemies:
            level += 1
            for e in enemies:
                e.kill()
            enemies = [BCalwan([100, 100], board, enemies_sprites), SCalwan([100, 300], board, enemies_sprites),
                        Calwan([300, 100], board, enemies_sprites)]
            mods[0] += 0.2
            mods[1] += 1
            mods[2] += 0.1

            hero.health += 180
            if hero.health > hero.max_health:
                hero.health = hero.max_health
            if level % 5 == 0:
                board = Board(700, 600, 10, screen, 50, 50)
                hero.board = board
                if board.item_inside([hero.rect.x, hero.rect.y], (hero.rect.width, hero.rect.height)):
                    x1 = hero.rect.x
                    x2 = hero.rect.x
                    while True:
                        x1 += 1
                        x2 -= 1
                        if board.item_inside([x1, hero.rect.y], (hero.rect.width, hero.rect.height)):
                            hero.rect.x = x1
                            break
                        if board.item_inside([x2, hero.rect.y], (hero.rect.width, hero.rect.height)):
                            hero.rect.x = x2
                            break

        string_rendered = font.render(f'Уровень {level}', 1, pygame.Color('white'))
        screen.blit(string_rendered, (600, 680))
        result[3] += 1

        pygame.display.flip()
        clc.tick(90)
        if not hero.alive():
            start_screen(clc, ["Конец", "",
                       f"Ноль: {result[0]}",
                       f"Нанесено урона: {result[1]}",
                       f"Убито существ: {result[2]}", f"Пройдено кадров:{result[3]}"], size)
            save(result[1], result[3], result[2])
    pygame.quit()

