####### import pygame ########
import pygame

pygame.init()

########### screen width,Heght ###########

screen = pygame.display.set_mode((494, 595))

########## loading music ########

awav = pygame.mixer.Sound('a.wav')
swav = pygame.mixer.Sound('a.wav')
dwav = pygame.mixer.Sound('a.wav')
fwav = pygame.mixer.Sound('a.wav')
gwav = pygame.mixer.Sound('a.wav')
hwav = pygame.mixer.Sound('a.wav')

############# loading image #################

pianop = pygame.image.load('piano.png')

cp = pygame.image.load('cpiano.png')

########### cord ##############

c_pos_x = 500
c_pos_y = 152


############# draw function #########

def piano():
    screen.blit(pianop, (0, 0))


def cpiano(x, y):
    screen.blit(cp, (x, y))


######### loop ###########

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

            ## key pressed ##

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                c_pos_x = 402
                c_pos_y = 152
                hwav.play()

            if event.key == pygame.K_g:
                c_pos_x = 315
                gwav.play()

            if event.key == pygame.K_f:
                c_pos_x = 228
                fwav.play()

            if event.key == pygame.K_d:
                c_pos_x = 141
                dwav.play()

            if event.key == pygame.K_s:
                c_pos_x = 58
                swav.play()

            if event.key == pygame.K_a:
                c_pos_x = -22
                awav.play()

            #### key unpressed ####

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_h or event.key == pygame.K_g or event.key == pygame.K_f or event.key == pygame.K_d or event.key == pygame.K_s or event.key == pygame.K_a:
                c_pos_x = 500
                c_pos_y = 152

    ########## calling function ##########

    piano()
    cpiano(c_pos_x, c_pos_y)
    pygame.display.update()
