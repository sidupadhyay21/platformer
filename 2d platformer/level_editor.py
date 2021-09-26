import pgzrun
from HelperTools import *
import json

WIDTH = 900
HEIGHT = 600

showBlockingTiles = True
mouseDown = False

saveButton = Actor("save", pos=(87,550))
leftArrow = Actor("left_arrow", pos=(250,510))
rightArrow = Actor("right_arrow", pos=(750,510))

numberRows = 20
numberCols = 20

selectedTile = None 

testTiles = TileSet('images/super_mario_tileset.png', numberRows , numberCols,alphaCheck=(339,339), scale = 2, padding=1)

sectionList = [0, 5, 10, 15, 200, 205, 210, 215]
section = 0

class Tile:
    def __init__(self, left, top, imgNum, size = 32):
        self.left = left
        self.top = top
        self.imgNum = imgNum
        self.type = "clear"
        self.size = size
        #self.rect = Rect(self.left, self.top, self.size, self.size)

    def getRect(self, scroll=0):
        return Rect(self.left - scroll, self.top, self.size, self.size)

    def draw(self, screen, scroll=0):
        testTiles.drawTile(screen, self.left - scroll, self.top, self.imgNum)

tileMap = []
viewWidth = 20
viewColumn = 0
mapColumns = 40
mapRows = 15
mapLeft = 200
mapTop = 0
menuLeft = 0
menuTop = 0
menuRows = 10
menuColumns = 5
start = (87, 480)
greenBox = Rect(40, 340, 32, 32)
redBox = Rect(100, 340, 32, 32)
blueBox = Rect(40, 380, 32, 32)
whiteBox = Rect(100, 380, 32, 32)
yellowBox = Rect(40, 420, 92, 32)

levelStart = [4,8]

with open('map2.json','r') as jfile:
    mapData = json.load(jfile)
    #levelStart = data['start']
    #mapData = data['map']
 
#TODO - update for when map size changes
for row in range(mapRows):
    top = row*testTiles.tileSize + mapTop
    left = mapLeft
    newRow = []
    for column in range(mapColumns):
        if column < len(mapData[row]):
            imgNum, tileType = mapData[row][column]
            newTile = Tile(left, top, imgNum)
            newTile.type = tileType
            left += testTiles.tileSize
            newRow.append(newTile)
        else:
            imgNum = 299
            tileType = "clear"
            newTile = Tile(left, top, imgNum)
            newTile.type = tileType
            left += testTiles.tileSize
            newRow.append(newTile)
    tileMap.append(newRow)

def draw():
    global print_view
    screen.fill("black")
 #  testTiles.drawTile(screen, 0, 0, 0)
    imgNum = 0
    top = menuTop
    left = menuLeft

    for row in range(menuRows):
        left = 0
        imgNum = sectionList[section] + row*numberCols
        for col in range(menuColumns):
            testTiles.drawTile(screen, left, top, imgNum)
            imgNum += 1
            left += 32
        top += 32

    endColumn = viewColumn + viewWidth
    if endColumn > mapColumns:
        endColumn = mapColumns
        
    for row in range(mapRows):
        for column in range(viewColumn, endColumn):
            tile = tileMap[row][column]
            scroll = viewColumn*testTiles.tileSize
            tile.draw(screen, scroll)
            
            outline = tile.getRect(scroll)
                
            if showBlockingTiles:
                if tile.type == "blocking":
                    screen.draw.rect(outline, 'red')
                elif tile.type == "goal":
                    screen.draw.rect(outline, 'blue')
                elif tile.type == "danger":
                    screen.draw.rect(outline, 'white')
                else:
                    screen.draw.rect(outline, 'green')
        
    saveButton.draw()
    leftArrow.draw()
    rightArrow.draw()
    screen.draw.rect(redBox, 'red')
    screen.draw.rect(greenBox, 'green')
    screen.draw.rect(blueBox, 'blue')
    screen.draw.rect(whiteBox, 'white')
    
def getJSONMap():
    jsonMap=[]
    for row in range(mapRows):
        newRow = []
        for col in range(mapColumns):
            newRow.append((tileMap[row][col].imgNum, tileMap[row][col].type))
        jsonMap.append(newRow)
    return jsonMap

