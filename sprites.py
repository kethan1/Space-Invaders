import random
import datetime
import pygame
import math
import requests
import tkinter as tk
import tkinter.simpledialog

root = tk.Tk()
root.withdraw()


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
        if self.x >= self.speed:
            self.x -= self.speed
        elif self.x >= 0:
            self.x = 0

    def move_right(self):
        if self.x < self.screen.get_width() - self.image.get_width():
            self.x += self.speed


class Player(Sprite):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50, speed=5,
                 damage=10, health=30, bullet_speed=5):
        super().__init__(screen, x, y, image, CELLSIZE, speed)
        self.damage = damage
        self.health = health
        self.bullets = []
        self.bullet_image = bullet_image
        self.bullet_speed = bullet_speed

    def shoot(self):
        self.bullets.append(Bullet(screen=self.screen, x=self.x,
                                   y=self.y - self.CELLSIZE / 2,
                                   image=self.bullet_image,
                                   speed=self.bullet_speed))

    def show_bullets(self, move=True):
        for bullet in self.bullets.copy():
            bullet.draw()
            if move:
                bullet.move_up()
                if bullet.y < 0 - self.CELLSIZE:
                    self.bullets.remove(bullet)

    def check_collision(self, obj):
        for bullet in self.bullets.copy():
            if obj.x <= bullet.x + 20 <= obj.x + obj.image.get_width() and \
              obj.y <= bullet.y + 20 <= obj.y + obj.image.get_height():
                obj.set_health(obj.health - self.damage)
                self.bullets.remove(bullet)
                return True
        return False

    def show_health(self, font):
        text = font.render(f"Health: {self.health}", True, (255, 255, 255))
        self.screen.blit(text, (5, 5))


class AlienTemplate(Sprite):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50,
                 damage=10, health=10, bullet_speed=5, shoot_probability=200):
        super().__init__(screen, x, y, image, CELLSIZE, speed=None)
        self.damage = damage
        self.health = health
        self.full_health = health
        self.bullets = []
        self.bullet_image = bullet_image
        self.bullet_speed = bullet_speed
        self.shoot_probability = shoot_probability
        self.WIDTH = screen.get_width()
        self.CELLSIZE = CELLSIZE

    def shoot(self):
        self.bullets.append(
            Bullet(screen=self.screen, x=self.x, y=self.y + self.CELLSIZE / 2,
                   image=self.bullet_image, speed=self.bullet_speed)
        )

    def shoot_prob(self):
        return random.randint(1, self.shoot_probability) == 1

    def move_down_row(self):
        self.y += self.CELLSIZE

    def show_bullets(self, move=True):
        for bullet in self.bullets.copy():
            bullet.draw()
            if move:
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

    def copy(self):
        return AlienTemplate(self.screen, self.x, self.y, self.image, self.bullet_image, self.CELLSIZE, self.damage, self.health, self.bullet_speed, self.shoot_probability)


class StandardAlien(AlienTemplate):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50):
        super().__init__(screen, x, y, image, bullet_image, damage=10,
                         CELLSIZE=CELLSIZE, health=10, bullet_speed=5)


class BeefyAlien(AlienTemplate):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50):
        super().__init__(screen, x, y, image, bullet_image, damage=15,
                         CELLSIZE=CELLSIZE, health=40, bullet_speed=5)


class AnnoyingAlien(AlienTemplate):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50):
        super().__init__(screen, x, y, image, bullet_image, damage=5,
                         CELLSIZE=CELLSIZE, health=5, bullet_speed=10,
                         shoot_probability=125)


class VeryAnnoyingAlien(AlienTemplate):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50):
        super().__init__(screen, x, y, image, bullet_image, damage=5,
                         CELLSIZE=CELLSIZE, health=5, bullet_speed=10,
                         shoot_probability=75)


class BossAlien(AlienTemplate):
    def __init__(self, screen, x, y, image, bullet_image, CELLSIZE=50):
        super().__init__(screen, x, y, image, bullet_image, damage=30,
                         CELLSIZE=CELLSIZE, health=100, bullet_speed=5)


class Bullet(Sprite):
    def move_up(self):
        self.y -= self.speed

    def move_down(self):
        self.y += self.speed


