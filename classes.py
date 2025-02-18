import pygame

from main import *


class Priest(Hero):
    def spell(self):
        if self.spellRecharge <= 0 < self.health:
            self.health += 90
            if self.health > self.max_health:
                self.health = self.max_health
            self.spellRecharge = 90*4


class Dodger(Hero):
    def spell(self):
        if self.spellRecharge <= 0 < self.health:
            l = 50
            if pygame.key.get_pressed()[pygame.K_w]:
                for _ in range(l):
                    self.move_up()
            if pygame.key.get_pressed()[pygame.K_a]:
                for _ in range(l):
                    self.move_left()
            if pygame.key.get_pressed()[pygame.K_s]:
                for _ in range(l):
                    self.move_down()
            if pygame.key.get_pressed()[pygame.K_d]:
                for _ in range(l):
                    self.move_right()
            self.spellRecharge = 180

charge = 0
class Warrior(Hero):


    def update(self):
        super().update()
        global charge
        if charge == 0:
            self.damage = 5
        charge -= 1

    def spell(self):
        if self.spellRecharge <= 0 < self.health:
            global charge
            charge = 90*3
            self.damage = self.damage * 2
            self.spellRecharge = 90*5
