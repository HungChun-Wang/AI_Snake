import tensorflow as tf
import numpy as np
import random
from CommonDefine import EDirection

class CAutoCommander:
    def __init__( self ):
        # size of input
        self.inputSize = 8

        # size of output
        self.outputSize = 4

        # rate for random exploration
        self.explorationRate = 1.0

        # decent rate of exploration
        self.explorationDescentRate = 0.02

        # whether train neural network or not
        self.__trainFlag = True

        # neural network model for exploring environment
        self.NN = None

        # build neural network model
        self.defineModel()

    # set flag for training data
    def setTrainFlag( self, flag ):
        self.__trainFlag = flag

    # define model of neural network
    def defineModel( self ):
        # build neural network mode
        self.NN = tf.keras.Sequential( [
                    tf.keras.layers.Dense( 10, activation = tf.nn.relu, input_shape=( self.inputSize, ) ),
                    tf.keras.layers.Dense( 10, activation = tf.nn.relu ),
                    tf.keras.layers.Dense( 10, activation = tf.nn.relu ),
                    tf.keras.layers.Dense( self.outputSize ) ] )

        # compile Neural network 
        self.NN.compile( optimizer = 'SGD',
                         loss = 'mean_squared_error',
                         metrics = [ 'accuracy' ] )

    # decide snake move command
    def decideCmd( self, envState ):
        # random float in range 0 ~ 1
        rand = random.random()

        # add small chance for random exploration
        if rand >= self.explorationRate:
            QValue = self.NN( envState )
            return int( tf.argmax( QValue, 1 ) ) + 1
        elif rand >= self.explorationRate / 4 * 3:
            return EDirection.up
        elif rand >= self.explorationRate / 2:
            return EDirection.down
        elif rand >= self.explorationRate / 4:
            return EDirection.left
        elif rand >= 0:
            return EDirection.right
        else:
            assert( False )

    def train( self, data ):
        if self.__trainFlag == False:
            return

        if len( data ) <= self.inputSize:
            return

        # convert list to array
        data = np.asarray( data, dtype = np.float32 )

        # slice feature data
        state = data[ :-1, :8 ]
        nextState = data[ 1:, :8 ]
        action = ( data[ :-1, 8 ] - 1 ).astype( 'int32' )
        reward = data[ 1:, 9 ]

        # calculate target Q value
        target = self.NN( state ).numpy()
        QNext = self.NN( nextState )
        target[ np.arange( len( action ) ), action ] = reward + np.amax( QNext, 1 )

        # train neural network
        self.NN.fit( x = state, y = target, epochs = 20, verbose = 2 )

        # descent exploration rate
        self.explorationRate = self.explorationRate - self.explorationDescentRate
