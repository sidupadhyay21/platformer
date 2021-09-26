import pgzrun
import json
from pygame import transform
import random
from HelperTools import *

"""
installing pygame & pgzero libraries

1. launch command prompt (cmd) as admin
2. enter the following command: python -m pip install --upgrade pygame pgzero
            note: might need to use "python3" instead of "python"

"""

#TODO - need to fix hazard factory
numberRows = 20
numberCols = 20
testTiles = TileSet('images/super_mario_tileset.png', numberRows , numberCols,alphaCheck=(339,339), scale = 2, padding=1)

currentLevel = 0
mapRows = 15
mapColumns = 40
viewColumns = 20
mapTop = 0
mapLeft = 0
WIDTH = viewColumns*testTiles.tileSize
HEIGHT = mapRows*testTiles.tileSize
GRAVITY = 4
MAX_FALL_SPEED = testTiles.tileSize
FLOOR = HEIGHT - 120
scrollAmount = 0
gameover = False
win = False
max_x = WIDTH - 100
min_x = 100

runSpeed = 10
jumpAmount = 40
lives = 5

retryBox = Rect(WIDTH/2 - 50, HEIGHT/2 + 150, 100, 30)

hazardList = []
selectedTile = None 

sectionList = [0, 5, 10, 15, 200, 205, 210, 215]
section = 0

class Tile:
    def ConvertTileToWorld(row, column):
        return column * testTiles.tileSize + testTiles.tileSize//2, row * testTiles.tileSize - testTiles.tileSize//2
    
    def __init__(self, left, top, imgNum, size = 32):
        self.left = left
        self.top = top
        self.imgNum = imgNum
        self.type = "clear"
        self.size = size
        self.rect = Rect(self.left, self.top, self.size, self.size)

    def getScreenPosition(self):
        return (self.left - scrollAmount, self.top)

    def draw(self, screen, scroll = 0):
        testTiles.drawTile(screen, self.left - scrollAmount, self.top, self.imgNum)

class AnimationSprite:
    def __init__(self, imageList, framesPerImage = 10):
        self.imageList = imageList
        self.framesPerImage = framesPerImage
        self.currentImage = 0
        self.lastUpdate = 0
        self.totalFrames = 0
        self.actor = self.imageList[0]
        self.fps = 60

    def updatePosition(self, pos):
        for actor in self.imageList:
            actor.pos = pos

    def currentActor(self):
        self.actor = self.imageList[self.currentImage]
        return self.actor

    def get_top(self):
        return self.actor.top

    def get_bottom(self):
        return self.actor.bottom

    def update(self):
        self.totalFrames += 1
        self.currentImage = round(self.totalFrames / self.framesPerImage) % len(self.imageList)
        self.actor = self.imageList[self.currentImage]

    def draw(self, screen, facingRight = True):
        self.actor = self.imageList[self.currentImage]
        if facingRight:
            self.actor.draw()
        else:
            flipped_image = transform.flip(self.actor._surf, True, False)
            screen.blit(flipped_image, self.actor.topleft)

class HazardSpawn:
    def __init__(self, row, col, spawn_rate, hazardFactory):
        self.row = row
        self.col = col
        self.spawn_rate = spawn_rate
        self.hazardFactory = hazardFactory
        self.currentTime = 0

    def update(self):
        self.currentTime += 1
        if self.currentTime == self.spawn_rate:
            self.currentTime = 0
            hazardList.append(self.hazardFactory.createHazard(self.row, self.col))

class HazardFactory:
    def __init__(self, filename, vx, vy):
        self.filename = filename
        self.vx = vx
        self.vy = vy

    def createHazard(self, row, col):
        newHazard = Actor(self.filename)
        return Hazard(newHazard, row, col, velocity = (self.vx, self.vy))

with open('map1.json','r') as jfile:
    mapData1 = json.load(jfile)

with open('map2.json','r') as jfile:
    mapData2 = json.load(jfile)

with open('map3.json','r') as jfile:
    mapData3 = json.load(jfile)

with open('map4.json','r') as jfile:
    mapData4 = json.load(jfile)

