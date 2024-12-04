import pygame
import sys

# Initialize Pygame and set up the display
pygame.init()
size = width, height = 640, 480
screen = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)

# Set up hardware-accelerated rendering
hardware_surface = pygame.Surface(size, pygame.HWSURFACE | pygame.DOUBLEBUF)

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Defining the main game loop
def main():
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Logic to update your game objects

        # Clear screen
        hardware_surface.fill(BLACK)

        # Game drawing goes here
        # Example: A red rectangle that will be hardware accelerated
        pygame.draw.rect(hardware_surface, RED, (150, 100, 100, 50))

        # Swap the display surface with the hardware surface
        screen.blit(hardware_surface, (0, 0))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate to 60 fps
        clock.tick(60)

    pygame.quit()
    sys.exit()


# Run the game
if __name__ == "__main__":
    main()
