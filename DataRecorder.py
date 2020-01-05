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
    # write data to file
    def writeData( self, minDistToBarrier, coorDiffToFood, roundStep, StepAcc ):
        # whether file exists
        isFileExist = False
        if os.path.isfile( 'SnakeData.csv' ):
            isFileExist = True

        # write data to file
        with open( 'SnakeData.csv', 'a', newline = '' ) as csvFile:
            fWrite = csv.writer( csvFile, delimiter=',' )

            # write title when create file
            if isFileExist == False:
                fieldnames = [ 'Upper Barrier Dist', 'Lower Barrier Dist', \
                            'Left Barrier Dist', 'Right Barrier Dist', \
                            'X Diff', 'Y Diff', 'Round Step', 'Total Step' ]
                fWrite.writerow( fieldnames )

            # write data
            data = [ minDistToBarrier.up, minDistToBarrier.down, \
                     minDistToBarrier.left, minDistToBarrier.right, \
                     coorDiffToFood.x, coorDiffToFood.y, roundStep, StepAcc ]
            fWrite.writerow( data )

        