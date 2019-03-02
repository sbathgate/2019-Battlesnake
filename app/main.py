import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.
    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    global boardWidth
    global boardHeight

    data = bottle.request.json


    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    boardWidth = data['board']['width']
    boardHeight = data['board']['height']
    gameID = data['game']['id']
    color = "#50C878"

    return start_response(color)


def getMyLocation(data):
  return data['you']['body'][0]

def getAdjacentCells(myLocation, data):
    # Coordinates of mySnake head and adajacent spaces
    adjacent = {}

    adjacent['up'] = [myLocation['y']-1, myLocation['x']]
    adjacent['down'] = [myLocation['y']+1, myLocation['x']]
    adjacent['left'] = [myLocation['y'], myLocation['x']-1]
    adjacent['right'] = [myLocation['y'], myLocation['x']+1]

    return adjacent

def isSafeSpace(adjacentCells, data):
    potentialMove = {}
    for direction, coordinate in adjacentCells.items():
        safeSpace = True

        # Check adjacentCells are within board
        if coordinate[0] < 0 or coordinate[0] >= boardHeight: # checking if move 'up' or 'down' is a wall
            safeSpace = False
        elif coordinate[1] < 0 or coordinate[1] >= boardWidth: # checking if move 'left' or 'right' is a wall
            safeSpace = False

        # Check adjacentCells for another snake
        for snake in data['board']['snakes']:
            if safeSpace == False:
                break

            for snakePart in snake['body']:
                if snakePart.values() == coordinate:
                    safeSpace = False
                    break

        if safeSpace == True:
            potentialMove[direction] = coordinate # Adds direction to potentialMove
    print(potentialMove)
    return potentialMove

def getClosestFood(potentialMove, data):
    closestFood = {}
    closestDistance = 100

    for berry in data['board']['food']:
        distanceX = abs(myLocation['x'] - berry['x'])
        distanceY = abs(myLocation['y'] - berry['y'])

        actualDistance = distanceX + distanceY

        if actualDistance < closestDistance:
            closestDistance = actualDistance
            closestFood = berry

    foodDirection = []
    safeFoodDirection = []
    if closestFood['y'] - myLocation['y'] < 0:
        foodDirection.append('up')
    elif closestFood['y'] - myLocation['y'] > 0:
        foodDirection.append('down')

    if closestFood['x'] - myLocation['x'] < 0:
        foodDirection.append('left')
    elif closestFood['x'] - myLocation['x'] > 0:
        foodDirection.append('right')
    print("Potential Move: ", potentialMove, "foodDirection: ", foodDirection)



    for safeDirections in potentialMove.keys():
        print(safeDirections)
        if safeDirections in foodDirection:
            safeFoodDirection.append(safeDirections)

    return safeFoodDirection

@bottle.post('/move')
def move():
    # Get request data
    data = bottle.request.json


    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))
    global myLocation
    myLocation = getMyLocation(data)
    adjacentCells = getAdjacentCells(myLocation, data)
    potentialMove = isSafeSpace(adjacentCells, data)
    findFood = getClosestFood(potentialMove, data)

    if len(findFood) > 0:
        direction = random.choice(findFood)
    else:
        direction = random.choice(potentialMove.keys())

    if len(direction) == 0:
        direction = ['up', 'down', 'left','right']

    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
