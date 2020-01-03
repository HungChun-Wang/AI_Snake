import random
from CommonDefine import direction
from CommonDefine import TCoor
from dataclasses import dataclass

class CSnake:

    def __init__( self, actRange ):
        # randomly decide start position
        initPos = TCoor( random.randint( actRange.lower, actRange.upper ) \
                        , random.randint( actRange.left, actRange.right ) )

        # list for body location
        self.__bodyList = []
        
        # append first body
        self.__bodyList.append( initPos )

        # length of bady
        self.__bodyLength = 1

        # move direction
        self.__moveDir = direction.none

        # accumulated step number
        self.__stepAcc = 0

    # set snake move direction
    def setMoveDir( self, dir ):
        self.__moveDir = dir

    # get position of snake head
    def getHeadPos( self ):
        return self.__bodyList[ self.__bodyLength - 1 ]

    # get position of snake body
    def getBodyPos( self ):
        return self.__bodyList

    # get length of snake body
    def getBodyLength( self ):
        return self.__bodyLength
    
    # get accumulated step number
    def getStepAcc( self ):
        return self.__stepAcc

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

    # snake move front
    def move( self ):
        # body length should not be zero
        assert( self.__bodyLength != 0 )

        # get head position
        bodyPos = self.__bodyList[ self.__bodyLength - 1 ]

        # configure new body node
        bodyPos = TCoor( bodyPos.x, bodyPos.y )

        # find new position according to move direction
        if self.__moveDir == direction.up:
            bodyPos.y = bodyPos.y - 1
        elif self.__moveDir == direction.down:
            bodyPos.y = bodyPos.y + 1
        elif self.__moveDir == direction.left:
            bodyPos.x = bodyPos.x - 1
        elif self.__moveDir == direction.right:
            bodyPos.x = bodyPos.x + 1
        else:
            return

        # remove tail and add new head
        self.__bodyList.append( bodyPos )
        self.__bodyList.pop( 0 )

        # accumulate step
        self.__stepAcc = self.__stepAcc + 1

    # whether snake bite itself
    def isBite( self ):
        # whether head and body overlap
        for i in range( self.__bodyLength - 1 ):
            if self.__bodyList[ i ] == self.__bodyList[ self.__bodyLength - 1 ]:
                return True
        return False