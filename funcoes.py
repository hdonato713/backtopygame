import pygame

def inicializa():
    pygame.init()
    window = pygame.display.set_mode((1000,1000))

    assets = {

    }

    state = {

    }

    return window, assets, state

def recebe_eventos():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True

def desenha(window):
    window.fill((0,0,0))

    pygame.display.update()

def gameloop(window, assets, state):
    while recebe_eventos():
        desenha(window)

if __name__ =='__main__':
    window, assets, state = inicializa()
    gameloop(window, assets, state)