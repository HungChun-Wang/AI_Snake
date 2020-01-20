from CommonDefine import direction
import tensorflow as tf
import numpy as np
import random

class CAutoCommander:
    def __init__( self ):
        self.input = None
        self.output = None
        self.target = None
        self.inputSize = 0
        self.outputSize = 0
        self.learningRate = 0.1
        self.explorationRate = 0.1
        self.model = None

        self.defineModel()

    # define model of neural network
    def defineModel( self ):
        self.inputSize = 6
        self.outputSize = 4
        
        # build neural network mode
        self.model = tf.keras.Sequential( [
                    tf.keras.layers.Dense( 10, activation = tf.nn.relu, input_shape=( 1, self.inputSize ) ),
                    tf.keras.layers.Dense( 10, activation = tf.nn.relu ),
                    tf.keras.layers.Dense( self.outputSize ) ] )

    # decide move direction command
    def decideCmd( self, envState ):
        # random number in range 0 ~ 1
        rand = random.random()

        if rand > self.explorationRate:
            QValue = self.model( envState )
            return int( tf.math.argmax( QValue, 1 ) ) + 1
        elif rand >= self.explorationRate / 3 * 2:
            return direction.down
        elif rand >= self.explorationRate / 3:
            return direction.left
        else:
            return direction.right



#    def __CalcQValue( self, state ):
#        return self.session.run( self.output, feed_dict = { self.input: state } )