class Game:
    def __init__(self, screen, player, levels, current_level, small_font, medium_font, big_font, bg_image, CELLSIZE=50):
        self.screen = screen
        self.player = player
        self.levels = levels
        self.current_level = current_level
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.CELLSIZE = CELLSIZE
        self.current_level_data = self.levels[self.current_level]
        self.small_font = small_font
        self.medium_font = medium_font
        self.font = big_font
        self.bg_image = bg_image
        self.screen_on = "menu"
        self.signup_clicked = False
        self.login_clicked = False

        self.level_buttons = []
        width_of_levels = len(self.levels[:5])
        if width_of_levels % 2 == 0:
            left_button_start = self.WIDTH / 2 - (width_of_levels / 2) * 150
        else:
            left_button_start = (self.WIDTH / 2 - (width_of_levels // 2) * 150) - 50
        for index, _ in enumerate(self.levels):
            self.level_buttons.append(
                DefaultButton(
                    text=f"Level {index + 1}", font=self.small_font,
                    screen=self.screen, x=left_button_start + (index % 5 * 150),
                    y=self.HEIGHT / 2 + (math.floor(index / 5) * 100) - 100,
                    width=100, height=50, on_click=lambda i=index: self.start_level(i)
                )
            )

        def initial_leaderboard_func():
            self.top_scores = Leaderboard.get_top_scores(10)
            self.leaderboard()

        self.level_buttons += [
            DefaultButton(
                text=f"How To Play", font=self.small_font,
                screen=self.screen, x=self.WIDTH / 2 - 125 / 2 - 80,
                y=self.HEIGHT / 2 + (math.floor(index / 5) * 100) + 15,
                width=125, height=50, on_click=self.how_to_play
            ),
            DefaultButton(
                text=f"Leaderboard", font=self.small_font,
                screen=self.screen, x=self.WIDTH / 2 - 125 / 2 + 80,
                y=self.HEIGHT / 2 + (math.floor(index / 5) * 100) + 15,
                width=125, height=50, on_click=initial_leaderboard_func
            )
        ]

        width = 110
        self.gameover_buttons = [
            DefaultButton(
                text="Restart", font=self.small_font,
                screen=self.screen, x=(self.WIDTH / 2 - width / 2) + 100,
                y=self.HEIGHT / 2,
                width=width, height=50, on_click=self.start_level
            ),
            DefaultButton(
                text="Main Menu", font=self.small_font,
                screen=self.screen, x=(self.WIDTH / 2 - width / 2) - 100,
                y=self.HEIGHT / 2,
                width=width, height=50, on_click=self.main_menu
            )
        ]

        self.how_to_play_buttons = [
            DefaultButton(
                text="Main Menu", font=self.small_font, screen=self.screen,
                x=self.WIDTH / 2 - width / 2, y=self.HEIGHT / 2 + 60, width=width, height=50,
                on_click=self.main_menu
            )
        ]

        self.leaderboard_buttons = [
            DefaultButton(
                text=f"Refresh", font=self.small_font,
                screen=self.screen, x=self.WIDTH / 2 - 125 / 2 - 80,
                y=self.HEIGHT / 2 + (math.floor(index / 5) * 100) + 15,
                width=125, height=50, on_click=self.refresh_leaderboard
            ),
            DefaultButton(
                text=f"Main Menu", font=self.small_font,
                screen=self.screen, x=self.WIDTH / 2 - 125 / 2 + 80,
                y=self.HEIGHT / 2 + (math.floor(index / 5) * 100) + 15,
                width=125, height=50, on_click=self.main_menu
            ),
            DefaultButton(
                text=f"Sign Up", font=self.small_font,
                screen=self.screen, x=self.WIDTH / 2 - 125 / 2 - 80,
                y=self.HEIGHT / 2 + (math.floor(index / 5) * 100) + 75,
                width=125, height=50, on_click=lambda s=self: s.signup_clicked_func()
            ),
            DefaultButton(
                text=f"Login", font=self.small_font,
                screen=self.screen, x=self.WIDTH / 2 - 125 / 2 + 80,
                y=self.HEIGHT / 2 + (math.floor(index / 5) * 100) + 75,
                width=125, height=50, on_click=lambda s=self: s.login_clicked_func()
            )
        ]

        self.pause_buttons = [
            DefaultButton(
                text=f"Resume", font=self.small_font,
                screen=self.screen, x=self.WIDTH / 2 - 125 / 2,
                y=self.HEIGHT / 2 - 50 / 2 - 30,
                width=125, height=50, on_click=lambda: self.screen_on_game()
            ),
            DefaultButton(
                text=f"Main Menu", font=self.small_font,
                screen=self.screen, x=self.WIDTH / 2 - 125 / 2,
                y=self.HEIGHT / 2 - 50 / 2 + 50,
                width=125, height=50, on_click=self.main_menu
            )
        ]

    def screen_on_game(self):
        self.screen_on = "game"

    def signup_clicked_func(self):
        self.signup_clicked = True

    def login_clicked_func(self):
        self.login_clicked = True

    def refresh_leaderboard(self, amount=10):
        self.top_scores = Leaderboard.get_top_scores(amount)

    def pause_game(self):
        self.screen_on = "pause"
        pygame.draw.rect(self.screen, (160, 160, 160), (self.WIDTH / 2 - 300 / 2, self.HEIGHT / 2 - 300 / 2, 300, 300))
        for button in self.pause_buttons:
            button.draw()

    def how_to_play(self):
        self.screen_on = "how_to_play"
        self.show_text("How to Play", y=20)
        self.show_text("Use the Arrow Keys to Move the Player Left and Right", y=self.HEIGHT / 2 - 30, font=self.small_font)
        self.show_text("Use the Spacebar or Click to Shoot", y=self.HEIGHT / 2 + 10, font=self.small_font)
        for button in self.how_to_play_buttons:
            button.draw()

    def leaderboard(self):
        self.screen_on = "leaderboard"
        self.show_text("Leaderboard", y=20)
        top_scores = self.top_scores
        if top_scores:
            for index, (name, score) in enumerate(top_scores):
                self.show_text(f"{index + 1}. {score} - {name}", y=100 + 35 * index, font=self.medium_font)
        elif top_scores == {}:
            self.show_text("No Scores Yet", y=100, font=self.medium_font)
        else:
            self.show_text("The Scores Could Not Be Retrieved", y=100, font=self.medium_font)
        if self.signup_clicked:
            result = TwoTextInputDialog(root, "Username", "Password").get_text()
            finished = False
            while not finished:
                if result is None:
                    finished = True
                elif Leaderboard.signup(*result):
                    result = TwoTextInputDialog(root, "Username", "Password", "An Account With That Username Already Exists").get_text()
                else:
                    finished = True
                    Leaderboard.current_account = result[0]
            self.signup_clicked = False
        elif self.login_clicked:
            result = TwoTextInputDialog(root, "Username", "Password").get_text()
            finished = False
            while not finished:
                if result is None:
                    finished = True
                elif Leaderboard.login(*result):
                    result = TwoTextInputDialog(root, "Username", "Password", "An Account With That Info Does Not Exist").get_text()
                else:
                    Leaderboard.current_account = result[0]
                    finished = True
            self.login_clicked = False
        for button in self.leaderboard_buttons:
            button.draw()

    def update_aliens(self, move=True):
        already_reversed = False
        for row in self.current_level_data.aliens:
            for alien in row:
                if alien.y >= self.HEIGHT - self.CELLSIZE:
                    self.screen_on = "lose"
                if alien.x <= 0 or alien.x >= self.WIDTH - self.CELLSIZE:
                    if not already_reversed:
                        if move:
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
                if move:
                    alien.move(self.current_level_data.alien_speed)
                alien.draw()
                if already_reversed:
                    if move:
                        alien.move_down_row()
                if alien.shoot_prob() and len(aliens_copy) == index + 1 and move:
                    alien.shoot()
                alien.show_bullets(move)
                alien.check_collision(self.player)
        if self.player.health <= 0:
            self.screen_on = "lose"

    def check_if_level_done(self):
        if sum(map(len, self.current_level_data.aliens)) == 0 and self.screen_on not in ("win", "lose"):
            self.end_level()
            self.screen_on = "win"
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.bg_image, (0, 0))
            self.win_screen()
            pygame.display.update()
            if Leaderboard.current_account is not None:
                score_added = Leaderboard.add_score(self.get_time_taken(), f"level{self.current_level + 1}")
                if score_added is None:
                    tk.messagebox.showerror(message="Unable to Submit Score. Check That You Are Connected to the Internet.")
                elif not score_added:
                    tk.messagebox.showerror(message="An Account With That Info Does Not Exist.")
            else:
                button_clicked = ThreeButtonInfo(root, "Login", "Signup", "Cancel", "Login or Signup to Post a Score").button_clicked
                if button_clicked == 1:  # Login
                    result = TwoTextInputDialog(root, "Username", "Password").get_text()
                    finished = False
                    while not finished:
                        if result is not None:
                            login_result = Leaderboard.login(*result)
                            if login_result:
                                result = TwoTextInputDialog(root, "Username", "Password", "An Account With That Info Does Not Exists").get_text()
                            elif login_result is None:
                                finished = True
                                tk.messagebox.showerror(message="Unable to Login. Check That You Are Connected to the Internet.")
                            else:
                                finished = True
                                Leaderboard.current_account = result[0]
                        else:
                            finished = True
                elif button_clicked == 2:  # Signup
                    result = TwoTextInputDialog(root, "Username", "Password").get_text()
                    finished = False
                    while not finished:
                        if result is not None:
                            signup_result = Leaderboard.signup(*result)
                            if signup_result:
                                result = TwoTextInputDialog(root, "Username", "Password", "An Account With That Username Already Exists").get_text()
                            elif signup_result is None:
                                finished = True
                                tk.messagebox.showerror(message="Unable to Sign Up. Check That You Are Connected to the Internet.")
                            else:
                                finished = True
                                Leaderboard.current_account = result[0]
                        else:
                            finished = True
                elif button_clicked == 3:  # Cancel
                    pass

                if Leaderboard.current_account is not None:
                    if not Leaderboard.add_score(self.get_time_taken(), f"level{self.current_level + 1}"):
                        tk.messagebox.showerror(message="Unable to Submit Score. Check That You Are Connected to the Internet.")

    def next_level(self):
        self.current_level += 1
        self.current_level_data = self.levels[self.current_level]

    def main_menu(self):
        self.screen_on = "menu"
        self.show_text("Space Invaders", y=20)
        for button in self.level_buttons:
            button.draw()

    def win_screen(self):
        self.show_text("You Won!", y=self.font.size("You Won!")[1] + 50)
        self.show_text(f"Time taken: {self.get_time_taken()}", y=self.font.size("You Won!")[1] + self.font.size("T")[1] + 50)
        for button in self.gameover_buttons:
            button.draw()

    def lose_screen(self):
        self.show_text("You Lost!", y=self.font.size("You Lost!")[1] + 100)
        for button in self.gameover_buttons:
            button.draw()

    def start_level(self, level=None):
        self.current_level_data.alien_speed = abs(self.current_level_data.alien_speed)
        self.screen_on = "game"
        self.player.health = 30
        self.player.bullets = []
        self.current_level_data = self.levels[level if level is not None else self.current_level]
        self.current_level_data.reset_level()
        for row in self.current_level_data.aliens:
            for alien in row:
                alien.bullets = []
        if level is not None:
            self.current_level = level
        self.start_time = datetime.datetime.now()

    def end_level(self):
        self.end_time = datetime.datetime.now()

    def show_text(self, text: str, x=None, y=None, font=None):
        if font is None:
            font = self.font
        text_obj = font.render(text, 1, (255, 255, 255))
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

    def check_menu_buttons(self, x, y):
        return any(button.check_click(x, y) for button in self.level_buttons)

    def check_gameover_buttons(self, x, y):
        return any(button.check_click(x, y) for button in self.gameover_buttons)

    def check_how_to_play_buttons(self, x, y):
        return any(button.check_click(x, y) for button in self.how_to_play_buttons)

    def check_leaderboard_buttons(self, x, y):
        return any(button.check_click(x, y) for button in self.leaderboard_buttons)

    def check_pause_buttons(self, x, y):
        return any(button.check_click(x, y) for button in self.pause_buttons)


class Level:
    def __init__(self, aliens, alien_speed):
        self.aliens = [[alien.copy() for alien in row] for row in aliens]
        self.original_aliens = aliens
        self.alien_speed = alien_speed

    def reset_level(self):
        self.aliens = [[alien.copy() for alien in row] for row in self.original_aliens]


class Button:
    def __init__(self, screen, x, y, width, height, on_click, color, rounded=0, border=0, border_color=(0, 0, 0)):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on_click = on_click
        self.color = color
        self.rounded = rounded
        self.border = border
        self.border_color = border_color

    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height), border_radius=self.rounded)
        if self.border != 0:
            pygame.draw.rect(self.screen, self.border_color, (self.x, self.y, self.width, self.height), border_radius=self.rounded, width=int(self.border * 2))

    def check_click(self, x, y):
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            self.on_click()
            return True
        return False