levelList = [mapData1, mapData2, mapData3, mapData4]
def loadMap(mapData):
    global tileMap, enemyList, hazardList

    hazardList = []
    tileMap = []    
    for row in range(mapRows):
        top = row*testTiles.tileSize
        left = 0
        newRow = []
        
        for column in range(mapColumns):
            imgNum, tileType = mapData[row][column]
            newTile = Tile(left, top, imgNum)
            newTile.type = tileType
            left += testTiles.tileSize
            newRow.append(newTile)
        tileMap.append(newRow)

    if(currentLevel == 2):
        villainImg = Actor("villain_idle", pos=(WIDTH/2, HEIGHT-100))
        villainAnimSprite = AnimationSprite([villainImg])
        villainImg2 = Actor("villain_idle", pos=(WIDTH/2, HEIGHT-100))
        villainAnimSprite2 = AnimationSprite([villainImg2])
        moveList = [(5, 0, 40)]

        boss = RandomMoveEnemy(9, 14, [villainAnimSprite, villainAnimSprite, villainAnimSprite])
        boss.is_active = False
        boss.triggerLocation = 3
        
        boss2 = RandomMoveEnemy(5, 21, [villainAnimSprite2, villainAnimSprite2, villainAnimSprite2])
        boss2.is_active = False
        boss2.triggerLocation = 16
            
        enemyList = [boss, boss2]

        enemyList[0].facingRight = False
        
    else:
        enemyList = []

bulletFactory2 = HazardFactory("bullet bill", -5, 0)
bulletbill2 = HazardSpawn(6, 32, 60, bulletFactory2)
bulletFactory3 = HazardFactory("enemy_bullet", 0, 5)
bulletbill3 = HazardSpawn(6, 10, 60, bulletFactory3)

def getMapTileForScreen(pos):
    x, y = pos
    
    row = (y - mapTop)//testTiles.tileSize
    column = (x - mapLeft + scrollAmount)//testTiles.tileSize

    return int(row), int(column)

def isOpenTile(row, col):
    return tileMap[row][col].type == 'clear' or tileMap[row][col].type == 'goal' or tileMap[row][col].type == 'danger'

def isGoal(row, col):
    return tileMap[row][col].type == 'goal'

def isPlayerAtGoal(player):
    actor = player.currentActor()
    playerPos = actor.pos
    pRow, pColumn = playerPos
    row, column = getMapTileForScreen((pRow, pColumn))
    if isGoal(row,column):
        return True
    return False

def inDanger(row, col):
    return tileMap[row][col].type == 'danger'

def isPlayerInDanger(player):
    actor = player.currentActor()
    playerPos = actor.pos
    pRow, pColumn = playerPos
    row, column = getMapTileForScreen((pRow, pColumn))
    
    for h in hazardList:
        if player.isOverlappingRect(h.img):
            print ("hazard")
            hazardList.remove(h)
            return True
    
    if inDanger(row,column):
        print ('inDanger')
        return True
    
    for i in range(len(enemyList)):
        if enemyList and player.isOverlappingRect(enemyList[i].hitbox):
            print("enemy")
            return True
        
    return False

