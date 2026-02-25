import pygame
import sys

print("Pygame version:", pygame.ver)

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Pygame测试窗口")
print("窗口已创建，请查看任务栏")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill((255, 255, 255))
    pygame.display.flip()