class ButtonWithText(Button):
    def __init__(self, screen, x, y, width, height, on_click, color, font, text="", rounded=0,  border=0, border_color=None, text_color=(255, 255, 255)):
        super().__init__(screen, x, y, width, height, on_click, color, rounded, border, border_color)
        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self):
        super().draw()
        text_obj = self.font.render(self.text, 1, self.text_color)
        text_width, text_height = text_obj.get_width(), text_obj.get_height()
        self.screen.blit(text_obj, (self.x + self.width / 2 - text_width / 2, self.y + self.height / 2 - text_height / 2))


class DefaultButton(ButtonWithText):
    def __init__(self, screen, x, y, width, height, on_click, font, text):
        super().__init__(screen, x, y, width, height, on_click, (70, 70, 70), font, text, 7,  1.5, (10, 10, 10))


class Leaderboard:
    server_url = "http://localhost:5000"
    cache_scores = []
    current_account = None

    @classmethod
    def get_top_scores(cls, amount, level="level1", refresh_cache=True):
        if not refresh_cache:
            if len(cls.cache_scores) >= amount:
                return cls.cache_scores[:amount]
            else:
                refresh_cache = True
        if refresh_cache:
            try:
                cls.cache_scores = requests.post(cls.server_url + "/get_scores", json={"amount": amount, "level": level}).json()["scores"]
            except requests.exceptions.RequestException:
                return False

        cls.cache_scores = list(sorted(cls.cache_scores, key=lambda x: x[1]))
        return cls.cache_scores

    @classmethod
    def add_score(cls, time, level):
        if cls.current_account is not None:
            try:
                requests.post(cls.server_url + "/add_score", json={"time": time, "name": cls.current_account, "level": level})
            except requests.exceptions.RequestException:
                return False
            return True
        return None

    @classmethod
    def login(cls, username, password):
        try:
            return requests.post(cls.server_url + "/login", json={"username": username, "password": password}).json()["incorrect_info"]
        except requests.exceptions.RequestException:
            pass

    @classmethod
    def signup(cls, username, password):
        try:
            return requests.post(cls.server_url + "/signup", json={"username": username, "password": password}).json()["already_exists"]
        except requests.exceptions.RequestException:
            pass


