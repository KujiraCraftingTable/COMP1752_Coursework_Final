import pygame
from pygame.locals import *


flying = False
game_over = False


class CharacterImage:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    # draw character on menu
    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Character(pygame.sprite.Sprite):
    def update(self, flying, game_over):
        # gravity
        if flying == True:
            self.vel += 0.5
        if self.vel > 8:
            self.vel = 8
        if self.rect.bottom < 768:
            self.rect.y += int(self.vel)

        # jump
        if game_over == False:
            key = pygame.key.get_pressed()
            if key[K_SPACE] and not self.pressed:
                self.pressed = True
                self.vel = -8
            if not key[K_SPACE]:
                self.pressed = False

            # animation of the character
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # rotate the character
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
