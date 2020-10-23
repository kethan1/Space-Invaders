import pygame, sys, random, math, time
from pygame.locals import *
pygame.init()
screen = pygame.display.set_mode((950,950))
pygame.display.set_caption("Space Invaders")
red = (255,0,0)
green = (0,255,0)
blue = (0, 0, 255)
nblue = (50, 50, 255)
yellow = (255, 235, 0)
brown = (200,100,60)
black = (0,0,0)
white = (255,255,255)
gray = (211,211,211)
screen.fill(nblue)

findnew = True

image1 = pygame.image.load("./space_invader1.png")
image1 = pygame.transform.scale(image1, (80, 60))
image2 = pygame.image.load("./space_invader2.png")
image2 = pygame.transform.scale(image2, (80, 60))
image3 = pygame.image.load("./space_invader3.png")
image3 = pygame.transform.scale(image3, (80, 60))
image4 = pygame.image.load("./Bullet.png")
image4 = pygame.transform.scale(image4, (10, 40))
image5 = pygame.image.load("./spaceship.png")
image5 = pygame.transform.scale(image5, (100, 100))
image6 = pygame.transform.flip(image4, False, True)


def showtext(message, x, y, size):         
    font = pygame.font.SysFont('freesans', int(size))         
    msg = font.render(message, True, white)         
    screen.blit(msg, (x,y))



class Invader:
    
    invader1 = []
    invader2 = []
    invader3 = []
    move = random.choice([-10, 10])

    
    def __init__(self, x, y, pic):
        self.x = x
        self.y = y
        self.pic = pic
        
    def display(self):
        screen.blit(self.pic, (self.x, self.y))
        
    def moveit(self):
        if self in Invader.invader1:
            index = Invader.invader1.index(self)
        elif self in Invader.invader2:
            index = Invader.invader2.index(self)
        elif self in Invader.invader3:
            index = Invader.invader3.index(self)
        self.x+=Invader.move
        if 950-((index*90)+200) <= self.x:
            Invader.move = -10
        elif ((index*90)+200) >= self.x:
            Invader.move = 10
                   
class Bullet:
    
    bullets = []
    
    def __init__(self, x, y, speed, direc, image=image4):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direc
        self.image = image
        Bullet.bullets.append(self)
    def show(self):
        screen.blit(self.image, (self.x, self.y))
    def move(self):
        if self.direction == "up":
            self.y-=self.speed
        else:
            self.y+=self.speed

class User:
    def __init__(self):
        self.x = 10
        self.y = 850
        speed = 15
        self.pic = image5
        self.health = 100
    def shoot(self):
        bullet = Bullet(self.x+45, self.y, 15, "up", image6)
    def display(self):
        screen.blit(self.pic, (self.x, self.y))
    def move(self, direction):
        if direction == "right":
            if self.x < 850:
                self.x+=5
        else:
            if self.x > 0:
                self.x-=5
    def ShowScore(self, x, y, size):         
        font = pygame.font.SysFont('freesans', int(size))         
        msg = font.render(str(self.health), True, white)         
        screen.blit(msg, (x,y))
    def userhit(self):
        self.health-=10

user = User()

a = 200
b = 10
image = image1
thelist = Invader.invader1

for i in range(0, 3):
    for i2 in range(0, 5):
        invader = Invader(a, b, image)
        thelist.append(invader)
        a+=90
    a = 200
    b+=90
    if image == image1:
        image = image2
        thelist = Invader.invader2
    elif image == image2:
        image = image3
        thelist = Invader.invader3
    elif image == image3:
        image = image1

d = time.time()

while True:
    
    user.ShowScore(10, 10, 32)
    
    if len(Invader.invader1)+len(Invader.invader2)+len(Invader.invader3) == 0:
        screen.fill(nblue)
        showtext("You Won", 350, 400, 52)
        showtext("With "+str(user.health)+" Health Points", 265, 450, 52)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
        
    if user.health == 0:
        screen.fill(nblue)
        showtext("You Lost", 350, 400, 52)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
    
    e = time.time()
    
    if 0.295 < e - d > 0.305:
        for Invader in Invader.invader1:
            Invader.moveit()
        for Invader in Invader.invader2:
            Invader.moveit()
        for Invader in Invader.invader3:
            Invader.moveit()
        
    if 0.395 < e - d > 0.405:
        if len(Invader.invader3) > 0:
            for Invader in Invader.invader1:
                Invader.moveit()
            for Invader in Invader.invader2:
                Invader.moveit()
            for Invader in Invader.invader3:
                Invader.moveit()
            shooting = random.choice(Invader.invader3)
            bullet = Bullet(shooting.x+30, shooting.y+40, 10, "down")   
        elif len(Invader.invader2) > 0:
            for Invader in Invader.invader1:
                Invader.moveit()
            for Invader in Invader.invader2:
                Invader.moveit()
            for Invader in Invader.invader3:
                Invader.moveit()
            shooting = random.choice(Invader.invader2)
            bullet = Bullet(shooting.x+30, shooting.y+40, 10, "down")
        elif len(Invader.invader1) > 0:
            for Invader in Invader.invader1:
                Invader.moveit()
            for Invader in Invader.invader2:
                Invader.moveit()
            for Invader in Invader.invader3:
                Invader.moveit()
            shooting = random.choice(Invader.invader1)
            bullet = Bullet(shooting.x+30, shooting.y+40, 10, "down")
        
        d = time.time()
    
    for thing in Invader.invader1:
        thing.display()
        for thing2 in Bullet.bullets:
            if thing.x < thing2.x < thing.x+80:
                if thing.y < thing2.y < thing.y+80:
                    if thing2.direction == "up":
                        Invader.invader1.remove(thing)
                        del thing
                        Bullet.bullets.remove(thing2)
                        del thing2
                        break
                
    for thing in Invader.invader2:
        thing.display()
        for thing2 in Bullet.bullets:
            if thing.x < thing2.x < thing.x+80:
                if thing.y < thing2.y < thing.y+80:
                    if thing2.direction == "up":
                        Invader.invader2.remove(thing)
                        del thing
                        Bullet.bullets.remove(thing2)
                        del thing2
                        break
            
    for thing in Invader.invader3:
        thing.display()
        for thing2 in Bullet.bullets:
            if thing.x < thing2.x < thing.x+80:
                if thing.y < thing2.y < thing.y+80:
                    if thing2.direction == "up":
                        Invader.invader3.remove(thing)
                        del thing
                        Bullet.bullets.remove(thing2)
                        del thing2
                        break
                    
    for thing in Bullet.bullets:
        if user.y < thing.y < user.y+100:
            if user.x < thing.x < user.x+100:
                user.health-=10
                Bullet.bullets.remove(thing)
                del thing
                break
    
    for t2 in Bullet.bullets:
        t2.move()
        t2.show()
        if t2.y > 599:
            del t2
            
    user.display()
    
    pygame.display.update()
    screen.fill(nblue)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                user.shoot()
            if event.key == K_UP:
                user.shoot()
    key = pygame.key.get_pressed()
    if key[K_LEFT]:
        user.move("left")
    if key[K_RIGHT]:
        user.move("right")
