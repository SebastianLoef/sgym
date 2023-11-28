import pygame

from ._game import Environment


def play():
    env = Environment(render=True)
    env.reset()
    # pygame stuff
    running = True
    # pygame setup
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # keys
        keys = pygame.key.get_pressed()
        action = None
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            action = 0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            action = 2
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            action = 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            action = 3
        if keys[pygame.K_r]:
            env.reset()

        env.step(action)

    # flip() the display to put your work on screen
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    env.quit_rendering()


if __name__ == "__main__":
    play()
