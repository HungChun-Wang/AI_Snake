import sys
import time
import pygame
from CommonDefine import direction
from pygame.locals import K_UP
from pygame.locals import K_DOWN
from pygame.locals import K_LEFT
from pygame.locals import K_RIGHT
from pygame.locals import KEYDOWN
from pygame.locals import QUIT
from pygame.locals import K_RETURN
from Referee import CReferee
from Referee import EGameState

Screen_Width = 600
Screen_Height = 480
Unit_Size = 5
White_Color = pygame.Color( 255, 255, 255 )
Red_Color = pygame.Color( 255, 0, 0 )
Background_Color = pygame.Color( 40, 40, 60 )

class CGUI:
    def __init__( self ):
        # init game
        pygame.init()

        # set window title
        pygame.display.set_caption( 'Snake' )

        # set window size
        self.__screen = pygame.display.set_mode( ( Screen_Width, Screen_Height ) )

        # configure referee
        self.__referee = CReferee( Screen_Width / Unit_Size, Screen_Height / Unit_Size )

    def start( self ):
        while True:
            # print start scrrean
            self.printInitScreen()

            # wait start key
            self.__startKeyInstruct()

            # wait for time interval
            time.sleep( 0.05 )

            # run game except game over
            while self.__referee.getGameState() == EGameState.running:
                # receive keyboard instruction
                self.__ctrlKeyInstruct()

                # do process which have to run every tick
                self.__referee.roundTask()

                self.__record_data()

                # print all element and update screen
                self.printGamingScreen()

                # wait for time interval
                time.sleep( 0.05 )

    def __record_data( self ):
        snakeHeadPos = self.__referee.getSnakeHeadPos()
        snakeBodyPos = self.__referee.getSnakeBody()
        wallBoundary = self.__referee.getWallBoundary()
        FoodPos = self.__referee.getFoodPos()

        distanceToWall_lst = [snakeHeadPos.y+1, 
                              wallBoundary.upper-snakeHeadPos.y+1, 
                              snakeHeadPos.x+1, 
                              wallBoundary.right-snakeHeadPos.x+1]
        DistanceToFood_lst = [abs(snakeHeadPos.x-FoodPos.x), abs(snakeHeadPos.y-FoodPos.y)]

        if len(snakeBodyPos)>1:
            upper_dist_lst = [snakeHeadPos.y - i.y for i in snakeBodyPos[0:-1] if snakeHeadPos.y - i.y >= 0 ]
            if len(upper_dist_lst)>0:
                upper_dist = sorted(upper_dist_lst)[0]
            else:
                upper_dist = 0

            lower_dist_lst = [i.y - snakeHeadPos.y for i in snakeBodyPos[0:-1] if i.y - snakeHeadPos.y >= 0 ]
            if len(lower_dist_lst)>0:
                lower_dist = sorted(lower_dist_lst)[0]
            else:
                lower_dist = 0

            left_dist_lst = [snakeHeadPos.x - i.x for i in snakeBodyPos[0:-1] if snakeHeadPos.x - i.x >= 0 ]
            if len(left_dist_lst)>0:
                left_dist = sorted(left_dist_lst)[0]
            else:
                left_dist = 0

            right_dist_lst = [i.x - snakeHeadPos.x for i in snakeBodyPos[0:-1] if i.x - snakeHeadPos.x >= 0 ]
            if len(right_dist_lst)>0:
                right_dist = sorted(right_dist_lst)[0]
            else:
                right_dist = 0

            DistanceToBody = [upper_dist, lower_dist, left_dist, right_dist]
        else:
            DistanceToBody= [0,0,0,0]

        print([distanceToWall_lst, DistanceToFood_lst, DistanceToBody])

        return [distanceToWall_lst, DistanceToFood_lst, DistanceToBody]

    # draw snake on window
    def __drawSnake( self ):
        snakeBody = self.__referee.getSnakeBody()
        snakeLength = self.__referee.getSnakeLength()

        for i in range( snakeLength ):
            pygame.draw.rect( self.__screen, White_Color, pygame.Rect \
                            ( snakeBody[ i ].x * Unit_Size, 
                              snakeBody[ i ].y * Unit_Size,
                              Unit_Size,
                              Unit_Size ) )

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

            # set move direction accroding to key
            if event.key == K_RETURN:
                self.__referee.start()

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
    def printInitScreen( self ):

        # print message in center of screen
        font = pygame.font.Font( None, 72 )
        content = "Press Enter"
        fWidth, fHeight = font.size( content )
        self.__screen.blit( font.render( content, True, White_Color ) \
                        , ( ( Screen_Width - fWidth ) / 2, ( Screen_Height - fHeight ) / 2 ) )

        # update scrren
        pygame.display.update()

    # print all element and update screen
    def printGamingScreen( self ):
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