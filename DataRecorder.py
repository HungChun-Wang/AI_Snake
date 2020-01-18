import os
import csv
from dataclasses import dataclass
from CommonDefine import TCoor

@dataclass
class TOrientalDist:
    up: int
    down: int
    left: int
    right: int

@dataclass
class TDataRecord:
    roundStep: int
    stepAcc: int

class CDataRecorder:
    def __init__( self, fileName, fieldName ):
        # the name of written file
        self.__fileName = fileName

        # field name of data
        self.__fieldName = fieldName

        self.__data = []

    # save data temporary
    def holdData( self, minDistToBarrier, coorDiffToFood, action, reward ):
        # reshape data
        dataRow = [ minDistToBarrier.up, minDistToBarrier.down, \
            minDistToBarrier.left, minDistToBarrier.right, \
            coorDiffToFood.x, coorDiffToFood.y, int( action ), int( reward ) ]
        
        # append to data list
        self.__data.append( dataRow )

    # write data to file
    def writeData( self ):
        # whether file exists
        isFileExist = False
        if os.path.isfile( self.__fileName ):
            isFileExist = True

        # write data to file
        with open( self.__fileName, 'a', newline = '' ) as csvFile:
            fWrite = csv.writer( csvFile, delimiter=',' )

            # write title when create file
            if isFileExist == False:
                fWrite.writerow( self.__fieldName )

            # write data
            for i in range( len( self.__data ) ):
                fWrite.writerow( self.__data[ i ] )

            # clear hold data
            self.__data.clear()