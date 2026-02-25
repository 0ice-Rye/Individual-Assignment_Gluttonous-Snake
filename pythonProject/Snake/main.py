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
    if score >= 90:
        return 6
    elif score >= 50:
        return 5
    elif score >= 20:
        return 4
    else:
        return 3

def manual_play():
    pygame.init()
    game = SnakeGame(grid_size=20, cell_size=25, poison_enabled=True)
    screen = pygame.display.set_mode((game.width, game.height))
    pygame.display.set_caption("贪吃蛇 - 手动模式")
    clock = pygame.time.Clock()

    # 状态变量
    state = COUNTDOWN
    countdown_start_time = pygame.time.get_ticks()
    countdown_number = 3
    action = 3  # 初始方向右
    play_time = 0  # 游玩时间（秒）
    play_start_time = 0
    paused_time = 0  # 暂停累积时间

    # 暂停按钮（右上角）
    pause_btn = Button(
        x=game.width - 80, y=10,
        width=60, height=30,
        text="Pause",
        color=(100, 100, 100), hover_color=(150, 150, 150),
        action=lambda: toggle_pause()
    )

    # 播放按钮（中间，仅在暂停时显示）
    play_btn = Button(
        x=game.width//2 - 50, y=game.height//2 - 25,
        width=100, height=50,
        text="Play",
        color=(0, 150, 0), hover_color=(0, 255, 0),
        action=lambda: resume_game()
    )

    # 重新开始和退出按钮（游戏结束用）
    button_width, button_height = 150, 50
    play_again_btn = Button(
        x=game.width//2 - button_width - 10,
        y=game.height//2,
        width=button_width, height=button_height,
        text="Play Again",
        color=(0, 100, 0), hover_color=(0, 200, 0),
        action=lambda: restart_game()
    )
    exit_btn = Button(
        x=game.width//2 + 10,
        y=game.height//2,
        width=button_width, height=button_height,
        text="Exit",
        color=(100, 0, 0), hover_color=(200, 0, 0),
        action=lambda: sys.exit()
    )

    def toggle_pause():
        nonlocal state, paused_time, play_start_time
        if state == PLAYING:
            state = PAUSED
            paused_time = pygame.time.get_ticks() - play_start_time  # 记录已游玩时间
        # 如果已经暂停，点击暂停按钮无效，应由播放按钮处理

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

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if state == PLAYING:
                pause_btn.handle_event(event)
            elif state == PAUSED:
                play_btn.handle_event(event)
            elif state == GAMEOVER:
                play_again_btn.handle_event(event)
                exit_btn.handle_event(event)

        # 状态逻辑
        if state == COUNTDOWN:
            elapsed = current_time - countdown_start_time
            if elapsed >= 1000:
                countdown_number -= 1
                countdown_start_time = current_time
                if countdown_number == 0:
                    state = PLAYING
                    play_start_time = current_time  # 开始计时
                    if paused_time > 0:
                        # 如果是从暂停恢复，调整开始时间
                        play_start_time = current_time - paused_time
                        paused_time = 0

        elif state == PLAYING:
            if not game.done:
                # 速度控制
                speed = get_speed_from_score(game.score)
                # 读取键盘
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

        # 计算游玩时间（仅当PLAYING时累积）
        if state == PLAYING:
            play_time = (current_time - play_start_time) / 1000.0

        # ---------- 绘制区域 ----------
        # 1. 绘制游戏区域（无UI文字）
        game.render(screen)

        # 2. 绘制覆盖层（半透明遮罩，针对非PLAYING状态）
        if state == COUNTDOWN:
            overlay = pygame.Surface((game.width, game.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
        elif state == PAUSED:
            overlay = pygame.Surface((game.width, game.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
        elif state == GAMEOVER:
            overlay = pygame.Surface((game.width, game.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))

        # 3. 绘制所有UI（文字和按钮），确保在覆盖层之上
        # 左上角得分和时间
        font = pygame.font.Font(None, 30)
        score_text = font.render(f"Score: {game.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        time_text = font.render(f"Time: {int(play_time//60):02d}:{int(play_time%60):02d}", True, (255, 255, 255))
        screen.blit(time_text, (10, 40))

        # 右上角速度（调整位置避免与暂停按钮重叠）
        speed = get_speed_from_score(game.score)
        speed_text = font.render(f"Speed: {speed}", True, (200, 200, 200))
        speed_rect = speed_text.get_rect()
        speed_rect.topright = (game.width - 150, 10)
        screen.blit(speed_text, speed_rect)

        # 左下角动作和奖励
        if game.last_action is not None:
            action_names = ["Up", "Down", "Left", "Right"]
            small_font = pygame.font.Font(None, 24)
            action_text = small_font.render(f"Action: {action_names[game.last_action]}", True, (200, 200, 200))
            reward_text = small_font.render(f"Reward: {game.last_reward:.1f}", True, (200, 200, 200))
            screen.blit(action_text, (10, game.height - 50))
            screen.blit(reward_text, (10, game.height - 25))

        # 绘制按钮（根据状态）
        if state == PLAYING:
            pause_btn.draw(screen)
        elif state == PAUSED:
            play_btn.draw(screen)
        elif state == GAMEOVER:
            play_again_btn.draw(screen)
            exit_btn.draw(screen)

        # 绘制中央文字（根据状态）
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
        # PAUSED状态不需要中央文字，播放按钮已经足够

        pygame.display.flip()

        # 根据状态设置帧率
        if state == PLAYING:
            clock.tick(get_speed_from_score(game.score))
        else:
            clock.tick(10)

    pygame.quit()
    sys.exit()

def ai_demo():
    """AI演示模式，同样加入速度控制和UI显示"""
    if not os.path.exists('qtable.pkl'):
        print("错误：找不到训练好的模型文件 'qtable.pkl'，请先运行 train.py 进行训练！")
        pygame.quit()
        sys.exit()

    game = SnakeGame(grid_size=20, cell_size=25, poison_enabled=True)
    agent = QLAgent()
    agent.load('qtable.pkl')

    pygame.init()
    screen = pygame.display.set_mode((game.width, game.height))
    pygame.display.set_caption("AI 演示 - 贪吃蛇")
    clock = pygame.time.Clock()

    state = game.reset()
    done = False
    play_start_time = pygame.time.get_ticks()
    play_time = 0

    # 为简化，AI演示不加入暂停按钮，但保留速度变化和UI显示
    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not done:
            state_key = agent._discretize_state(state)
            q_values = agent.q_table[state_key]
            action = int(np.argmax(q_values))
            next_state, reward, done = game.step(action)
            state = next_state

            play_time = (current_time - play_start_time) / 1000.0
            speed = get_speed_from_score(game.score)
        else:
            # 游戏结束，显示得分并等待3秒后重置
            font = pygame.font.Font(None, 36)
            text = font.render(f"Game Over! Score: {game.score}", True, (255, 255, 255))
            screen.blit(text, (game.width // 2 - 100, game.height // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            state = game.reset()
            done = False
            play_start_time = pygame.time.get_ticks()
            continue

        # 绘制
        game.render(screen)

        # 绘制UI（与手动模式一致，但无按钮）
        font = pygame.font.Font(None, 30)
        score_text = font.render(f"Score: {game.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        time_text = font.render(f"Time: {int(play_time//60):02d}:{int(play_time%60):02d}", True, (255, 255, 255))
        screen.blit(time_text, (10, 40))

        # 右上角速度
        speed_text = font.render(f"Speed: {speed}", True, (200, 200, 200))
        speed_rect = speed_text.get_rect()
        speed_rect.topright = (game.width - 150, 10)
        screen.blit(speed_text, speed_rect)

        # 左下角动作和奖励
        if game.last_action is not None:
            action_names = ["Up", "Down", "Left", "Right"]
            small_font = pygame.font.Font(None, 24)
            action_text = small_font.render(f"Action: {action_names[game.last_action]}", True, (200, 200, 200))
            reward_text = small_font.render(f"Reward: {game.last_reward:.1f}", True, (200, 200, 200))
            screen.blit(action_text, (10, game.height - 50))
            screen.blit(reward_text, (10, game.height - 25))

        pygame.display.flip()
        clock.tick(speed)

if __name__ == "__main__":
    mode = menu.show_menu()
    if mode == "manual":
        manual_play()
    elif mode == "ai":
        ai_demo()
    else:
        sys.exit()