class Character:
    def __init__(self, anim_list, hitbox = None, affectScroll=False):
        self.state = "standing"
        self.anim_list = anim_list
        self.animation = anim_list[0]
        self.facingRight = True
        self.alive = True
        self.affectScroll = affectScroll

        self.isPlayer = True

        if hitbox:
            self.hitbox = hitbox
        else:
            actor = self.animation.currentActor()
            self.hitbox = Rect(actor.left, actor.top, actor.width, actor.height)
        self.vy = 0
        self.vx = 0

        self.shoot_start_time = -100.0
        self.shoot_duration = 0.08 # hundreths of a second before stopping shooting animation

    def draw(self, screen):
        
        if self.state == "standing":
            self.animation = self.anim_list[0]
        elif self.state == "jumping":
            self.animation = self.anim_list[1]
            
        self.animation.draw(screen, self.facingRight)

    def goto(self, x, y):
        self.updatePosition((x, y))
        self.animation.updatePosition((x, y))

    def jump (self, force):
        if self.state != "jumping" and self.state != "jumping_shoot":
            self.vy -= force

    def isValidPos(self):
        actor = self.currentActor()

        row0, col0 = getMapTileForScreen((actor.left, actor.top))
        row1, col1 = getMapTileForScreen((actor.right, actor.bottom))

        for row in range(row0, row1+1):
            for col in range(col0, col1+1):
        
                if not isOpenTile(row, col):
                    return False

        return True

    def updateState(self, newState):

        currentPosition = self.screenPosition()

        if self.shoot_start_time + self.shoot_duration < timer:
            
            if newState == "standing":
                self.state = newState
                self.animation = self.anim_list[0]
                self.updatePosition(currentPosition)
            elif newState == "jumping":
                self.state = newState
                self.animation = self.anim_list[1]
                self.updatePosition(currentPosition)  
            elif newState == "running":
                self.state = newState
                self.animation = self.anim_list[2]
                self.updatePosition(currentPosition)

        else:
            if newState == "standing":
                self.state = "standing_shoot"
                self.animation = self.anim_list[3]
                self.updatePosition(currentPosition)
            elif newState == "jumping":
                self.state = "jumping_shoot"
                self.animation = self.anim_list[4]
                self.updatePosition(currentPosition)  
            elif newState == "running":
                self.state = "running_shoot"
                self.animation = self.anim_list[5]
                self.updatePosition(currentPosition)

        self.hitbox.left = currentPosition[0] - self.hitbox.width//2
        self.hitbox.top = currentPosition[1] - self.hitbox.height//2

    def currentActor(self):
        if self.state == "standing":
            self.animation = self.anim_list[0]
        elif self.state == "jumping":
            self.animation = self.anim_list[1]

        return self.animation.currentActor()

    def isMovingInBlockedTile(self):
        row, col = getMapTileForScreen(self.screenPosition())
        if isOpenTile(row, col):
            return False
        return True
    
    def isFallingOnPlatform(self):
        bottom = self.currentActor().bottom
        left = self.currentActor().left
        right = self.currentActor().right
        center = self.currentActor().bottom

        row, col = getMapTileForScreen((center, bottom))
        if row >= mapRows:
            print("!!!!!", row)
        if isOpenTile(row, col):
            return False
        
        row, col = getMapTileForScreen((left, bottom))
        if isOpenTile(row, col):
            return False
        
        row, col = getMapTileForScreen((right, bottom))
        if isOpenTile(row, col):
            return False

        return True

    def characterValid(self):
        left = int(self.hitbox.left)
        right = int(self.hitbox.left + self.hitbox.width)
        top = int(self.hitbox.top)
        bottom = int(self.hitbox.top + self.hitbox.height)

        if isOffScreen(self):
            return False

        if not self.isValidPos():
            return False
        
        return True

    def updatePosition(self, pos):
        self.animation.updatePosition(pos)

        self.hitbox.left = pos[0] - self.hitbox.width//2
        self.hitbox.top = pos[1] - self.hitbox.height//2

    def screenPosition(self):
        return self.currentActor().pos
                
    def updatePhysics(self):
        global scrollAmount

        self.updateState('standing')

        old_x, old_y = self.screenPosition()
        new_x, new_y = self.screenPosition()
        self.vy += GRAVITY
        
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
            
        new_y += self.vy
        
        self.updatePosition((new_x, new_y))
        
        if self.characterValid():
            self.updateState("jumping")
        else:
            self.vy = 0
            self.updatePosition((old_x, old_y))

            if self.vx == 0:
                self.updateState("standing")
            else:
                self.updateState("running")
            
        old_x, old_y = self.screenPosition()
        new_x, new_y = self.screenPosition()
        
        new_x += self.vx
        self.updatePosition((new_x, new_y))
        
        if not self.characterValid():
            self.updatePosition((old_x, old_y))
            
        elif new_x > max_x:
            self.updatePosition((old_x, old_y))
            if self.affectScroll:
                scrollAmount += self.vx
                if scrollAmount > 640:
                    scrollAmount = 640            

        elif new_x < min_x:
            self.updatePosition((old_x, old_y))
            if self.affectScroll:
                scrollAmount += self.vx
                if scrollAmount < 0:
                    scrollAmount = 0

    def shoot(self):
        self.shoot_start_time = timer

    def isOverlappingRect(self, rect):
        if self.hitbox.right < rect.left:
            return False
        elif self.hitbox.left > rect. right:
            return False
        elif self.hitbox.top > rect. bottom:
            return False
        elif self.hitbox.bottom < rect. top:
            return False
        else:
            return True
        

    def update(self):
        
        oldState = self.state
        self.updatePhysics()
        if self.state == oldState:
            self.animation.update()
        else:
            self.animation.totalFrames = 0        
            
    def getLeft(self):
        currentImage = self.currentActor()
        return currentImage.left
    def getRight(self):
        currentImage = self.currentActor()
        return currentImage.right
    def getTop(self):
        currentImage = self.currentActor()
        return currentImage.top
    def getBottom(self):
        currentImage = self.currentActor()
        return currentImage.bottom

