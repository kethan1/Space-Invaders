import sys
import time
import pygame
from pygame.locals import *
from sprites import *

CELLSIZE = 50
WIDTH = 800
HEIGHT = 600

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

player_image = pygame.transform.scale(pygame.image.load("spaceship.png"), (CELLSIZE, CELLSIZE))
bullet_image = pygame.transform.scale(pygame.image.load("bullet.png"), (CELLSIZE, CELLSIZE))
bullet_image2 = pygame.transform.flip(pygame.transform.scale(pygame.image.load("bullet.png"), (CELLSIZE, CELLSIZE)), False, True)
alien1_image = pygame.transform.scale(pygame.image.load("alien1.png"), (CELLSIZE, CELLSIZE))

player = Player(screen=screen, x=WIDTH/2 - CELLSIZE/2, y=HEIGHT - CELLSIZE - 5,
                image=player_image, bullet_image=bullet_image)

clock = pygame.time.Clock()

x = WIDTH / 2 - CELLSIZE * 3
y = CELLSIZE * 2
level1 = [
    [StandardAlien(screen, x + CELLSIZE * n - 1, y, alien1_image, bullet_image2) for n in range(1, 7)],
    [StandardAlien(screen, x + CELLSIZE * n - 1, y + CELLSIZE, alien1_image, bullet_image2) for n in range(1, 7)],
    [StandardAlien(screen, x + CELLSIZE * n - 1, y + CELLSIZE * 2, alien1_image, bullet_image2) for n in range(1, 7)],
    [StandardAlien(screen, x + CELLSIZE * n - 1, y + CELLSIZE * 3, alien1_image, bullet_image2) for n in range(1, 7)]
]
levels = [Level(level1, 3)]
game = Game(screen, player, levels, 0, pygame.font.SysFont("monospace", 50))

aliens = level1.copy()

space_invader_movement = -5
while True:
    clock.tick(60)
    pygame.display.update()
    screen.fill((0, 0, 0))
    for row in range(CELLSIZE, WIDTH + 1, CELLSIZE):
        pygame.draw.line(screen, (255, 255, 255), (row, 0), (row, HEIGHT))
        pygame.draw.line(screen, (255, 255, 255), (0, row), (WIDTH, row))

    game.update_aliens()
    game.check_if_level_done()
    player.draw()
    player.show_bullets()

    if game.gameover:
        if game.win:
            game.win_screen()
        else:
            game.lose_screen()

    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        player.move_left()
    if keys[K_RIGHT]:
        player.move_right()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            player.shoot()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                player.shoot()
