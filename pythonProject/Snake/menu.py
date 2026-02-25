import pygame
import sys
from button import Button

def show_menu():
    pygame.init()
    screen = pygame.display.set_mode((500, 400))
    pygame.display.set_caption("贪吃蛇 - 主菜单")
    clock = pygame.time.Clock()

    # 颜色
    black = (0, 0, 0)
    white = (255, 255, 255)
    green = (0, 150, 0)
    green_hover = (0, 255, 0)
    blue = (0, 0, 150)
    blue_hover = (0, 0, 255)
    red = (150, 0, 0)
    red_hover = (255, 0, 0)

    # 创建按钮
    button_width, button_height = 400, 50
    start_btn = Button(
        x=50, y=120,
        width=button_width, height=button_height,
        text="GameStart",
        color=green, hover_color=green_hover,
        action=lambda: set_mode("manual")
    )
    ai_btn = Button(
        x=50, y=200,
        width=button_width, height=button_height,
        text="AI Training Demonstration",
        color=blue, hover_color=blue_hover,
        action=lambda: set_mode("ai")
    )
    exit_btn = Button(
        x=50, y=280,
        width=button_width, height=button_height,
        text="Exit",
        color=red, hover_color=red_hover,
        action=lambda: set_mode("exit")
    )

    mode = None

    def set_mode(m):
        nonlocal mode
        mode = m

    while mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            start_btn.handle_event(event)
            ai_btn.handle_event(event)
            exit_btn.handle_event(event)

        screen.fill(black)

        # 绘制标题
        font = pygame.font.Font(None, 64)
        title = font.render("Gluttonous Snake", True, white)
        title_rect = title.get_rect(center=(250, 60))
        screen.blit(title, title_rect)

        # 绘制按钮
        start_btn.draw(screen)
        ai_btn.draw(screen)
        exit_btn.draw(screen)

        pygame.display.flip()
        clock.tick(30)

    return mode