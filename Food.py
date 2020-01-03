import random
from CommonDefine import TCoor

class CFood:

    def __init__( self, appearRange ):
        # randomly decide the position of food
        self.__Pos = TCoor( random.randint( appearRange.left, appearRange.right ) \
                            , random.randint( appearRange.lower, appearRange.upper ) )

    # get position of food
    def getPos( self ):
        return self.__Pos