class TwoTextInputDialog(tk.simpledialog.Dialog):
    def __init__(self, master, first_label, second_label, extra_text=None, title=None):
        self.first_label = first_label
        self.second_label = second_label
        self.master = master
        self.extra_text = extra_text
        super().__init__(master, title)

    def body(self, master):
        tk.Label(master, text=f"{self.first_label}: ").grid(row=0)
        if self.second_label == "Password":
            tk.Label(master, text=f"{self.second_label}: ").grid(row=1)
            self.e2 = tk.Entry(master, show="•")
        if self.extra_text is not None:
            tk.Label(master, text=self.extra_text).grid(row=2)

        self.e1 = tk.Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1  # initial focus

    def apply(self):
        first = self.e1.get()
        second = self.e2.get()
        self.data = [first, second]

    def validate(self):
        first = self.e1.get()
        second = self.e2.get()
        if first and second:
            return 1
        else:
            return 0

    def get_text(self):
        try:
            return self.data
        except AttributeError:  # User clicked cancel
            return None


class ThreeButtonInfo(tk.simpledialog.Dialog):
    def __init__(self, master, button1_text, button2_text, button3_text, info=None, title=None):
        self.button1_text = button1_text
        self.button2_text = button2_text
        self.button3_text = button3_text
        self.button_clicked = None
        self.master = master
        self.info = info
        super().__init__(master, title)

    def body(self, master):
        if self.info is not None:
            tk.Label(master, text=self.info).grid(row=2)

        return None  # initial focus

    def buttonbox(self):
        box = tk.Frame(self)

        w = tk.Button(box, text=self.button1_text, width=10, command=self.button1_clicked, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text=self.button2_text, width=10, command=self.button2_clicked)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text=self.button3_text, width=10, command=self.button3_clicked)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.button1_clicked)
        self.bind("<Escape>", self.button3_clicked)

        box.pack()

    def button1_clicked(self):
        self.button_clicked = 1
        self.ok()

    def button2_clicked(self):
        self.button_clicked = 2
        self.cancel()

    def button3_clicked(self):
        self.button_clicked = 3
        self.cancel()
