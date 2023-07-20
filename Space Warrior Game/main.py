import math
import random
import mysql.connector

import pygame
from pygame import mixer

# MySQL connectivity
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1608",
  database="score"
)

# Intialize the pygame
pygame.init()

# create the screen
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load('background.png')

# Main page
main_text1 = pygame.font.Font('ChrustyRock.ttf', 64)
main_text2 = pygame.font.Font('ChrustyRock.ttf', 64)

# Sound
mixer.music.load("background.wav")
mixer.music.play(-1)

# Caption and Icon
pygame.display.set_caption("Space Warriors")
icon = pygame.image.load('logo.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('spaceship.png')
playerX = 370
playerY = 480
playerX_change = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

def enemy_generator():
    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load('enemy.png'))
        enemyX.append(random.randint(0, 736))
        enemyY.append(random.randint(50, 150))
        enemyX_change.append(4)
        enemyY_change.append(40)

# Bullet

# Ready - You can't see the bullet on the screen
# Fire - The bullet is currently moving

bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 20
bullet_state = "ready"

# Score
score_value = 0
highscore=[]
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
testY = 10

# Game Over
over_font = pygame.font.Font('ChrustyRock.ttf', 64)


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    screen.blit(background,(0,0))
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (220, 200))
    show_score(330,295)
    replay = font.render("Press 'Space' to Play Again", True, (255,255,255))
    screen.blit(replay, (200,450))


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))
    
def highscore_db():
    mycursor = mydb.cursor()
    sql = "INSERT INTO mytb VALUES (%s)"
    val = (score_value,)
    mycursor.execute(sql, val)
    mydb.commit()
    
def show_highscore():
    highscore=[]
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM mytb")
    myresult = mycursor.fetchall()
    for row in myresult:
        l=list(row)
        highscore.append(l[0])
    score = font.render("High Score : " + str(max(highscore)), True, (255, 255, 255))
    screen.blit(score, (290,325))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False
    
game_state = False
over = False

# Game Loop
running = True
while running:

    if game_state:
        # RGB = Red, Green, Blue
        screen.fill((0, 0, 0))
        # Background Image
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # if keystroke is pressed check whether its right or left
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    playerX_change = -5
                if event.key == pygame.K_RIGHT:
                    playerX_change = 5
                if event.key == pygame.K_SPACE:
                    if bullet_state == "ready":
                        bulletSound = mixer.Sound("laser.wav")
                        bulletSound.play()
                        # Get the current x cordinate of the spaceship
                        bulletX = playerX
                        fire_bullet(bulletX, bulletY)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0

        # 5 = 5 + -0.1 -> 5 = 5 - 0.1
        # 5 = 5 + 0.1

        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        # Enemy Movement
        for i in range(num_of_enemies):

            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = 4
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 736:
                enemyX_change[i] = -4
                enemyY[i] += enemyY_change[i]
            

            # Collision
            collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                explosionSound = mixer.Sound("explosion.wav")
                explosionSound.play()
                bulletY = 480
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 736)
                enemyY[i] = random.randint(50, 150)
            
            enemy(enemyX[i], enemyY[i], i)
            
            
        # Game Over
            if enemyY[i] > 440:
                enemyImg=[]
                for i in range(num_of_enemies):
                    enemyY[i]=random.randint(50, 150)
                over = True
                game_state = False
                highscore_db()
                break
            

        
        # Bullet Movement
        if bulletY <= 0:
            bulletY = 480
            bullet_state = "ready"

        if bullet_state == "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change

        player(playerX, playerY)
        show_score(textX, testY)
    else:
        if over:
            screen.fill((230,234,96))
            screen.blit(background,(0,0))
            game_over_text()
            show_highscore()
        else: 
            screen.fill((230,234,96))
            screen.blit(background,(0,0))
            main_text1 = over_font.render("SPACE", True, (255, 255, 255))
            screen.blit(main_text1, (290, 100))
            main_text2 = over_font.render("WARRIORS", True, (255, 255, 255))
            screen.blit(main_text2, (220, 170))
            btn = pygame.image.load("play-button.png")
            screen.blit(btn, (350,280))
            start = font.render("Press 'Space' to Start", True, (255,255,255))
            screen.blit(start, (230,450))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = True
                    over = False
                    enemy_generator()
                    score_value=0
    pygame.display.update()

