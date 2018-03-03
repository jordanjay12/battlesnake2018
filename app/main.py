import bottle
import os
import random
import heapq

boardWidth = None
boardHeight = None
snakeLength = 0
snakeHealth = None

# The URL of Xander's snake: https://dwightsnake.herokuapp.com

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
    
    def in_bounds(self, id):
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, id):
        return id not in self.walls
    
    def neighbors(self, id):
        (x, y) = id
        results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
        if (x + y) % 2 == 0: results.reverse() # aesthetics
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results

# the Heuristic required for running A* algorithm
def heuristic (a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

# I guess the actual search of the A* algorithm
def bs_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbors(current):
            # new_cost = cost_so_far[current] + graph.cost(current, next)
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current
    return came_from, cost_so_far



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
    print data
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')


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
    snakes = data['snakes']['data']
    mySnakeId = data['you']['id']
    foodList = []
    allFood = data['food']['data']
    for food in allFood:
        foodList.append((food['x'], food['y']))
    ourSnake = None;
    dangerZone = []

    # Find the ID of our snake
    for snake in snakes:
        print snake
        snakeCoords = snake['body']['data']
        currentId = snake['id']
        if currentId == mySnakeId:
            print("Found our snake")
            ourSnake = snake;
        # Go through the coordinates of each of the snakes: this should really in range(len-1) since the tail will move
        for coordinate in snake['body']['data']:
            dangerZone.append((coordinate['x'], coordinate['y']))


    # Our danger zone should be complete now - I should be able to create a graph out of it
    graph = SquareGrid(boardWidth, boardHeight) # needs the dimensions of the graph
    graph.walls = dangerZone

    print("If I am seeing this, then I think the graph is working as intended")

    snakeLength = ourSnake['length']
    snakeHealth = ourSnake['health']

    # Find the location of our snake
    ourCoordinates = ourSnake['body']['data']
    # the x and y coordinates of our head
    xCoord = int(ourCoordinates[0]['x'])
    yCoord = int(ourCoordinates[0]['y'])

    start = (xCoord, yCoord)
    goal = findFood(foodList, (xCoord,yCoord))
    came_from, cost_so_far = bs_search(graph, start, goal)
    print("The value of head is:", start)
    print("The value of goal is:", goal)
    print("The value of came_from is: ")
    print(came_from)
    print()
    print("The value of cost_so_far is: ")
    print(cost_so_far)


    print("Printing out goal")
    print(goal)
    print("Printing out what was returned from the key")
    print(came_from[goal])
    destination = goal
    previousMove = None
    while start != destination:
        previousMove = destination
        destination = came_from[destination]

    print("Our next move should be:", previousMove)

    left = xCoord - 1
    right = xCoord + 1
    up = yCoord -1 # since the top is 0
    down = yCoord + 1

    nextMoveX = previousMove[0]
    nextMoveY = previousMove[1]

    if xCoord - nextMoveX < 0:
        direction = "right"
    if xCoord - nextMoveX > 0:
        direction = "left"
    # if both of these cases fail, then we need to move in the up down direction

    if yCoord - nextMoveY < 0:
        direction = "down"
    if yCoord - nextMoveY > 0:
        direction = "up"

    '''
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
    '''


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