class Enemy(Character):
    def __init__(self, row, column, anim_list, hitbox = None, hazard_file = "enemy_bullet", shoot_rate = 80, lives = 2):
        Character.__init__(self, anim_list, hitbox)
        self.timer = 0
        self.last_shot = 0
        self.shoot_rate = shoot_rate

        self.is_active = True
        self.triggerLocation = 0

        self.hazard_file = hazard_file
        
        self.lives = lives

        self.startRow = row
        self.startColumn = column

        self.world_x, self.world_y = Tile.ConvertTileToWorld(row, column)

        self.isPlayer  = False
        
    def characterValid(self):
        left = int(self.hitbox.left)
        right = int(self.hitbox.left + self.hitbox.width)
        top = int(self.hitbox.top)
        bottom = int(self.hitbox.top + self.hitbox.height)

        midy = (bottom + top)/2
        midx = (left + right)/2

        if top < 0:
            return False

        if bottom > HEIGHT:
            return False

        if not self.isValidPos():
            return False
        
        return True

    def screenPosition(self):
        return self.world_x - scrollAmount, self.world_y

    def updatePosition(self, pos):
        screen_x, screen_y = pos

        self.world_x = screen_x + scrollAmount
        self.world_y = screen_y

        self.animation.updatePosition((screen_x, screen_y))
        

        self.hitbox.left = pos[0] - self.hitbox.width//2
        self.hitbox.top = pos[1] - self.hitbox.height//2

    def move(self, player):
        pass

    def createHazard(self):
        if self.facingRight:
            velocity = (20, 0)
            x, y = self.screenPosition()
            pos = (self.getRight() + 25, y)
            newHazard = Actor(self.hazard_file, pos=pos)
            row, column = getMapTileForScreen((x, y))
            hazardList.append(Hazard(newHazard, row, column, velocity = velocity))
        else:
            velocity = (-20, 0)
            x, y = self.screenPosition()
            pos = (self.getLeft() - 25, y)
            newHazard = Actor(self.hazard_file, pos=pos)
            row, column = getMapTileForScreen((x, y))
            hazardList.append(Hazard(newHazard, row, column, velocity = velocity))

    def update(self):

        if self.is_active:
            
            self.move(player)
            
            self.updateState('standing')

            old_x, old_y = self.screenPosition()
            new_x, new_y = self.screenPosition()
            self.vy += GRAVITY
            
            if self.vy > MAX_FALL_SPEED:
                self.vy = MAX_FALL_SPEED
                
            new_y += self.vy
            
            self.updatePosition((new_x, new_y))
            
            if self.characterValid():
                self.updateState("jumping")
            else:
                self.vy = 0
                self.updatePosition((old_x, old_y))

                if self.vx == 0:
                    self.updateState("standing")
                else:
                    self.updateState("running")
                
            old_x, old_y = self.screenPosition()
            new_x, new_y = self.screenPosition()
            
            new_x += self.vx
            self.updatePosition((new_x, new_y))
            
            if not self.characterValid():
                self.updatePosition((old_x, old_y))

            x, y = self.screenPosition()
            while not self.characterValid():
                self.updatePosition((x, y-1))
                x, y = self.screenPosition()
            
            self.timer += 1
            if self.last_shot + self.shoot_rate < self.timer:
                self.createHazard()
                self.last_shot = self.timer
            
        else:
            self.updateState('standing')

            old_x, old_y = self.screenPosition()
            new_x, new_y = self.screenPosition()
            self.vy += GRAVITY
            
            if self.vy > MAX_FALL_SPEED:
                self.vy = MAX_FALL_SPEED
                
            new_y += self.vy
            
            self.updatePosition((new_x, new_y))
            
            if self.characterValid():
                self.updateState("jumping")
            else:
                self.vy = 0
                self.updatePosition((old_x, old_y))

                if self.vx == 0:
                    self.updateState("standing")
                else:
                    self.updateState("running")
    
