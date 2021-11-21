import sys
import os
import time
from playsound import playsound
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

if "--dev" not in sys.argv[1:]:
    Leaderboard.server_url = "https://space-invaders1.herokuapp.com"


def load_img(path):
    return pygame.transform.scale(pygame.image.load(path), (CELLSIZE, CELLSIZE))


player_image = load_img("assets/images/spaceship.png").convert_alpha()
bullet_image = load_img("assets/images/bullet.png").convert_alpha()
bullet_image2 = pygame.transform.flip(bullet_image, False, True)
standard_alien_image = load_img("assets/images/aliens/alien1.png").convert_alpha()
beefy_alien_image = load_img("assets/images/aliens/alien2.png").convert_alpha()
annoying_alien_image = load_img("assets/images/aliens/alien3.png").convert_alpha()
boss_alien_image = load_img("assets/images/aliens/alien4.png").convert_alpha()
mirror_image = load_img("assets/images/mirror.png").convert_alpha()
background = pygame.image.load("assets/images/background.png").convert_alpha()
icon = pygame.image.load("assets/icon.png")
font_path = "assets/Segoe-UI-Variable-Static-Display.ttf"

shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
shoot_sound.set_volume(0.01)

pygame.display.set_icon(icon)

player = Player(screen=screen, x=WIDTH/2 - CELLSIZE/2, y=HEIGHT - CELLSIZE - 5,
                image=player_image, bullet_image=bullet_image)

levels = []

alien_types = {
    "0": StandardAlien,
    "1": BeefyAlien,
    "2": AnnoyingAlien,
    "3": VeryAnnoyingAlien,
    "4": BossAlien,
    "5": Mirror,
    "x": None
}

alien_images = {
    StandardAlien: standard_alien_image,
    BeefyAlien: beefy_alien_image,
    AnnoyingAlien: annoying_alien_image,
    VeryAnnoyingAlien: annoying_alien_image,
    BossAlien: boss_alien_image,
    Mirror: mirror_image
}

for file in natsort.natsorted(os.listdir("assets/levels/"), alg=natsort.ns.IGNORECASE):
    with open(f"assets/levels/{file}") as level_csv:
        level_class_template = []
        stationary_objs = []
        for line in level_csv:
            if line.startswith("#alien_speed="):
                level_speed = int(line.strip("#alien_speed=").strip())
                continue
            level_class_template.append([
                alien_types[class_num.strip()] for class_num in line.split(",")
            ])
        level_objs = []
        y = CELLSIZE * 2
        for index, row in enumerate(level_class_template):
            level_objs.append([])
            x = WIDTH / 2 - CELLSIZE * len(row) / 2
            for alien_class in row:
                if alien_class is not None:
                    if alien_class != Mirror:
                        level_objs[index].append(alien_class(screen, x, y, alien_images[alien_class], bullet_image2))
                    else:
                        stationary_objs.append(alien_class(screen, x, y, alien_images[alien_class]))
                x += CELLSIZE
            y += CELLSIZE
        levels.append(Level(aliens=level_objs, alien_speed=level_speed, stationary_objs=stationary_objs))


small_font = pygame.font.Font(font_path, 20)
large_font = pygame.font.Font(font_path, 50)
medium_font = pygame.font.Font(font_path, 27)
game = Game(screen, player, levels, 0, small_font, medium_font, large_font, background)

clock = pygame.time.Clock()
while True:
    clock.tick(60)
    pygame.display.update()
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    if game.screen_on == "menu":
        game.main_menu()
    elif game.screen_on == "how_to_play":
        game.how_to_play()
    elif game.screen_on == "leaderboard":
        game.leaderboard()
    elif game.screen_on == "win":
        game.win_screen()
    elif game.screen_on == "lose":
        game.lose_screen()
    elif game.screen_on == "game":
        game.update_aliens()
        game.draw_stationary_objs()
        game.check_stationary_obj_bullet_hits()
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
    elif game.screen_on == "pause":
        game.update_aliens(move=False)
        game.draw_stationary_objs()
        game.check_stationary_obj_bullet_hits()
        game.check_if_level_done()
        game.show_time_taken()
        player.draw()
        player.show_bullets(move=False)
        player.show_health(small_font)
        game.pause_game()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if game.screen_on == "menu":
                game.check_menu_buttons(*pygame.mouse.get_pos())
            elif game.screen_on == "game":
                player.shoot()
                shoot_sound.play()
            elif game.screen_on in ("win", "lose"):
                game.check_gameover_buttons(*pygame.mouse.get_pos())
            elif game.screen_on == "how_to_play":
                game.check_how_to_play_buttons(*pygame.mouse.get_pos())
            elif game.screen_on == "leaderboard":
                game.check_leaderboard_buttons(*pygame.mouse.get_pos())
            elif game.screen_on == "pause":
                game.check_pause_buttons(*pygame.mouse.get_pos())
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                if game.screen_on == "game":
                    player.shoot()
                    shoot_sound.play()
            elif event.key == K_ESCAPE:
                if game.screen_on == "game":
                    game.pause_game()
                elif game.screen_on == "pause":
                    game.screen_on = "game"
