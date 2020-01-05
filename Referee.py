from CommonDefine import TCoor
from CommonDefine import direction
from enum import Enum
from Snake import CSnake
from Food import CFood
from Wall import CWall
from Wall import TBoundary

# game state type
class EGameState( Enum ):
    ready = 0
    running = 1
    over = 2

class CReferee:

    def __init__( self, lateralGridNum, verticalGridNum ):
        # boundary wall
        self.__wall = CWall( TBoundary( verticalGridNum - 1, 0, 0, lateralGridNum - 1 ) )

        # played snake
        self.__snake = None

        # targer food
        self.__food = None

        # total num of eaten food
        self.__foodNum = 0

        # state of game
        self.__gameState = EGameState.ready

    # start game
    def start( self ):
        # configure snake
        self.__snake = CSnake( self.__wall.getBoundary() )

        # configure food
        self.createFood()

        # switch game state to running
        self.__gameState = EGameState.running

    # create food without overlapping
    def createFood( self ):
        # get snake body list
        snakeBody = self.__snake.getBodyPos()

        # get snake body length
        snakeLength = self.__snake.getBodyLength()

        while True:
            # configure food
            self.__food = CFood( self.__wall.getBoundary() )

            # get food position
            foodPos = self.__food.getPos()

            # traversal body list for avoiding food overlapping 
            isFoodValid = True
            for i in range( snakeLength ):
                if snakeBody[ i ] == foodPos:
                    isFoodValid = False
                    break

            # not stop until valid food generated
            if isFoodValid == True:
                break

    # get total num of eaten food
    def getFoodNum( self ):
        return self.__foodNum

    # get state of game
    def getGameState( self ):
        return self.__gameState

    # set move Direction of snake
    def setSnakeMoveDir( self, dir ):
        self.__snake.setMoveDir( dir )

    # get Snake head pos
    def getSnakeHeadPos( self ):
        return self.__snake.getHeadPos()

    # get Snake head pos
    def getWallBoundary( self ):
        return self.__wall.getBoundary()

    # get whole body list of snake
    def getSnakeBody( self ):
        return self.__snake.getBodyPos()

    # get length of snake
    def getSnakeLength( self ):
        return self.__snake.getBodyLength()

    # get snake accumulated step number
    def getSnakeStepAcc( self ):
        return self.__snake.getStepAcc()

    # get position of food
    def getFoodPos( self ):
        return self.__food.getPos()

    # whether snake head and food overlap
    def isSnakeEating( self ):
        if self.__snake.getHeadPos() == self.__food.getPos():
            self.__foodNum = self.__foodNum + 1
            return True

    # whether snake head out of boundary
    def IsSnakeCrash( self ):
        # get head position
        snakeHead = self.__snake.getHeadPos()

        # get wall boundary
        boundary = self.__wall.getBoundary()

        # whether head position exceed activity range 
        if snakeHead.x < boundary.left \
        or snakeHead.x > boundary.right \
        or snakeHead.y < boundary.lower \
        or snakeHead.y > boundary.upper: 
            return True

        return False

    # do process which need to do every tick
    def roundTask( self ):
        # snake move command
        self.__snake.move()
        
        # game over when snake bite itself
        if self.__snake.isBite() or self.IsSnakeCrash():
             self.__gameState = EGameState.over
             return

        # end one round when snake get food
        if self.isSnakeEating():
            # add snake body
            self.__snake.growUp()

            # configure new food
            self.createFood()
            return


