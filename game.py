import sys
import os
import pygame
from pygame.locals import *
from sprites import *

CELLSIZE = 40
WIDTH = 800
HEIGHT = 600

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

player_image = pygame.transform.scale(pygame.image.load("spaceship.png"), (CELLSIZE, CELLSIZE))
bullet_image = pygame.transform.scale(pygame.image.load("bullet.png"), (CELLSIZE, CELLSIZE))
bullet_image2 = pygame.transform.flip(bullet_image, False, True)
standard_alien_image = pygame.transform.scale(pygame.image.load("alien1.png"), (CELLSIZE, CELLSIZE))
beefy_alien_image = pygame.transform.scale(pygame.image.load("alien2.png"), (CELLSIZE, CELLSIZE))
annoying_alien_image = pygame.transform.scale(pygame.image.load("alien3.png"), (CELLSIZE, CELLSIZE))
boss_alien_image = pygame.transform.scale(pygame.image.load("alien4.png"), (CELLSIZE, CELLSIZE))
background = pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT))


player = Player(screen=screen, x=WIDTH/2 - CELLSIZE/2, y=HEIGHT - CELLSIZE - 5,
                image=player_image, bullet_image=bullet_image)

levels = []

alien_types = {
    "0": StandardAlien,
    "1": BeefyAlien,
    "2": AnnoyingAlien,
    "3": BossAlien
}

alien_images = {
    StandardAlien: standard_alien_image,
    BeefyAlien: beefy_alien_image,
    AnnoyingAlien: annoying_alien_image,
    BossAlien: boss_alien_image
}

for file in os.listdir("levels/"):
    with open(f"levels/{file}") as level1_csv:
        level_class_template = []
        for line in level1_csv:
            if line.startswith("#"):
                level_speed = int(line.strip("#alien_speed=").strip())
                continue
            level_class_template.append([])
            for class_num in line.split(","):
                level_class_template[-1].append(alien_types[class_num.strip()])
        level_objs = []
        y = CELLSIZE * 2
        for index, row in enumerate(level_class_template):
            level_objs.append([])
            x = WIDTH / 2 - CELLSIZE * len(row) / 2
            for column, alien_class in enumerate(row):
                level_objs[index].append(alien_class(screen, x, y, alien_images[alien_class], bullet_image2))
                x += CELLSIZE
            y += CELLSIZE
        levels.append(Level(aliens=level_objs, alien_speed=level_speed))


small_font = pygame.font.SysFont("monospace", 20)
game = Game(screen, player, levels, 0, pygame.font.SysFont("monospace", 50), small_font)

game.start_level()
clock = pygame.time.Clock()
while True:
    clock.tick(60)
    pygame.display.update()
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    # for row in range(CELLSIZE, WIDTH + 1, CELLSIZE):
    #     pygame.draw.line(screen, (255, 255, 255), (row, 0), (row, HEIGHT))
    #     pygame.draw.line(screen, (255, 255, 255), (0, row), (WIDTH, row))

    game.update_aliens()
    game.check_if_level_done()
    game.show_time_taken()
    player.draw()
    player.show_bullets()
    player.show_health(small_font)

    if game.gameover:
        screen.fill((0, 0, 0))
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
        elif event.type == MOUSEBUTTONDOWN:
            player.shoot()
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                player.shoot()
