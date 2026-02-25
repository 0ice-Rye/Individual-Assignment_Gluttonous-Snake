from game_env import SnakeGame
from ql_agent import QLAgent
import numpy as np
import matplotlib.pyplot as plt
import pygame
import sys

def train(episodes=10000, render_every=1000, save_path='qtable.pkl'):
    """
    训练智能体（启用毒药）
    episodes: 训练轮数（10000轮）
    render_every: 每隔多少轮渲染一次游戏界面（设为0则不渲染）
    save_path: 保存Q表的文件路径
    """
    # 初始化环境和智能体（启用毒药）
    env = SnakeGame(grid_size=20, cell_size=25, poison_enabled=True)
    agent = QLAgent(alpha=0.05, gamma=0.95, epsilon=1.0,
                    epsilon_min=0.01, epsilon_decay=0.998)  # 探索衰减

    # 记录得分和平均得分
    scores = []
    avg_scores = []
    record_points = []  # 记录平均得分对应的episode

    # 如果需要渲染，初始化pygame
    if render_every > 0:
        pygame.init()
        screen = pygame.display.set_mode((env.width, env.height))
        pygame.display.set_caption("训练中 - 贪吃蛇")
        clock = pygame.time.Clock()
    else:
        screen = None
        clock = None

    for episode in range(1, episodes + 1):
        state = env.reset()
        total_reward = 0
        done = False

        while not done:
            # 选择动作
            action = agent.get_action(state)
            # 执行动作
            next_state, reward, done = env.step(action)
            # 更新Q表
            agent.update(state, action, reward, next_state, done)
            # 累加奖励
            total_reward += reward
            # 更新状态
            state = next_state

            # 如果需要渲染且当前episode满足条件
            if render_every > 0 and episode % render_every == 0:
                # 处理pygame事件（允许关闭窗口）
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                env.render(screen)
                # 在训练时显示得分
                font = pygame.font.Font(None, 36)
                score_text = font.render(f"Score: {env.score}", True, (255, 255, 255))
                screen.blit(score_text, (10, 10))
                pygame.display.flip()
                clock.tick(10)  # 控制渲染速度

        # 记录得分（吃到宝石的总分，可能为负）
        scores.append(env.score)

        # 每1000轮计算一次平均得分
        if episode % 1000 == 0:
            avg_score = np.mean(scores[-1000:])
            avg_scores.append(avg_score)
            record_points.append(episode)
            print(f"Episode {episode}/{episodes} | 平均得分(最近1000轮): {avg_score:.2f} | Epsilon: {agent.epsilon:.3f}")

    # 训练结束，保存Q表
    agent.save(save_path)
    print(f"训练完成，Q表已保存至 {save_path}")

    # 绘制学习曲线
    plt.figure(figsize=(10, 5))
    plt.plot(record_points, avg_scores, marker='o', linestyle='-', color='b')
    plt.xlabel('Episode')
    plt.ylabel('Average Score (last 1000 episodes)')
    plt.title('Q-learning Training Progress (with poison)')
    plt.grid(True)
    plt.savefig('training_curve.png')
    plt.show()

    return agent

def demo(agent_path='qtable.pkl', grid_size=20):
    """
    加载训练好的智能体并演示（供main.py调用）
    """
    env = SnakeGame(grid_size=grid_size, cell_size=25, poison_enabled=True)
    agent = QLAgent()
    try:
        agent.load(agent_path)
        print("模型加载成功，开始演示...")
    except Exception as e:
        print(f"模型加载失败：{e}")
        return

    pygame.init()
    screen = pygame.display.set_mode((env.width, env.height))
    pygame.display.set_caption("AI 演示 - 贪吃蛇")
    clock = pygame.time.Clock()

    state = env.reset()
    done = False
    play_start_time = pygame.time.get_ticks()
    play_time = 0

    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not done:
            # 演示时完全利用：直接取Q值最大的动作
            state_key = agent._discretize_state(state)  # noqa
            q_values = agent.q_table[state_key]
            action = int(np.argmax(q_values))
            next_state, reward, done = env.step(action)
            state = next_state

            play_time = (current_time - play_start_time) / 1000.0
            speed = 3  # 演示时固定速度或可自定义
        else:
            # 游戏结束，显示得分并等待3秒后重置
            font = pygame.font.Font(None, 36)
            text = font.render(f"Game Over! Score: {env.score}", True, (255, 255, 255))
            screen.blit(text, (env.width // 2 - 100, env.height // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            state = env.reset()
            done = False
            play_start_time = pygame.time.get_ticks()

        env.render(screen)

        # 绘制UI（得分、时间）
        font = pygame.font.Font(None, 30)
        score_text = font.render(f"Score: {env.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        time_text = font.render(f"Time: {int(play_time//60):02d}:{int(play_time%60):02d}", True, (255, 255, 255))
        screen.blit(time_text, (10, 40))

        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    trained_agent = train(episodes=10000, render_every=1000, save_path='qtable.pkl')
    # 训练结束后自动进入演示模式（可选，如需演示请取消下一行注释）
    # demo('qtable.pkl')