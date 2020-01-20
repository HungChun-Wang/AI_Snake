from CommonDefine import TCoor
from CommonDefine import direction
from enum import IntEnum
import numpy as np
from Snake import CSnake
from Food import CFood
from Wall import CWall
from Wall import TBoundary
from DataRecorder import CDataRecorder
from DataRecorder import TOrientalDist

# game state type
class EGameState( IntEnum ):
    ready = 0
    running = 1
    over = 2

class EReward( IntEnum ):
    none = 0
    eat = 10
    die = -10

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

        # minimal distance from snake head to body or wall in four orientation
        self.__minDistToBarrier = None

        # coordinate different between snake head and food
        self.__coorDiffToFood = None

        fieldnames = [ 'Upper Barrier Dist', 'Lower Barrier Dist', \
                        'Left Barrier Dist', 'Right Barrier Dist', \
                        'X Diff', 'Y Diff', 'Move Direction', 'Reward' ]

        # record data
        self.__dataRecorder = CDataRecorder( 'SnakeData.csv' , fieldnames )

    # start game
    def start( self ):
        # configure snake
        self.__snake = CSnake( self.__wall.getBoundary() )

        # configure food
        self.createFood()

        # clean food number
        self.__foodNum = 0

        # switch game state to running
        self.__gameState = EGameState.running

        # calculate distance to closed barrier in four orientaion
        self.__minDistToBarrier = self.__calcMinDistToBarrier( self.__snake.getBodyPos(), \
                    self.__snake.getBodyLength(), self.__wall.getBoundary() )
        
        # calculate coordinate different between snake head and food
        self.__coorDiffToFood = self.__calcCoorDiffToFood( self.__snake.getHeadPos(), self.__food.getPos() )

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

    # get environment state
    def getEnvState( self ):
        # arrange state parameter
        envState = np.array(
            [ self.__minDistToBarrier.up, self.__minDistToBarrier.down, \
            self.__minDistToBarrier.left, self.__minDistToBarrier.right, \
            self.__coorDiffToFood.x, self.__coorDiffToFood.y ], \
            dtype = 'float32' )

        # reshape to 2D array
        envState = np.reshape( envState, ( 1, 6 ) )
        
        return envState

    # set move Direction of snake
    def setSnakeMoveDir( self, dir ):
        self.__snake.setMoveDir( dir )

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
        if self.__snake.getMoveDir() == direction.none:
            return

        # snake move command
        self.__snake.move()

        # game over when snake bite itself
        if self.__snake.isBite() or self.IsSnakeCrash():
            # give reward of die
            self.__snake.setReward( EReward.die )

            # hold data for training snake
            self.__holdData()

            # write data to file
            self.__dataRecorder.writeData()

            # switch game state to over
            self.__gameState = EGameState.over
            return

        # end one round when snake get food
        if self.isSnakeEating():
            # give reward of eating
            self.__snake.setReward( EReward.eat )

            # hold data for training snake
            self.__holdData()

            # write data to file
            self.__dataRecorder.writeData()

            # add snake body
            self.__snake.growUp()

            # configure new food
            self.createFood()
            return

        # reset reward
        self.__snake.setReward( EReward.none )

        # hold data for training snake
        self.__holdData()

    # calculate distance to closed barrier in four orientaion
    def __calcMinDistToBarrier( self, snakeBody, snakeLength, wallBoundary ):
        # init list
        upperList = [ wallBoundary.upper - snakeBody[ snakeLength - 1 ].y + 1 ]
        lowerList = [ snakeBody[ snakeLength - 1 ].y - wallBoundary.lower + 1 ]
        leftList = [ snakeBody[ snakeLength - 1 ].x - wallBoundary.left + 1 ]
        rightList = [ wallBoundary.right - snakeBody[ snakeLength - 1 ].x + 1 ]

        # traversal body list to find minimum distance of four orientation
        for i in range( snakeLength - 1 ):
            if snakeBody[ snakeLength - 1 ].x == snakeBody[ i ].x:
                # find upper-closet body
                if snakeBody[ snakeLength - 1 ].y < snakeBody[ i ].y:
                    upperList.append( snakeBody[ i ].y - snakeBody[ snakeLength - 1 ].y )
                # find lower-closet body
                elif snakeBody[ snakeLength - 1 ].y > snakeBody[ i ].y:
                    lowerList.append( snakeBody[ snakeLength - 1 ].y - snakeBody[ i ].y )
                # exception
                else:
                    assert( False )
            
            if snakeBody[ snakeLength - 1 ].y == snakeBody[ i ].y:
                # find left-closet body
                if snakeBody[ snakeLength - 1 ].x > snakeBody[ i ].x:
                    leftList.append( snakeBody[ i ].x - snakeBody[ snakeLength - 1 ].x )
                # find right-closet body
                elif snakeBody[ snakeLength - 1 ].x < snakeBody[ i ].x:
                    rightList.append( snakeBody[ snakeLength - 1 ].x - snakeBody[ i ].x )
                # exception
                else:
                    assert( False )
                    
        return TOrientalDist( min( upperList ), min( lowerList ), min( leftList ), min( rightList ) )

    # calculate coordinate different between snake head and food
    def __calcCoorDiffToFood( self, snakeHead, foodPos ):
        coorDiff = TCoor( snakeHead.x - foodPos.x, snakeHead.y - foodPos.y )
        return coorDiff

    def __holdData( self ):
        # calculate distance to closed barrier in four orientaion
        self.__minDistToBarrier = self.__calcMinDistToBarrier( self.__snake.getBodyPos(), \
                    self.__snake.getBodyLength(), self.__wall.getBoundary() )
        
        # calculate coordinate different between snake head and food
        self.__coorDiffToFood = self.__calcCoorDiffToFood( self.__snake.getHeadPos(), self.__food.getPos() )

        # write data to file
        self.__dataRecorder.holdData( self.__minDistToBarrier, self.__coorDiffToFood, \
                                        self.__snake.getMoveDir(), self.__snake.getReward() )