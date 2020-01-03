from dataclasses import dataclass

@dataclass
class TBoundary:
    upper : int
    lower : int
    left : int
    right : int

class CWall:
    def __init__( self, boundary ):
        self.__boundary = boundary

    def getBoundary( self ):
        return self.__boundary