class RunAndShootEnemy(Enemy):
    def __init__(self, row, column, anim_list, moveList, hitbox = None, hazard_file = "enemy_bullet", shoot_rate = 80):
        Enemy.__init__(self, row, column, anim_list, hitbox, hazard_file, shoot_rate)
        self.moveList = moveList
        
        self.moveIndex = 0
        self.currentTime = 0
        self.moveTime = self.moveList[self.moveIndex][2]

    def move(self, player):

        if self.is_active:
        
            self.currentTime += 1
            if(self.currentTime >= self.moveTime):
                self.moveIndex = (self.moveIndex + 1) % len(self.moveList)
                self.currentTime = 0
            
            self.vx = self.moveList[self.moveIndex][0]
            self.vy = self.moveList[self.moveIndex][1]
            self.moveTime = self.moveList[self.moveIndex][2]

class RandomMoveEnemy(Enemy):
    def __init__(self, row, column, anim_list, hitbox = None, hazard_file = "enemy_bullet", shoot_rate = 80):
        Enemy.__init__(self, row, column, anim_list, hitbox, hazard_file, shoot_rate)

        self.jumpValues = [0, -30, 0, 0, -40]

        self.currentTime = 0
        if self.facingRight == True:
            self.vx = random.randint(-2, 5)
        else:
            self.vx = random.randint(-5, 2)
        self.vy = random.choice(self.jumpValues)
        self.moveTime = random.randint(0, 40)

    def move(self, player):

        if self.is_active:
        
            self.currentTime += 1
            if(self.currentTime >= self.moveTime):
                self.currentTime = 0
                if self.facingRight == True:
                    self.vx = random.randint(-1, 5)
                else:
                    self.vx = random.randint(-5, 1)
                self.vy = random.choice(self.jumpValues)
                self.moveTime = random.randint(0, 40)

    def draw(self, screen):
        x, y = self.screenPosition()
        pX, pY = player.screenPosition()
        if pX < x:
            self.facingRight = False
        else:
            self.facingRight = True
        
        self.animation.draw(screen, self.facingRight)

class Hazard:
    def __init__(self, img, row, col, velocity=(0, 0)):
        self.img = img
        self.vel = velocity
        self.world_x, self.world_y = Tile.ConvertTileToWorld(row, col)

        self.timer = 0
        self.lifetime = 3000

    def isOffScreen(self):
        actor = self.img
        if actor.left < 0:
            return True
        if actor.right > WIDTH:
            return True
        if actor.top < 0:
            return True
        if actor.bottom > HEIGHT:
            return True
        return False

    def update(self):

        if self.timer < self.lifetime:
            self.timer += 1
            
            vx, vy = self.vel
            self.world_x += vx
            self.world_y += vy
            
            self.img.pos = (self.world_x - scrollAmount, self.world_y)

            row, col = getMapTileForScreen(self.img.pos)

            if not isOpenTile(row, col):
                self.timer = self.lifetime

    def draw(self):
        if self.timer < self.lifetime:
            self.img.draw()
            
playerimg = Actor("mini-megaman-1")
bulletlist = []
bulletcount = 0
bulletspeed = 25

idle_image = Actor("megaman_idle")
idle_animation = AnimationSprite([idle_image])

jump_image = Actor("megaman_jump")
jump_animation = AnimationSprite([jump_image])

run0_image = Actor("megaman_run_0")
run1_image = Actor("megaman_run_1")
run2_image = Actor("megaman_run_2")
run3_image = Actor("megaman_run_1")
runList = [run0_image, run1_image, run2_image, run3_image]
run_animation = AnimationSprite(runList)

standShoot_image = Actor("megaman_standshoot")
standShoot_animation = AnimationSprite([standShoot_image])

jumpShoot_image = Actor("megaman_jumpshoot")
jumpShoot_animation = AnimationSprite([jumpShoot_image])

