from enum import IntEnum
import numpy as np
from dataclasses import dataclass
from CommonDefine import TCoor
from CommonDefine import EDirection
from Snake import CSnake
from Food import CFood
from Wall import CWall
from Wall import TBoundary
from DataRecorder import CDataRecorder
from DataRecorder import TOrientalDist
from DataRecorder import TActionResult

Max_Round_Step = 1000

# game state type
class EGameState( IntEnum ):
    ready = 0
    running = 1
    over = 2

@dataclass
class TReward:
    none: float
    eat: float
    die: float
    close: float
    far: float

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

        # define reward
        self.__rewardDef = TReward( 0, 10.0, -10.0, 1.0, -1.0 )

        # state parameter of environment
        self.__envState = []

        fieldnames = [ 'Up Safety', 'Down Safety', 'Left Safety', 'Right Safety',
                        'Food Up', 'Food Down', 'Food Left', 'Food Right',
                        'Action', 'Reward' ]

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

        # current distance from snake head to food
        self.__dist = self.__calcDist( self.__snake.getHeadPos(), self.__food.getPos() )

        # distance from snake head to food in last tick
        self.__lastDist = self.__dist

        # update environment parameter
        self.__updateEnv()

        # reset data in memory
#        self.__dataRecorder.clearData()

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
        return self.__envState

    # set move Direction of snake
    def setMoveDir( self, dir ):
        self.__snake.setMoveDir( dir )

        # update state parameter
        self.__updateEnv()

    def initMoveDir( self ):
        coorDiff = self.__calcCoorDiff( self.__snake.getHeadPos(), self.getFoodPos() )
        if coorDiff.x > 0:
            self.__snake.setMoveDir( EDirection.left )
        elif coorDiff.x < 0:
            self.__snake.setMoveDir( EDirection.right )
        elif coorDiff.y > 0:
            self.__snake.setMoveDir( EDirection.up )
        else:
            self.__snake.setMoveDir( EDirection.down )
        
        # update state parameter
        self.__updateEnv()

    def __setMaxFoodNum( self ):
        if self.__maxFoodNum < self.__foodNum:
            self.__maxFoodNum = self.__foodNum

    def __setReward( self ):
        # penalty for die
        if self.__snake.isBite() or self.__isOutOfBound( self.__snake.getHeadPos() ):
            self.__snake.setReward( self.__rewardDef.die )
        # reward for eating food
        elif self.__isSnakeEating():
            self.__snake.setReward( self.__rewardDef.eat )
        elif self.__isSnakeCloser():
            self.__snake.setReward( self.__rewardDef.close )
        # no reward
        else:
            self.__snake.setReward( self.__rewardDef.far )

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
    def __isSnakeEating( self ):
        if self.__snake.getHeadPos() == self.__food.getPos():
            return True

    # whether snake close to wall comparing to last tick
    def __isSnakeCloser( self ):
        if self.__dist < self.__lastDist:
            return True
        else:
            return False

    # whether input position is out of wall boundary
    def __isOutOfBound( self, pos ):
        if self.__findDirOfOutBound( pos ) == EDirection.none:
            return False
        return True

    # find the direction of boundary which is broken
    def __findDirOfOutBound( self, pos ):
        # get wall boundary
        boundary = self.__wall.getBoundary()

        # which direction of boundary is broken
        if pos.x < boundary.left:
            return EDirection.left
        elif pos.x > boundary.right:
            return EDirection.right
        elif pos.y < boundary.lower:
            return EDirection.down
        elif pos.y > boundary.upper: 
            return EDirection.up
        else:
            return EDirection.none

    # number of round step exceed maximum
    def __isRoundStepExceed( self ):
        return self.__snake.getRoundStep() > Max_Round_Step

    # do process which need to do every tick
    def tickTask( self ):
        if self.__snake.getMoveDir() == EDirection.none:
            return

        # hold data for training snake
        self.__holdData()

        # snake move command
        self.__snake.move()

        # calculate distance from snake head to food
        self.__dist = self.__calcDist( self.__snake.getHeadPos(), self.__food.getPos() )

        # update enviroment state
        self.__updateEnv()

        # set reward
        self.__setReward()

        # game over when snake bite itself
        if self.__snake.isBite() or self.__isOutOfBound( self.__snake.getHeadPos() ):
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
        if self.__isSnakeEating():
            # add foodNum
            self.__foodNum = self.__foodNum + 1

            # write data to file
            self.__dataRecorder.writeData()

            # add snake body
            self.__snake.growUp()

            # configure new food
            self.createFood()

            # reset data in memory
#            self.__dataRecorder.clearData()
            return

        if self.__isRoundStepExceed():
            # write data to file
            self.__dataRecorder.writeData()

            # set maximal food number
            self.__setMaxFoodNum()

            # switch game state to over
            self.__gameState = EGameState.over
            return

        # update last distance
        self.__lastDist = self.__dist

    # update environment state parameters
    def __updateEnv( self ):
        # get state parameter
        dirSafety = self.__findDirSafety()
        dirToFood = self.__findDirToFood()

        # set to member
        self.__envState = [ int( dirSafety.up ), int( dirSafety.down ), int( dirSafety.left ), int( dirSafety.right ),
                            int( dirToFood.up ), int( dirToFood.down ), int( dirToFood.left ), int( dirToFood.right ) ]

    # whether all action are safe
    def __findDirSafety( self ):
        # initialize variable
        dirSafety = TActionResult( False, False, False, False )
        
        # check safety of all move direction
        dirSafety.up = self.__isMoveDirSafe( EDirection.up )
        dirSafety.down = self.__isMoveDirSafe( EDirection.down )
        dirSafety.left = self.__isMoveDirSafe( EDirection.left )
        dirSafety.right = self.__isMoveDirSafe( EDirection.right )

        return dirSafety

    # whether move direction make snake close to food
    def __findDirToFood( self ):

        # get snake head and food position
        pos = self.__snake.getHeadPos()
        food = self.__food.getPos()

        # initialize variable
        isDirCloser = TActionResult( False, False, False, False )

        if food.x > pos.x:
            isDirCloser.right = True
        elif food.x < pos.x:
            isDirCloser.left = True

        if food.y > pos.y:
            isDirCloser.down = True
        if food.y < pos.y:
            isDirCloser.up = True
        
        return isDirCloser

    # whether move direction are safe
    def __isMoveDirSafe( self, moveDir ):
        # get snake head coordinate after moving 
        nextCoord = self.__snake.calcMoveCoord( moveDir )
        return not self.__isOutOfBound( nextCoord ) and not self.__snake.isOnBody( nextCoord )

    # calculate coordinate different between two point
    def __calcCoorDiff( self, P1, P2 ):
        coorDiff = TCoor( P1.x - P2.x, P1.y - P2.y )
        return coorDiff

    # calculate the distance between two point
    def __calcDist( self, P1, P2 ):
        return ( ( P1.x - P2.x )**2 + ( P1.y - P2.y )**2 )**0.5

    # hold training data
    def __holdData( self ):
        # write data to file
        self.__dataRecorder.holdData( self.__envState, self.__snake.getMoveDir(), self.__snake.getReward() )