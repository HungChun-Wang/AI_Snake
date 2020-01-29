import random
from enum import IntEnum
from CommonDefine import TCoor
from CommonDefine import EDirection

class CSnake:

    def __init__( self, actRange ):
        # randomly decide start position
        initPos = TCoor( random.randint( actRange.left, actRange.right ) \
                        , random.randint( actRange.lower, actRange.upper ) )

        # list for body location
        self.__bodyList = []
        
        # append first body
        self.__bodyList.append( initPos )

        # length of bady
        self.__bodyLength = 1

        # move direction
        self.__moveDir = EDirection.none

        # step number of single round
        self.__roundStep = 0

        # accumulated step number
        self.__stepAcc = 0

        # reward for Q learning
        self.__reward = 0.0

    # set snake move direction
    def setMoveDir( self, dir ):
        # set move direction
        self.__moveDir = dir

    # set reward for Q learning
    def setReward( self, reward ):
        self.__reward = reward

    # get snake move direction
    def getMoveDir( self ):
        return self.__moveDir

    # get position of snake head
    def getHeadPos( self ):
        return self.__bodyList[ self.__bodyLength - 1 ]

    # get position of snake body
    def getBodyPos( self ):
        return self.__bodyList

    # get length of snake body
    def getBodyLength( self ):
        return self.__bodyLength
    
    # get step number of single round
    def getRoundStep( self ):
        return self.__roundStep

    # get accumulated step number
    def getStepAcc( self ):
        return self.__stepAcc

    def getReward( self ):
        return self.__reward

    # get coordinate after move
    def calcMoveCoord( self, moveDir ):
        # body length should large than zero
        assert( self.__bodyLength > 0 )

        # get head position
        headPos = self.__bodyList[ self.__bodyLength - 1 ]

        # configure new body node
        headPos = TCoor( headPos.x, headPos.y )

        # find position according to move direction
        if moveDir == EDirection.up:
            headPos.y = headPos.y - 1
        elif moveDir == EDirection.down:
            headPos.y = headPos.y + 1
        elif moveDir == EDirection.left:
            headPos.x = headPos.x - 1
        elif moveDir == EDirection.right:
            headPos.x = headPos.x + 1
            
        return headPos

    # add body from tail
    def growUp( self ):
        # body length should not be zero
        assert( self.__bodyLength != 0 )

        # get tail position
        bodyPos = self.__bodyList[ 0 ]

        # configure new body node
        bodyPos = TCoor( bodyPos.x, bodyPos.y )

        # insert new node to tail
        self.__bodyList.insert( 0, bodyPos )

        # increase body length
        self.__bodyLength = self.__bodyLength + 1

        # clean round step
        self.__roundStep = 0

    # snake move front
    def move( self ):
        # get coordinate after moving
        headPos = self.calcMoveCoord( self.__moveDir )

        # remove tail and add new head
        self.__bodyList.append( headPos )
        self.__bodyList.pop( 0 )

        # accumulate step
        self.__stepAcc = self.__stepAcc + 1
        self.__roundStep = self.__roundStep + 1

    # whether snake bite itself
    def isOnBody( self, pos ):
        # whether head and body overlap
        for i in range( self.__bodyLength - 1 ):
            if self.__bodyList[ i ] == pos:
                return True
        return False

    # whether snake bite itself
    def isBite( self ):
        return self.isOnBody( self.__bodyList[ self.__bodyLength - 1 ] )