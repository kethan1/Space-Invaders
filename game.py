import sys
import os
import natsort
import pygame
from pygame.locals import *
from sprites import *

CELLSIZE = 40
WIDTH = 800
HEIGHT = 600

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

player_image = pygame.transform.scale(pygame.image.load("assets/images/spaceship.png"), (CELLSIZE, CELLSIZE))
bullet_image = pygame.transform.scale(pygame.image.load("assets/images/bullet.png"), (CELLSIZE, CELLSIZE))
bullet_image2 = pygame.transform.flip(bullet_image, False, True)
standard_alien_image = pygame.transform.scale(pygame.image.load("assets/images/aliens/alien1.png"), (CELLSIZE, CELLSIZE))
beefy_alien_image = pygame.transform.scale(pygame.image.load("assets/images/aliens/alien2.png"), (CELLSIZE, CELLSIZE))
annoying_alien_image = pygame.transform.scale(pygame.image.load("assets/images/aliens/alien3.png"), (CELLSIZE, CELLSIZE))
boss_alien_image = pygame.transform.scale(pygame.image.load("assets/images/aliens/alien4.png"), (CELLSIZE, CELLSIZE))
background = pygame.transform.scale(pygame.image.load("assets/images/background.png"), (WIDTH, HEIGHT)).convert_alpha()
font_path = "assets/Segoe-UI-Variable-Static-Display.ttf"


player = Player(screen=screen, x=WIDTH/2 - CELLSIZE/2, y=HEIGHT - CELLSIZE - 5,
                image=player_image, bullet_image=bullet_image)

levels = []

alien_types = {
    "0": StandardAlien,
    "1": BeefyAlien,
    "2": AnnoyingAlien,
    "3": VeryAnnoyingAlien,
    "4": BossAlien
}

alien_images = {
    StandardAlien: standard_alien_image,
    BeefyAlien: beefy_alien_image,
    AnnoyingAlien: annoying_alien_image,
    VeryAnnoyingAlien: annoying_alien_image,
    BossAlien: boss_alien_image
}

for file in natsort.natsorted(os.listdir("assets/levels/"), alg=natsort.ns.IGNORECASE):
    with open(f"assets/levels/{file}") as level1_csv:
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


small_font = pygame.font.Font(font_path, 20)
large_font = pygame.font.Font(font_path, 50)
game = Game(screen, player, levels, 0, large_font, small_font)

clock = pygame.time.Clock()
while True:
    clock.tick(60)
    pygame.display.update()
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    if game.screen_on == "menu":
        game.main_menu()
    elif game.screen_on == "win":
        game.win_screen()
    elif game.screen_on == "lose":
        game.lose_screen()
    elif game.screen_on == "game":
        game.update_aliens()
        game.check_if_level_done()
        game.show_time_taken()
        player.draw()
        player.show_bullets()
        player.show_health(small_font)

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
            if game.screen_on == "menu":
                game.check_menu_buttons(*pygame.mouse.get_pos())
            elif game.screen_on == "game":
                player.shoot()
            elif game.screen_on in ("win", "lose"):
                game.check_gameover_buttons(*pygame.mouse.get_pos())
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                player.shoot()