runShoot0_image = Actor("megaman_runshoot_0")
runShoot1_image = Actor("megaman_runshoot_1")
runShoot2_image = Actor("megaman_runshoot_2")
runShoot3_image = Actor("megaman_runshoot_1")
runShootList = [runShoot0_image, runShoot1_image, runShoot2_image, runShoot3_image]
runShoot_animation = AnimationSprite(runShootList)

megaman_list = [idle_animation, jump_animation, run_animation, standShoot_animation, jumpShoot_animation, runShoot_animation]
player = Character(megaman_list, affectScroll = True)
player.goto(150, 200)

moveAmount = 8
moveUp = False
moveDown = False
moveRight = False
moveLeft = False
lastUpdate = 0

def createBullet():
    global bulletcount
    bulletcount += 1
    bulletimg = Actor("bullet")

    if player.facingRight:
        x, y = player.currentActor().midright
        bulletimg.pos = (x, y)
    else:
        x, y = player.currentActor().midleft
        bulletimg.pos = (x, y)
        
    bulletlist.append((bulletcount, bulletimg, player.facingRight))
    player.shoot()
    
enemyList = []

def on_mouse_down(pos):
    global gameover, lives, currentLevel, scrollAmount, bulletcount, bulletlist
    print(getMapTileForScreen(pos))
    if gameover:
        if retryBox.collidepoint(pos):
            print('retry....')
            currentLevel = 0
            loadMap(levelList[currentLevel])
            scrollAmount = 0
            player.goto(150, 200)
            lives = 5
            bulletcount = 0
            bulletlist = []
            gameover = False

rightDown = False
leftDown = False          

def on_key_down(key):
    global moveUp, moveDown, moveLeft, moveRight, scrollAmount, rightDown, leftDown
    if key == keys.RIGHT:
            rightDown = True
            if leftDown == False:
                player.facingRight = True
            player.vx += runSpeed
    if key == keys.LEFT:
            leftDown = True
            if rightDown == False:
                player.facingRight = False 
            player.vx -= runSpeed
    if key == keys.UP:
            player.jump(jumpAmount)
    if key == keys.SPACE:
            createBullet()
    if key == keys.D:
            print(scrollAmount)
    if key == keys.P:
            print(player.currentActor().pos)

def on_key_up(key):
    global moveUp, moveDown, moveLeft, moveRight, rightDown, leftDown
    if key == keys.RIGHT:
            rightDown = False
            if leftDown == True:
                player.facingRight = False
            player.vx -= runSpeed
    if key == keys.LEFT:
            leftDown = False
            if rightDown == True:
                player.facingRight = True 
            player.vx += runSpeed

def update():
    global lastUpdate, currentLevel, lives
    global scrollAmount, gameover, enemyList, win
    global hazardList
    time_passes = timer - lastUpdate
    lastUpdate = timer
    player.update()
    
    if currentLevel == 0:
        bulletbill2.update()

    elif currentLevel == 1:
        bulletbill3.update()
    
    for enemy in enemyList:
        if enemy.alive:
            enemy.update()

    if isOffScreen(player):
        fixOffScreen(player)

    if isPlayerAtGoal(player):
        if currentLevel == 2:
            win = True

        else:
            lives = 5
            currentLevel += 1
            loadMap(levelList[currentLevel])
            if currentLevel == 0 or currentLevel == 3:
                scrollAmount = 0
                player.goto(150, 150)
            elif currentLevel == 1:
                scrollAmount = 580
                player.goto(550, 69)
            elif currentLevel == 2:
                scrollAmount = 0
                player.goto(150, 200)
            pass

    elif isPlayerInDanger(player):
        
        if currentLevel == 0 or currentLevel == 3:
            scrollAmount = 0
            player.goto(150, 150)
            hazardList = []
        elif currentLevel == 1:
            scrollAmount = 580
            player.goto(550, 69)
            hazardList = []
        elif currentLevel == 2:
            scrollAmount = 0
            player.goto(150, 200)
            hazardList = []

            villainImg = Actor("villain_idle", pos=(WIDTH/2, HEIGHT-100))
            villainAnimSprite = AnimationSprite([villainImg])

            villainImg2 = Actor("villain_idle", pos=(WIDTH/2, HEIGHT-100))
            villainAnimSprite2 = AnimationSprite([villainImg2])

            boss = RandomMoveEnemy(9, 14, [villainAnimSprite, villainAnimSprite, villainAnimSprite])
            boss.is_active = False
            boss.triggerLocation = 3
            
            boss2 = RandomMoveEnemy(8, 25, [villainAnimSprite2, villainAnimSprite2, villainAnimSprite2])
            boss2.is_active = False
            boss2.triggerLocation = 16
            
            enemyList = [boss, boss2]
            
        lives -= 1
        if lives < 0:
            gameover = True

    x, y = getMapTileForScreen(player.screenPosition())
    
    for i in enemyList:
        if y > i.triggerLocation:
            i.is_active = True

    for bulletid, bulletimg, facingRight in bulletlist:
        x, y = bulletimg.pos
        if facingRight:
            bulletimg.pos = (x+bulletspeed, y)
        else:
            bulletimg.pos = (x-bulletspeed, y)

    for hazard in hazardList:
        hazard.update()

    cleanupBulletlist()

