import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display (width, height)
screen = pygame.display.set_mode((800, 600))

# Set window caption
pygame.display.set_caption("Pygame Window Test")

# Set a background color (RGB)
background_color = (0, 0, 0)

# Main loop flag
running = True

# Main loop
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with the background color
    screen.fill(background_color)

    # Draw a rectangle (just as an example)
    pygame.draw.rect(screen, (255, 0, 0), (100, 100, 200, 100))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()