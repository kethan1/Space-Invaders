import random
import datetime


class Sprite:
    def __init__(self, screen, x, y, image, CELLSIZE=50, speed=5):
        self.x = x
        self.y = y
        self.image = image.copy()
        self.speed = speed
        self.screen = screen
        self.CELLSIZE = CELLSIZE

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))

    def move_left(self):
        if self.x >= 0:
            self.x -= self.speed

    def move_right(self):
        w, h = self.screen.get_size()
        if self.x < w - self.image.get_width():
            self.x += self.speed


class Player(Sprite):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50, speed=5, damage=10, health=30, bullet_speed=5):
        super().__init__(screen, x, y, image, CELLSIZE, speed)
        self.damage = damage
        self.health = health
        self.bullets = []
        self.bullet_image = bullet_image
        self.bullet_speed = bullet_speed

    def shoot(self):
        self.bullets.append(Bullet(screen=self.screen, x=self.x, y=self.y - self.CELLSIZE / 2, image=self.bullet_image, speed=self.bullet_speed))

    def show_bullets(self):
        for bullet in self.bullets.copy():
            bullet.draw()
            bullet.move_up()
            if bullet.y < 0 - self.CELLSIZE:
                self.bullets.remove(bullet)

    def check_collision(self, obj):
        for bullet in self.bullets.copy():
            if obj.x <= bullet.x + 20 <= obj.x + obj.image.get_width() and obj.y <= bullet.y + 20 <= obj.y + obj.image.get_height():
                obj.set_health(obj.health - self.damage)
                self.bullets.remove(bullet)
                return True
        return False

    def show_health(self, font):
        text = font.render(f"Health: {self.health}", True, (255, 255, 255))
        self.screen.blit(text, (5, 5))


class AlienTemplate(Sprite):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50, damage=10, health=10, bullet_speed=5):
        super().__init__(screen, x, y, image, CELLSIZE, speed=None)
        self.damage = damage
        self.health = health
        self.full_health = health
        self.bullets = []
        self.bullet_image = bullet_image
        self.bullet_speed = bullet_speed
        self.WIDTH = screen.get_width()

    def shoot(self):
        self.bullets.append(
            Bullet(screen=self.screen, x=self.x, y=self.y + self.CELLSIZE / 2,
                   image=self.bullet_image, speed=self.bullet_speed)
        )

    def move_down_row(self):
        self.y += self.CELLSIZE

    def show_bullets(self):
        for bullet in self.bullets.copy():
            bullet.draw()
            bullet.move_down()
            if bullet.y > self.WIDTH:
                self.bullets.remove(bullet)

    def check_collision(self, player):
        for bullet in self.bullets.copy():
            if player.x <= bullet.x + 20 <= player.x + player.image.get_width() and player.y <= bullet.y + 20 <= player.y + player.image.get_height():
                player.health -= self.damage
                self.bullets.remove(bullet)
                return True
        return False

    def move(self, move_by):
        self.x += move_by

    def set_health(self, health):
        self.health = health
        self.image.set_alpha(round((self.health / self.full_health) * 255))


class StandardAlien(AlienTemplate):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50):
        super().__init__(screen, x, y, image, bullet_image, damage=10, CELLSIZE=CELLSIZE, health=10, bullet_speed=5)


class BeefyAlien(AlienTemplate):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50):
        super().__init__(screen, x, y, image, bullet_image, damage=15, CELLSIZE=CELLSIZE, health=40, bullet_speed=5)


class AnnoyingAlien(AlienTemplate):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50):
        super().__init__(screen, x, y, image, bullet_image, damage=5, CELLSIZE=CELLSIZE, health=5, bullet_speed=10)


class BossAlien(AlienTemplate):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50):
        super().__init__(screen, x, y, image, bullet_image, damage=30, CELLSIZE=CELLSIZE, health=100, bullet_speed=5)


class Bullet(Sprite):
    def move_up(self):
        self.y -= self.speed

    def move_down(self):
        self.y += self.speed


class Game:
    def __init__(self, screen, player, levels, current_level, font, small_font, CELLSIZE=50):
        self.screen = screen
        self.player = player
        self.levels = levels
        self.current_level = current_level
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.CELLSIZE = CELLSIZE
        self.current_level_data = self.levels[self.current_level]
        self.gameover = False
        self.win = False
        self.font = font
        self.small_font = small_font

    def update_aliens(self):
        already_reversed = False
        for row in self.current_level_data.aliens:
            for alien in row:
                if alien.y >= self.HEIGHT - self.CELLSIZE:
                    self.gameover = True
                if alien.x <= 0 or alien.x >= self.WIDTH - self.CELLSIZE:
                    if not already_reversed:
                        self.current_level_data.alien_speed = -self.current_level_data.alien_speed
                    already_reversed = True
                    break
            if already_reversed:
                break

        aliens_copy = self.current_level_data.aliens.copy()
        for index, row in enumerate(aliens_copy):
            for alien in row.copy():
                if self.player.check_collision(alien) and alien.health <= 0:
                    row.remove(alien)
                    if row == []:
                        self.current_level_data.aliens.remove([])
                        continue
                alien.move(self.current_level_data.alien_speed)
                alien.draw()
                if already_reversed:
                    alien.move_down_row()
                if random.randint(1, 200) == 1 and len(aliens_copy) == index + 1:
                    alien.shoot()
                alien.show_bullets()
                alien.check_collision(self.player)
        if self.player.health <= 0:
            self.gameover = True

    def check_if_level_done(self):
        if sum(map(len, self.current_level_data.aliens)) == 0:
            if self.current_level < len(self.levels) - 1:
                self.current_level += 1
                self.current_level_data = self.levels[self.current_level]
            else:
                if not self.gameover:
                    self.end_level()
                self.win = True
                self.gameover = True

    def main_menu(self):
        self.show("Space Invaders")

    def win_screen(self):
        self.show_text("You Won!", y=self.HEIGHT / 2 - self.font.size("You Won!")[1])
        self.show_text(f"Time taken: {self.get_time_taken()}", y=self.HEIGHT / 2)

    def start_level(self):
        self.player.health = 30
        self.current_level_data = self.levels[self.current_level]
        self.start_time = datetime.datetime.now()

    def end_level(self):
        self.end_time = datetime.datetime.now()

    def lose_screen(self):
        self.show_text("You Lost!")

    def show_text(self, text: str, x=None, y=None):
        text_obj = self.font.render(text, 1, (255, 255, 255))
        text_width, text_height = text_obj.get_width(), text_obj.get_height()
        if y is None:
            y = self.HEIGHT / 2 - text_height / 2
        if x is None:
            x = self.WIDTH / 2 - text_width / 2
        self.screen.blit(text_obj, (x, y))

    def get_time_taken(self, end_time=None):
        if end_time is None:
            end_time = self.end_time
        return str((end_time - self.start_time)).split('.')[0]

    def show_time_taken(self):
        text_obj = self.small_font.render(f"Time Taken: {self.get_time_taken(datetime.datetime.now())}", 1, (255, 255, 255))
        width = text_obj.get_width()
        self.screen.blit(text_obj, (self.WIDTH - width - 5, 5))


class Level:
    def __init__(self, aliens, alien_speed):
        self.aliens = aliens
        self.alien_speed = alien_speed