def isActorOffScreen(actor):
    if actor.left > WIDTH:
        return True
    if actor.right < 0:
        return True
    if actor.bottom < 0:
        return True
    if actor.top > HEIGHT:
        return True
    return False

def hitEnemies(actor):
    global enemyList
    for enemy in enemyList:
        if enemy.alive and enemy.isOverlappingRect(actor):
            enemy.lives -= 1
            if enemy.lives <1:
                enemy.alive = False
                enemyList.remove(enemy)
            return True
    return False
    
def cleanupBulletlist():
    global bulletlist
    newbulletlist1 = []
    
    for bulletid, bulletimg, facingRight in bulletlist:
        if not isActorOffScreen(bulletimg):
            newbulletlist1.append((bulletcount, bulletimg, facingRight))

    newbulletlist2 = []
    for bulletid, bulletimg,facingRight in newbulletlist1:
        if not hitEnemies(bulletimg):
            newbulletlist2.append((bulletcount, bulletimg, facingRight))

    newbulletlist3 = []
    
    for bulletid, bulletimg,facingRight in newbulletlist2:
        row, col = getMapTileForScreen(bulletimg.pos)
        if isOpenTile(row, col):
            newbulletlist3.append((bulletcount, bulletimg, facingRight))
            
    bulletlist = newbulletlist3

def isOffScreen(character):
    actor = character.currentActor()
    if actor.left < 0:
        return True
    if actor.right > WIDTH:
        return True
    if actor.top < 0:
        return True
    if actor.bottom > HEIGHT:
        return True
    return False

def fixOffScreen(char):
    box = char.hitbox
    if box.left < 0:
        box.left = 0 + 1
    if box.right > WIDTH:
        box.right = WIDTH - 1
    if box.top < 0:
        box.top = 0 + 1
    if box.bottom > HEIGHT:
        box.bottom = HEIGHT - 1

icon = Actor("mini-megaman-1")
icon.pos = (20, 20)
def drawHUD():
    icon.draw()
    screen.draw.text("x" + str(lives), pos = (35,20), color = "red")


def draw():
    screen.fill('black')
    for row in range(mapRows):
        for column in range(mapColumns):
            tileMap[row][column].draw(screen, scrollAmount)
    player.draw(screen)

    for enemy in enemyList:
        if enemy.alive:
            if currentLevel == 2:
                enemy.draw(screen)

    for hazard in hazardList:
        hazard.draw()

    for bulletid, bulletimg, facingRight in bulletlist:
        bulletimg.draw()

    drawHUD()

    if gameover == True:
        screen.fill('black')
        screen.draw.text("GAME OVER", pos = (100,200), fontsize = 100, color = "white")
        screen.draw.filled_rect(retryBox, "red")
        screen.draw.textbox("RETRY", retryBox, color="black")

    if win == True:
        screen.fill("black")
        screen.draw.text("YOU WIN!!!", pos = (110, 200), fontsize = 100, color = "white")

timer = 0
def game_tick():
    global timer
    timer += 0.01

clock.schedule_interval(game_tick, 0.01)
loadMap(levelList[currentLevel])
pgzrun.go()
