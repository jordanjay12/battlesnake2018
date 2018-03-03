import bottle
import os
import random

boardWidth = None
boardHeight = None
snakeLength = 0
snakeHealth = None

# The URL of Xander's snake: https://dwightsnake.herokuapp.com

def findTail(ourCoordinates):
    # return the location of our tail (x, y)
    xCoord = int(ourCoordinates[len(ourCoordinates) -1]['x'])
    yCoord = int(ourCoordinates[len(ourCoordinates) -1]['y'])
    print("The coordinates of our tail")
    print((xCoord, yCoord))
    return (xCoord, yCoord)



def findFood(foodList, head):
    # find the food item that is closest to the head
    global boardWidth
    global boardHeight
    closest = foodList[0];
    headX = head[0]
    headY = head[1]
    min = boardWidth + boardHeight
    for food in foodList:
        foodX = food[0]
        foodY = food[1]
        distX = abs(headX - foodX)
        distY = abs(headY - foodY)
        total_distance = distX + distY
        if total_distance < min:
            min = total_distance
            closest = food
    return closest
    print("Should be finding food")


@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    global boardWidth
    global boardHeight
    data = bottle.request.json
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')

    # we get our Id in the post request that is sent here

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data
    # There doesn't appear to be that much that is relevant
    print("In the start method")
    print(data)
    boardWidth = data['width']
    boardHeight = data['height']

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url
    }


@bottle.post('/move')
def move():
    global boardWidth
    global boardHeight
    global snakeLength
    global snakeHealth
    data = bottle.request.json

    # TODO: Do things with data
    # Made some more changes to the python file
    # print "Printing out the contents of data"
    #print data
    snakes = data['snakes']['data']
    #print str(snakes[0]['id'])
    # mySnakeId = "409e5891-9d0a-4bc6-9b66-fb1b2d562762"
    mySnakeId = snakes[0]['id']
    foodList = []
    allFood = data['food']['data']
    for food in allFood:
        foodList.append((food['x'], food['y']))

   

    ourSnake = None;
    dangerZone = []

    # Find the ID of our snake
    for snake in snakes:
        snakeCoords = snake['body']['data']
        currentId = snake['id']
        if currentId == mySnakeId:
            print("Found our snake")
            ourSnake = snake;
        # Go through the coordinates of each of the snakes: this should really in range(len-1) since the tail will move
        for coordinate in snake['body']['data']:
            dangerZone.append((coordinate['x'], coordinate['y']))


    snakeLength = ourSnake['length']
    snakeHealth = ourSnake['health']

    # Find the location of our snake
    ourCoordinates = ourSnake['body']['data']
    # the x and y coordinates of our head
    xCoord = int(ourCoordinates[0]['x'])
    yCoord = int(ourCoordinates[0]['y'])


    direction = None

    # Check to see what we should be doing based on our health level
    # Remember that our snakes grow out of our tail
    print("Our Snake Health is: " + str(snakeHealth))
    if snakeHealth > 50 and snakeHealth < 95: # for the initial, not sure if we should be using this at the very beginning of the game
        # I need to do more testing on this to see if it will work
        print("Should be trying to find our tail")
        snake = findTail(ourCoordinates)
        tailX = snake[0]
        tailY = snake[1]

        # I can probably modularize this into some other function
        left = xCoord - 1
        right = xCoord + 1
        up = yCoord -1 # since the top is 0
        down = yCoord + 1

        xMove = xCoord - tailX
        yMove = yCoord - tailY

        if xMove < 0:
            # then the head is to the left of the food
            move = (right, yCoord)
            if move not in dangerZone and right < boardWidth:
                print("Moving Right towards food")
                direction = "right"
            elif move in dangerZone:
                print("Moving right into a danger zone")
        if direction == None and xMove > 0:
            # then the head is to the right of the food
            move = (left, yCoord)
            if move not in dangerZone and left >=0:
                print("Moving Left towards food")
                direction = 'left'
            elif move in dangerZone:
                print("Moving left into a danger zone")
        if direction == None and yMove > 0:
            # then the head is below the food
            move = (xCoord, up)
            if move not in dangerZone and up >= 0:
                print("Moving Up towards food")
                direction = 'up'
            elif move in dangerZone:
                print("Moving up into a danger zone")
        if direction == None and yMove < boardHeight:
            move = (xCoord, down)
            print("At the start of the else case")
            if move not in dangerZone and down < boardHeight:
                print("Moving Down towards food")
                direction = 'down'
            elif move in dangerZone:
                print("Moving down into a danger zone")


        if direction == None:
            print("Print direction is None, finding another safe move")
            if (left,yCoord) not in dangerZone and left >=0:
                direction = 'left'
            elif (right,yCoord) not in dangerZone and right < boardWidth:
                direction = 'right'
            elif (xCoord,up) not in dangerZone and up >= 0:
                direction = 'up'
            else:
                direction = "down"

    else:

        closestFood = findFood(foodList, (xCoord,yCoord))
        foodX = closestFood[0]
        foodY = closestFood[1]

        left = xCoord - 1
        right = xCoord + 1
        up = yCoord -1 # since the top is 0
        down = yCoord + 1
        move = None;
        #direction = None
        xMove = xCoord - foodX
        yMove = yCoord - foodY

        print(dangerZone)

        print("The board width is: " + str(boardWidth))
        print("The board height is " + str(boardHeight))

        if xMove < 0:
            # then the head is to the left of the food
            move = (right, yCoord)
            if move not in dangerZone and right < boardWidth:
                #print("Moving Right towards food")
                direction = "right"
            elif move in dangerZone:
                print("Moving right into a danger zone")
        if direction == None and xMove > 0:
            # then the head is to the right of the food
            move = (left, yCoord)
            if move not in dangerZone and left >=0:
                #print("Moving Left towards food")
                direction = 'left'
            elif move in dangerZone:
                print("Moving left into a danger zone")
        if direction == None and yMove > 0:
            # then the head is below the food
            move = (xCoord, up)
            if move not in dangerZone and up >= 0:
                #print("Moving Up towards food")
                direction = 'up'
            elif move in dangerZone:
                print("Moving up into a danger zone")
        if direction == None and yMove < boardHeight:
            move = (xCoord, down)
            #print("At the start of the else case")
            if move not in dangerZone and down < boardHeight:
                #print("Moving Down towards food")
                direction = 'down'
            elif move in dangerZone:
                print("Moving down into a danger zone")


        if direction == None:
            print("Print direction is None, finding another safe move")
            if (left,yCoord) not in dangerZone and left >=0:
                direction = 'left'
            elif (right,yCoord) not in dangerZone and right < boardWidth:
                direction = 'right'
            elif (xCoord,up) not in dangerZone and up >= 0:
                direction = 'up'
            else:
                direction = "down"    



    # Directions must be one of the following strings
    #directions = ['up', 'down', 'left', 'right']
    #direction = random.choice(directions)
    #print direction
    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
