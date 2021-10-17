import random


class Sprite:
    def __init__(self, screen, x, y, image, CELLSIZE=50, speed=5):
        self.x = x
        self.y = y
        self.image = image
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
                obj.health -= self.damage
                self.bullets.remove(bullet)
                return True
        return False

    def show_health(self, font):
        text = font.render(f"Health: {self.health}", True, (255, 255, 255))
        self.screen.blit(text, (5, 5))


class StandardAlien(Sprite):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50, damage=10, health=10, bullet_speed=5):
        super().__init__(screen, x, y, image, CELLSIZE, speed=None)
        self.damage = damage
        self.health = health
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


class Bullet(Sprite):
    def move_up(self):
        self.y -= self.speed

    def move_down(self):
        self.y += self.speed


class Game:
    def __init__(self, screen, player, levels, current_level, font, CELLSIZE=50):
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
                if self.player.check_collision(alien):
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
                self.win = True
                self.gameover = True

    def win_screen(self):
        self.show_center_text("You Won!")

    def lose_screen(self):
        self.show_center_text("You Lost!")

    def show_center_text(self, text: str):
        self.screen.fill((0, 0, 0))
        text_obj = self.font.render(text, 1, (255, 255, 255))
        text_width = text_obj.get_width()
        text_height = text_obj.get_height()
        self.screen.blit(text_obj, (self.WIDTH / 2 - text_width / 2, self.HEIGHT / 2 - text_height / 2))


class Level:
    def __init__(self, aliens, alien_speed):
        self.aliens = aliens
        self.alien_speed = alien_speed
