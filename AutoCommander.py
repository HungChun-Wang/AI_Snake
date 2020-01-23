from CommonDefine import direction
import tensorflow as tf
import numpy as np
import random

class CAutoCommander:
    def __init__( self ):
        # size of input
        self.inputSize = 6

        # size of output
        self.outputSize = 4

        # rate for random exploration
        self.explorationRate = 1

        # decent rate of exploration
        self.explorationDescentRate = 0.01

        # neural network model for exploring environment
        self.NN = None

        # loss function of learning
        self.lossModel = None

        # build neural network model
        self.defineModel()

    # define model of neural network
    def defineModel( self ):
        # build neural network mode
        self.NN = tf.keras.Sequential( [
                    tf.keras.layers.Dense( 100, activation = tf.nn.relu, input_shape=( self.inputSize, ) ),
                    tf.keras.layers.Dense( 100, activation = tf.nn.relu ),
                    tf.keras.layers.Dense( 100, activation = tf.nn.relu ),
                    tf.keras.layers.Dense( self.outputSize ) ] )

        # compile Neural network 
        self.NN.compile( optimizer = 'SGD',
                         loss = 'mean_squared_error',
                         metrics = [ 'accuracy' ] )

    # decide move direction command
    def decideCmd( self, envState ):
        # random float in range 0 ~ 1
        rand = random.random()

        # add small chance for random exploration
        if rand > self.explorationRate:
            QValue = self.NN( envState )
            return int( tf.argmax( QValue, 1 ) ) + 1
        elif rand > self.explorationRate / 4 * 3:
            return direction.up  
        elif rand > self.explorationRate / 2:
            return direction.down
        elif rand > self.explorationRate / 4 :
            return direction.left
        elif rand > 0:
            return direction.right
        else:
            assert( False )

    def train( self, data ):
        if len( data ) <= self.inputSize:
            return

        # convert list to array
        data = np.asarray( data, dtype = np.int32 )

        # slice feature data
        state = data[ :-1, :6 ]
        nextState = data[ 1:, :6 ]
        action = data[ :-1, 6 ] - 1
        reward = data[ 1:, 7 ]

        # calculate target Q value
        target = self.NN( state ).numpy()
        QNext = self.NN( nextState )
        target[ np.arange( len( action ) ), action ] = reward + np.amax( QNext, 1 )

        # train neural network
        self.NN.fit( x = state, y = target, epochs = 20 )

        # descent exploration rate
        self.explorationRate = self.explorationRate - self.explorationDescentRate