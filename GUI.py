import sys
import time
import pygame
from enum import IntEnum
from CommonDefine import direction
from pygame.locals import K_UP
from pygame.locals import K_DOWN
from pygame.locals import K_LEFT
from pygame.locals import K_RIGHT
from pygame.locals import KEYDOWN
from pygame.locals import QUIT
from pygame.locals import K_RETURN
from pygame.locals import K_RSHIFT
from pygame.locals import K_RCTRL
from Referee import CReferee
from Referee import EGameState
from AutoCommander import CAutoCommander

Screen_Width = 600
Screen_Height = 480
Unit_Size = 10
Time_Interval = 0.05
White_Color = pygame.Color( 255, 255, 255 )
Red_Color = pygame.Color( 255, 0, 0 )
Background_Color = pygame.Color( 40, 40, 60 )

class EGUIState( IntEnum ):
    mainMenu = 0
    game = 1

class CGUI:
    def __init__( self ):
        # init game
        pygame.init()

        # set window title
        pygame.display.set_caption( 'Snake' )

        # game type
        self.__State = EGUIState.mainMenu

        # set window size
        self.__screen = pygame.display.set_mode( ( Screen_Width, Screen_Height ) )

        # configure referee
        self.__referee = CReferee( Screen_Width / Unit_Size, Screen_Height / Unit_Size )

        # auto commander
        self.__autoCommander = None

    def start( self ):
        while True:
            # main menu screen
            if self.__State == EGUIState.mainMenu:
                # print start scrrean
                self.__printInitScreen()

                # wait start key
                self.__startKeyInstruct()

            # game screen
            elif self.__State == EGUIState.game:
                # back to main menu when game over
                if self.__referee.getGameState() == EGameState.over:
                    self.__State = EGUIState.mainMenu
                    continue

                if self.__autoCommander != None:
                    envState = self.__referee.getEnvState()
                    cmd = self.__autoCommander.decideCmd( envState )
                    self.__putCmd( cmd )

                # receive keyboard instruction
                self.__ctrlKeyInstruct()

                # do process which have to run every tick
                self.__referee.roundTask()

                # print all element and update screen
                self.__printGamingScreen()

            # wait for time interval
            time.sleep( Time_Interval )

    # draw snake on window
    def __drawSnake( self ):
        snakeBody = self.__referee.getSnakeBody()
        snakeLength = self.__referee.getSnakeLength()

        for i in range( snakeLength ):
            pygame.draw.rect( self.__screen, White_Color, pygame.Rect \
                            ( snakeBody[ i ].x * Unit_Size, snakeBody[ i ].y * Unit_Size, \
                                Unit_Size, Unit_Size ) )

    # draw food on window
    def __drawFood( self ):
        foodPos = self.__referee.getFoodPos()

        pygame.draw.rect( self.__screen, Red_Color, pygame.Rect \
                        ( foodPos.x * Unit_Size, foodPos.y * Unit_Size, \
                            Unit_Size, Unit_Size ) )

    # deal with keyboard instruction
    def __startKeyInstruct( self ):
        for event in pygame.event.get():
            # exit game
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                return

            # key buttom from up to down
            if event.type != KEYDOWN:
                return

            # start manual game
            if event.key == K_RETURN:
                self.__referee.start()
                self.__State = EGUIState.game

            # start auto game
            elif event.key == K_RSHIFT:
                self.__referee.start()
                self.__autoCommander = CAutoCommander()
                self.__State = EGUIState.game

    # deal with keyboard instruction
    def __ctrlKeyInstruct( self ):
        # receive keyboard event
        for event in pygame.event.get():

            # key buttom from up to down
            if event.type != KEYDOWN:
                return

            # set move direction accroding to key
            if event.key == K_UP:
                self.__referee.setSnakeMoveDir( direction.up )
            elif event.key == K_DOWN:
                self.__referee.setSnakeMoveDir( direction.down )
            elif event.key == K_LEFT:
                self.__referee.setSnakeMoveDir( direction.left )
            elif event.key == K_RIGHT:
                self.__referee.setSnakeMoveDir( direction.right )

    # print beginning screen
    def __printInitScreen( self ):
        # print message in center of screen
        font = pygame.font.Font( None, 72 )
        content = "Press Enter"
        fWidth, fHeight = font.size( content )
        self.__screen.blit( font.render( content, True, White_Color ) \
                        , ( ( Screen_Width - fWidth ) / 2, ( Screen_Height - fHeight ) / 2 ) )

        # update scrren
        pygame.display.update()

    # print all element and update screen
    def __printGamingScreen( self ):
        # reflash background color
        self.__screen.fill( Background_Color )

        # print total number of eaten food
        font = pygame.font.Font( None, 18 )
        self.__screen.blit( font.render( f"Food: { self.__referee.getFoodNum() }" \
                            , True, White_Color ), ( 450, 10 ) )
        self.__screen.blit( font.render( f"Step: { self.__referee.getSnakeStepAcc() }" \
                            , True, White_Color ), ( 450, 30 ) )

        # draw snake and food
        self.__drawSnake()
        self.__drawFood()

        # update scrren
        pygame.display.update()

    # put command
    def __putCmd( self, cmd ):
        # set move direction accroding to key
        self.__referee.setSnakeMoveDir( cmd )