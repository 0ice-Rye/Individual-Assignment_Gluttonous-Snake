import pygame
import sys
import os
import time
from game_env import SnakeGame
from button import Button
import menu
from ql_agent import QLAgent
import numpy as np

# 游戏状态常量
COUNTDOWN = 0
PLAYING = 1
PAUSED = 2
GAMEOVER = 3

def get_speed_from_score(score):
    """根据得分返回速度（帧率）"""
    if score >= 180:
        return 10
    elif score >= 150:
        return 9
    elif score >= 120:
        return 8
    elif score >= 90:
        return 7
    elif score >= 70:
        return 6
    elif score >= 40:
        return 5
    elif score >= 20:
        return 4
    else:
        return 3

def manual_play():
    """手动模式，返回 True 表示返回主菜单，False 表示退出程序"""
    pygame.init()
    game = SnakeGame(grid_size=20, cell_size=25, poison_enabled=True)
    screen = pygame.display.set_mode((game.width, game.height))
    pygame.display.set_caption("Snake - Game Mode")
    clock = pygame.time.Clock()

    # 状态变量
    state = COUNTDOWN
    countdown_start_time = pygame.time.get_ticks()
    countdown_number = 3
    action = 3  # 初始方向右
    play_time = 0
    play_start_time = 0
    paused_time = 0

    # 返回主菜单标志
    return_to_menu = False

    # 暂停按钮（右上角）
    pause_btn = Button(
        x=game.width - 100, y=10,
        width=80, height=30,
        text="Pause",
        color=(0, 100, 200), hover_color=(50, 150, 255),
        action=lambda: toggle_pause()
    )

    # 暂停界面的播放按钮（居中偏上）
    play_btn = Button(
        x=game.width//2 - 50, y=game.height//2 - 50,
        width=100, height=50,
        text="Play",
        color=(0, 150, 0), hover_color=(0, 255, 0),
        action=lambda: resume_game()
    )

    # 暂停界面的退出按钮（居中偏下）
    pause_exit_btn = Button(
        x=game.width//2 - 50, y=game.height//2 + 20,
        width=100, height=50,
        text="Exit",
        color=(100, 0, 0), hover_color=(200, 0, 0),
        action=lambda: exit_to_menu()
    )

    # 游戏结束界面的按钮
    button_width, button_height = 150, 50
    play_again_btn = Button(
        x=game.width//2 - button_width - 10,
        y=game.height//2,
        width=button_width, height=button_height,
        text="Play Again",
        color=(0, 100, 0), hover_color=(0, 200, 0),
        action=lambda: restart_game()
    )
    gameover_exit_btn = Button(
        x=game.width//2 + 10,
        y=game.height//2,
        width=button_width, height=button_height,
        text="Exit",
        color=(100, 0, 0), hover_color=(200, 0, 0),
        action=lambda: exit_to_menu()
    )

    def toggle_pause():
        nonlocal state, paused_time, play_start_time
        if state == PLAYING:
            state = PAUSED
            paused_time = pygame.time.get_ticks() - play_start_time

    def resume_game():
        nonlocal state, countdown_start_time, countdown_number
        if state == PAUSED:
            state = COUNTDOWN
            countdown_start_time = pygame.time.get_ticks()
            countdown_number = 3

    def restart_game():
        nonlocal state, countdown_start_time, countdown_number, action, play_time, play_start_time, paused_time
        game.reset()
        state = COUNTDOWN
        countdown_start_time = pygame.time.get_ticks()
        countdown_number = 3
        action = 3
        play_time = 0
        play_start_time = 0
        paused_time = 0

    def exit_to_menu():
        nonlocal return_to_menu, running
        return_to_menu = True
        running = False

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return_to_menu = False  # 直接退出，不返回菜单
            if state == PLAYING:
                pause_btn.handle_event(event)
            elif state == PAUSED:
                play_btn.handle_event(event)
                pause_exit_btn.handle_event(event)
            elif state == GAMEOVER:
                play_again_btn.handle_event(event)
                gameover_exit_btn.handle_event(event)

        # 状态逻辑
        if state == COUNTDOWN:
            elapsed = current_time - countdown_start_time
            if elapsed >= 1000:
                countdown_number -= 1
                countdown_start_time = current_time
                if countdown_number == 0:
                    state = PLAYING
                    play_start_time = current_time
                    if paused_time > 0:
                        play_start_time = current_time - paused_time
                        paused_time = 0

        elif state == PLAYING:
            if not game.done:
                speed = get_speed_from_score(game.score)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    new_action = 0
                elif keys[pygame.K_DOWN]:
                    new_action = 1
                elif keys[pygame.K_LEFT]:
                    new_action = 2
                elif keys[pygame.K_RIGHT]:
                    new_action = 3
                else:
                    new_action = action
                action = new_action
                game.step(action)
            else:
                state = GAMEOVER

        # 计算游玩时间
        if state == PLAYING:
            play_time = (current_time - play_start_time) / 1000.0

        # ---------- 绘制界面 ----------
        # 1. 绘制游戏区域
        game.render(screen)

        # 2. 绘制覆盖层
        if state != PLAYING:
            overlay = pygame.Surface((game.width, game.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))

        # 3. 绘制UI文字（黑色，确保在覆盖层之上可见）
        font = pygame.font.Font(None, 30)
        # 左上角得分和时间
        score_text = font.render(f"Score: {game.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 5))
        time_text = font.render(f"Time: {int(play_time//60):02d}:{int(play_time%60):02d}", True, (0, 0, 0))
        screen.blit(time_text, (10, 25))

        # 右上角速度
        speed = get_speed_from_score(game.score)
        speed_text = font.render(f"Speed: {speed}", True, (0, 0, 0))
        speed_rect = speed_text.get_rect()
        speed_rect.topright = (game.width - 150, 10)
        screen.blit(speed_text, speed_rect)

        # 左下角动作和奖励
        if game.last_action is not None:
            action_names = ["Up", "Down", "Left", "Right"]
            small_font = pygame.font.Font(None, 24)
            action_text = small_font.render(f"Action: {action_names[game.last_action]}", True, (100, 100, 100))
            reward_text = small_font.render(f"Reward: {game.last_reward:.1f}", True, (100, 100, 100))
            # 底部边距内 y = margin + game_height + 5 和 +25
            bottom_y1 = game.margin + game.game_height + 5
            bottom_y2 = game.margin + game.game_height + 25
            screen.blit(action_text, (10, bottom_y1))
            screen.blit(reward_text, (10, bottom_y2))

        # 绘制按钮
        if state == PLAYING:
            pause_btn.draw(screen)
        elif state == PAUSED:
            play_btn.draw(screen)
            pause_exit_btn.draw(screen)
        elif state == GAMEOVER:
            play_again_btn.draw(screen)
            gameover_exit_btn.draw(screen)

        # 绘制中央文字
        if state == COUNTDOWN:
            big_font = pygame.font.Font(None, 100)
            if countdown_number > 0:
                text = big_font.render(str(countdown_number), True, (255, 255, 255))
            else:
                text = big_font.render("GO!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(game.width//2, game.height//2))
            screen.blit(text, text_rect)
        elif state == GAMEOVER:
            big_font = pygame.font.Font(None, 48)
            text = big_font.render(f"Game Over! Score: {game.score}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(game.width//2, game.height//2 - 50))
            screen.blit(text, text_rect)

        pygame.display.flip()

        # 帧率控制
        if state == PLAYING:
            clock.tick(speed)
        else:
            clock.tick(10)

    pygame.quit()
    return return_to_menu

def ai_demo():
    """AI演示模式（带返回主菜单按钮）"""
    if not os.path.exists('qtable_final.pkl'):
        print("错误：找不到训练好的模型文件 'qtable_final.pkl'，请先运行 train.py 进行训练！")
        pygame.quit()
        sys.exit()

    game = SnakeGame(grid_size=20, cell_size=25, poison_enabled=True)
    agent = QLAgent()
    agent.load('qtable_final.pkl')

    pygame.init()
    screen = pygame.display.set_mode((game.width, game.height))
    pygame.display.set_caption("Snake - AI Demonstration ")
    clock = pygame.time.Clock()

    # 右上角退出按钮
    exit_btn = Button(
        x=game.width - 100, y=10,
        width=80, height=30,
        text="Exit",
        color=(100, 0, 0), hover_color=(200, 0, 0),
        action=lambda: set_exit_flag()
    )

    exit_to_menu = False
    def set_exit_flag():
        nonlocal exit_to_menu
        exit_to_menu = True

    state = game.reset()
    done = False
    play_start_time = pygame.time.get_ticks()
    play_time = 0

    while not exit_to_menu:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            exit_btn.handle_event(event)

        if not done:
            state_key = agent._discretize_state(state)
            q_values = agent.q_table[state_key]
            action = int(np.argmax(q_values))
            next_state, reward, done = game.step(action)
            state = next_state

            play_time = (current_time - play_start_time) / 1000.0
            speed = get_speed_from_score(game.score)
        else:
            # 游戏结束，显示黑色文字
            font = pygame.font.Font(None, 36)
            text = font.render(f"Game Over! Score: {game.score}", True, (0, 0, 0))
            screen.blit(text, (game.width // 2 - 100, game.height // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            state = game.reset()
            done = False
            play_start_time = pygame.time.get_ticks()
            continue

        game.render(screen)

        # 绘制UI文字（黑色）
        font = pygame.font.Font(None, 30)
        score_text = font.render(f"Score: {game.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 5))
        time_text = font.render(f"Time: {int(play_time // 60):02d}:{int(play_time % 60):02d}", True, (0, 0, 0))
        screen.blit(time_text, (10, 25))

        speed_text = font.render(f"Speed: {speed}", True, (0, 0, 0))
        speed_rect = speed_text.get_rect()
        speed_rect.topright = (game.width - 150, 10)
        screen.blit(speed_text, speed_rect)

        if game.last_action is not None:
            action_names = ["Up", "Down", "Left", "Right"]
            small_font = pygame.font.Font(None, 24)
            action_text = small_font.render(f"Action: {action_names[game.last_action]}", True, (100, 100, 100))
            reward_text = small_font.render(f"Reward: {game.last_reward:.1f}", True, (100, 100, 100))
            bottom_y1 = game.margin + game.game_height + 5
            bottom_y2 = game.margin + game.game_height + 25
            screen.blit(action_text, (10, bottom_y1))
            screen.blit(reward_text, (10, bottom_y2))

        # 绘制退出按钮
        exit_btn.draw(screen)

        pygame.display.flip()
        clock.tick(speed)

    # 退出循环后返回，主菜单重新显示
    pygame.quit()


if __name__ == "__main__":
    while True:
        mode = menu.show_menu()
        if mode == "manual":
            # 如果 manual_play 返回 True，则继续循环显示菜单；否则退出
            if manual_play():
                continue
            else:
                break
        elif mode == "ai":
            ai_demo()
        else:  # exit
            sys.exit()

