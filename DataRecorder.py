import os
import csv
from dataclasses import dataclass
from CommonDefine import TCoor

@dataclass
class TActionResult:
    up: bool
    down: bool
    left: bool
    right: bool

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

        # hold data for training
        self.__data = []

        # data for writing to file
        self.__writeData = [] 

        # max data number
        self.__dataNum = 0

    def getData( self ):
        return self.__data

    def clearData( self ):
        # clear hold data
        self.__data.clear()

    # save data temporary
    def holdData( self, envState, action, reward ):
        if self.__dataNum > 5000:
            self.__data.pop( 0 )

        # reshape data
        dataRow = envState[:]
        dataRow.append( int( action ) )
        dataRow.append( reward )
        
        # append to data list
        self.__data.append( dataRow )

        # add data number
        self.__dataNum += 1

    # write data to file
    def writeData( self ):
        # whether file exists
        isFileExist = False
        if os.path.isfile( self.__fileName ):
            isFileExist = True
"""
        # write data to file
        with open( self.__fileName, 'a', newline = '' ) as csvFile:
            fWrite = csv.writer( csvFile, delimiter=',' )

            # write title when create file
            if isFileExist == False:
                fWrite.writerow( self.__fieldName )

            # write data
            for i in range( len( self.__data ) ):
                fWrite.writerow( self.__data[ i ] )
"""