def on_key_down(key):
    global section
    if key == keys.UP:
        section += 1
    if key == keys.DOWN:
        section -= 1

    section = section % len(sectionList)
    print(section)

def getMapTile(pos):
    x, y = pos
    mapWidth = mapColumns*testTiles.tileSize
    mapHeight = mapRows*testTiles.tileSize
    if x >= mapLeft and y >= mapTop and x < (mapLeft + mapWidth) and y < (mapTop + mapHeight):
        row = (y - mapTop)//testTiles.tileSize
        column = (x - mapLeft)//testTiles.tileSize
        return row, (column+viewColumn)
    return None

def getMenuImgNum(pos):
    x,y = pos
    menuWidth = menuColumns*testTiles.tileSize
    menuHeight = menuRows*testTiles.tileSize
    if x >= menuLeft and y >= menuTop and x < (menuLeft + menuWidth) and y < (menuTop + menuHeight):
        row = (y - menuTop)//testTiles.tileSize
        column = (x - menuLeft)//testTiles.tileSize
        imgNum = sectionList[section] + row*numberCols + column
        return imgNum
    
    return None

def isRectangleClicked(rect, pos):
    left, top, width, height = rect
    x, y = pos
    if x > left and x < left + width and y > top and y < top + height:
        return True
    else:
        return False
    
def on_mouse_down(pos):
    global selectedTile,showBlockingTiles, mouseDown, viewColumn, levelStart
    mouseDown = True
    print (pos)
    tile = getMapTile(pos)
    if tile:
        print ('tile', tile)
        if selectedTile:
            row, col = tile
            if selectedTile == 'green':
                tileMap[row][col].type = "clear"
            elif selectedTile == 'red':
                tileMap[row][col].type = "blocking"
            elif selectedTile == 'blue':
                tileMap[row][col].type = "goal"
            elif selectedTile == 'white':
                tileMap[row][col].type = "danger"
            elif selectedTile == 'yellow':
                levelStart = [row, col]
            else:
                tileMap[row][col].imgNum = selectedTile
    elif rightArrow.collidepoint(pos):
        viewColumn += 1
    elif leftArrow.collidepoint(pos):
        viewColumn -= 1
    else:
        #showBlockingTiles = False
        if saveButton.collidepoint(pos):
            print('save')
            with open('map2.json','w') as f:
                #jsonData = {}
                #jsonData['start'] = (150,150)
                #jsonData['map'] = getJSONMap()
                json.dump(getJSONMap(), f, ensure_ascii=False)
        elif isRectangleClicked(greenBox, pos):
            selectedTile = 'green'
            showBlockingTiles = True
        elif isRectangleClicked(redBox, pos):
            selectedTile = 'red'
            showBlockingTiles = True
        elif isRectangleClicked(blueBox, pos):
            selectedTile = 'blue'
            showBlockingTiles = True
        elif isRectangleClicked(whiteBox, pos):
            selectedTile = 'white'
            showBlockingTiles = True
        elif isRectangleClicked(yellowBox, pos):
            selectedTile = 'yellow'
            showBlockingTiles = True
        else:
            selectedTile = getMenuImgNum(pos)

        print('selected:', selectedTile)
    
    if viewColumn < 0:
        viewColumn = 0
    if viewColumn >= mapColumns - 20:
        viewColumn = mapColumns - 20
def on_mouse_up(pos):
    global mouseDown
    mouseDown = False
def on_mouse_move(pos):
    global mouseDown, levelStart
    if mouseDown == True:
        tile = getMapTile(pos)
        if tile:
            print ('tile', tile)
            if selectedTile:
                row, col = tile
                if selectedTile == 'green':
                    tileMap[row][col].type = "clear"
                elif selectedTile == 'red':
                    tileMap[row][col].type = "blocking"
                elif selectedTile == 'blue':
                    tileMap[row][col].type = "goal"
                elif selectedTile == 'white':
                    tileMap[row][col].type = "danger"
                elif selectedTile == 'yellow':
                    levelStart = [row, col]
                else:
                    tileMap[row][col].imgNum = selectedTile
    
pgzrun.go()
