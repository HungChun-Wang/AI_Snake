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

Max_Round_Step = 1000

# game state type
class EGameState( IntEnum ):
    ready = 0
    running = 1
    over = 2

class EReward( IntEnum ):
    none = 0
    moveFarther = -0.001
    moveCloser = 0.001
    eat = 1
    die = -0.1

class CReferee:

    def __init__( self, lateralGridNum, verticalGridNum ):
        # boundary wall
        self.__wall = CWall( TBoundary( verticalGridNum - 1, 0, 0, lateralGridNum - 1 ) )

        # played snake
        self.__snake = None

        # targer food
        self.__food = None

        # maximal number of eaten food
        self.__maxFoodNum = 0

        # total num of eaten food
        self.__foodNum = 0

        # total round number
        self.__roundNum = 0

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
        # add round numer
        self.__roundNum += 1

        # configure snake
        self.__snake = CSnake( self.__wall.getBoundary() )

        # configure food
        self.createFood()

        # clean food number
        self.__foodNum = 0

        # switch game state to running
        self.__gameState = EGameState.running

        # distance from snake head to food in last tick
        self.__lastDist = float('inf')

        # current distance from snake head to food
        self.__dist = 0.0

        # calculate distance to closed barrier in four orientaion
        self.__minDistToBarrier = self.__calcMinDistToBarrier( self.__snake.getBodyPos(), \
                    self.__snake.getBodyLength(), self.__wall.getBoundary() )
        
        # calculate coordinate different between snake head and food
        self.__coorDiffToFood = self.__calcCoorDiff( self.__snake.getHeadPos(), self.__food.getPos() )

        # reset data in memory
        self.__dataRecorder.clearData()

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
    def getMaxFoodNum( self ):
        return self.__maxFoodNum

    # get total num of eaten food
    def getFoodNum( self ):
        return self.__foodNum

    # get state of game
    def getGameState( self ):
        return self.__gameState

    # get total round number
    def getRoundNum( self ):
        return self.__roundNum

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

    def __setMaxFoodNum( self ):
        if self.__maxFoodNum < self.__foodNum:
            self.__maxFoodNum = self.__foodNum

    def __setReward( self ):
        # penalty for die
        if self.__snake.isBite() or self.isSnakeCrash():
            self.__snake.setReward( EReward.die )
        # reward for eating food
        elif self.isSnakeEating():
            self.__snake.setReward( EReward.eat )
        # reward for moving closer
        elif self.__isSnakeCloser():
            self.__snake.setReward( EReward.moveCloser )
        # penalty for moving farther
        elif self.__isSnakeCloser() == False:
            self.__snake.setReward( EReward.moveFarther )
        # no reward
        else:
            self.__snake.setReward( EReward.none )

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

    def getData( self ):
        return self.__dataRecorder.getData()

    # whether snake head and food overlap
    def isSnakeEating( self ):
        if self.__snake.getHeadPos() == self.__food.getPos():
            return True

    # whether snake head out of boundary
    def isSnakeCrash( self ):
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

    def __isSnakeCloser( self ):
        if self.__dist < self.__lastDist:
            return True
        else:
            return False

    def __isRoundStepExceed( self ):
        return self.__snake.getRoundStep() > Max_Round_Step

    # do process which need to do every tick
    def tickTask( self ):
        if self.__snake.getMoveDir() == direction.none:
            return

        # snake move command
        self.__snake.move()

        # calculate distance from snake head to food
        self.__dist = self.__calcDist( self.__snake.getHeadPos(), self.__food.getPos() )

        # set reward
        self.__setReward()

        # game over when snake bite itself
        if self.__snake.isBite() or self.isSnakeCrash():
            # hold data for training snake
            self.__holdData()

            # write data to file
            self.__dataRecorder.writeData()

            # set maximal food number
            self.__setMaxFoodNum()

            # switch game state to over
            self.__gameState = EGameState.over
            return

        # end one round when snake get food
        if self.isSnakeEating():
            # add foodNum
            self.__foodNum = self.__foodNum + 1

            # hold data for training snake
            self.__holdData()

            # write data to file
            self.__dataRecorder.writeData()

            # add snake body
            self.__snake.growUp()

            # configure new food
            self.createFood()
            return

        if self.__isRoundStepExceed():
            # hold data for training snake
            self.__holdData()

            # write data to file
            self.__dataRecorder.writeData()

            # set maximal food number
            self.__setMaxFoodNum()

            # switch game state to over
            self.__gameState = EGameState.over
            return

        # hold data for training snake
        self.__holdData()

        # update last distance
        self.__lastDist = self.__dist

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
                elif snakeBody[ snakeLength - 1 ].y >= snakeBody[ i ].y:
                    lowerList.append( snakeBody[ snakeLength - 1 ].y - snakeBody[ i ].y )
            
            if snakeBody[ snakeLength - 1 ].y == snakeBody[ i ].y:
                # find left-closet body
                if snakeBody[ snakeLength - 1 ].x > snakeBody[ i ].x:
                    leftList.append( snakeBody[ i ].x - snakeBody[ snakeLength - 1 ].x )
                # find right-closet body
                elif snakeBody[ snakeLength - 1 ].x <= snakeBody[ i ].x:
                    rightList.append( snakeBody[ snakeLength - 1 ].x - snakeBody[ i ].x )
                    
        return TOrientalDist( min( upperList ), min( lowerList ), min( leftList ), min( rightList ) )

    # calculate coordinate different between two point
    def __calcCoorDiff( self, P1, P2 ):
        coorDiff = TCoor( P1.x - P2.x, P1.y - P2.y )
        return coorDiff

    # calculate the distance between two point
    def __calcDist( self, P1, P2 ):
        return ( ( P1.x - P2.x )**2 + ( P1.y - P2.y )**2 )**0.5

    def __holdData( self ):
        # calculate distance to closed barrier in four orientaion
        self.__minDistToBarrier = self.__calcMinDistToBarrier( self.__snake.getBodyPos(), \
                    self.__snake.getBodyLength(), self.__wall.getBoundary() )
        
        # calculate coordinate different between snake head and food
        self.__coorDiffToFood = self.__calcCoorDiff( self.__snake.getHeadPos(), self.__food.getPos() )

        # write data to file
        self.__dataRecorder.holdData( self.__minDistToBarrier, self.__coorDiffToFood, \
                                        self.__snake.getMoveDir(), self.__snake.getReward() )