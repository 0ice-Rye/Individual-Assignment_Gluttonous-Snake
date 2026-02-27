from game_env import SnakeGame
from ql_agent import QLAgent
import numpy as np
import matplotlib.pyplot as plt
import pygame
import sys
import os

def train_phase(env_config, agent, episodes, phase_name, render_every=1000, render_fps=30):
    """
    单个阶段的训练函数
    env_config: 环境参数字典
    agent: 智能体实例
    episodes: 本阶段训练轮数
    phase_name: 阶段名称（用于显示）
    render_every: 渲染间隔
    """
    env = SnakeGame(**env_config)
    scores = []
    avg_scores = []
    record_points = []

    # 初始化渲染
    if render_every > 0:
        pygame.init()
        screen = pygame.display.set_mode((env.width, env.height))
        pygame.display.set_caption(f"训练 - {phase_name}")
        clock = pygame.time.Clock()
    else:
        screen = None
        clock = None

    for episode in range(1, episodes + 1):
        state = env.reset()
        done = False

        while not done:
            action = agent.get_action(state)
            next_state, reward, done = env.step(action)
            agent.update(state, action, reward, next_state, done)
            state = next_state

            if render_every > 0 and episode % render_every == 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                env.render(screen)
                font = pygame.font.Font(None, 36)
                score_text = font.render(f"Score: {env.score}", True, (0, 0, 0))
                screen.blit(score_text, (10, 10))
                pygame.display.flip()
                clock.tick(render_fps)

        scores.append(env.score)

        if episode % 1000 == 0:
            avg_score = np.mean(scores[-1000:])
            avg_scores.append(avg_score)
            record_points.append(episode)
            print(f"[{phase_name}] Episode {episode}/{episodes} | 平均得分(最近1000轮): {avg_score:.2f} | Epsilon: {agent.epsilon:.3f}")

    return agent, scores, avg_scores, record_points


def multi_stage_train(total_episodes=30000, render_every=1000):
    """
    多阶段训练
    total_episodes: 总训练轮数，按比例分配
    """
    # 各阶段轮数分配
    phase1_episodes = int(total_episodes * 0.4)   # 40% 无毒药
    phase2_episodes = int(total_episodes * 0.3)   # 30% 毒药延迟
    phase3_episodes = total_episodes - phase1_episodes - phase2_episodes  # 剩余 30% 毒药立即

    print("===== 多阶段训练开始 =====")
    print(f"阶段1 (无毒药): {phase1_episodes} 轮")
    print(f"阶段2 (毒药延迟10秒): {phase2_episodes} 轮")
    print(f"阶段3 (毒药立即出现): {phase3_episodes} 轮")

    # 创建智能体（初始参数）
    agent = QLAgent(alpha=0.05, gamma=0.95, epsilon=1.0,
                    epsilon_min=0.01, epsilon_decay=0.999)

    # 阶段1：无毒药
    print("\n====== 阶段1：无毒药 ======")
    config1 = {
        'grid_size': 20,
        'cell_size': 25,
        'poison_enabled': False,
        'poison_immediate': False   # 设为True也不影响，因为poison_enabled=False
    }
    agent, scores1, avg1, points1 = train_phase(config1, agent, phase1_episodes, "Phase1-NoPoison", render_every)
    agent.save("qtable_phase1.pkl")
    print("阶段1完成，Q表已保存为 qtable_phase1.pkl")

    # 阶段2：毒药延迟出现
    print("\n====== 阶段2：毒药延迟出现 (10秒后) ======")
    # 加载阶段1的Q表（agent已经是训练后的，无需重新加载，但可以重置epsilon以保持探索）
    agent.epsilon = 0.3   # 提高探索率，让AI适应新环境
    config2 = {
        'grid_size': 20,
        'cell_size': 25,
        'poison_enabled': True,
        'poison_immediate': False   # 延迟出现
    }
    agent, scores2, avg2, points2 = train_phase(config2, agent, phase2_episodes, "Phase2-PoisonDelayed", render_every)
    agent.save("qtable_phase2.pkl")
    print("阶段2完成，Q表已保存为 qtable_phase2.pkl")

    # 阶段3：毒药立即出现
    print("\n====== 阶段3：毒药立即出现 ======")
    agent.epsilon = 0.1   # 降低探索，更多利用已学知识
    config3 = {
        'grid_size': 20,
        'cell_size': 25,
        'poison_enabled': True,
        'poison_immediate': True    # 立即出现
    }
    agent, scores3, avg3, points3 = train_phase(config3, agent, phase3_episodes, "Phase3-PoisonImmediate", render_every)
    agent.save("qtable_final.pkl")
    print("\n多阶段训练完成！最终Q表保存为 qtable_final.pkl")

    # 绘制各阶段学习曲线
    plt.figure(figsize=(12, 6))
    # 由于各阶段记录点可能不同，分别绘图
    # 将各阶段记录点的episode编号转换为全局episode编号
    global_points1 = points1
    global_points2 = [p + phase1_episodes for p in points2]
    global_points3 = [p + phase1_episodes + phase2_episodes for p in points3]

    plt.plot(global_points1, avg1, label='Phase1 (No Poison)', marker='o')
    plt.plot(global_points2, avg2, label='Phase2 (Delayed Poison)', marker='s')
    plt.plot(global_points3, avg3, label='Phase3 (Immediate Poison)', marker='^')
    plt.xlabel('Global Episode')
    plt.ylabel('Average Score (last 1000 episodes)')
    plt.title('Multi-Stage Training Progress')
    plt.legend()
    plt.grid(True)
    plt.savefig('multi_stage_curve.png')
    plt.show()

    return agent


def demo(agent_path='qtable_final.pkl', grid_size=20):
    """
    加载训练好的智能体并演示（供main.py调用）
    """
    env = SnakeGame(grid_size=grid_size, cell_size=25, poison_enabled=True, poison_immediate=True)
    agent = QLAgent()
    try:
        agent.load(agent_path)
        print("模型加载成功，开始演示...")
    except Exception as e:
        print(f"模型加载失败：{e}")
        return

    pygame.init()
    screen = pygame.display.set_mode((env.width, env.height))
    pygame.display.set_caption("AI Demonstration - Snake")
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
            state_key = agent._discretize_state(state)  # noqa
            q_values = agent.q_table[state_key]
            action = int(np.argmax(q_values))
            next_state, reward, done = env.step(action)
            state = next_state
            play_time = (current_time - play_start_time) / 1000.0
        else:
            font = pygame.font.Font(None, 36)
            text = font.render(f"Game Over! Score: {env.score}", True, (255, 255, 255))
            screen.blit(text, (env.width // 2 - 100, env.height // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            state = env.reset()
            done = False
            play_start_time = pygame.time.get_ticks()

        env.render(screen)
        font = pygame.font.Font(None, 30)
        score_text = font.render(f"Score: {env.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        time_text = font.render(f"Time: {int(play_time//60):02d}:{int(play_time%60):02d}", True, (255, 255, 255))
        screen.blit(time_text, (10, 40))
        pygame.display.flip()
        clock.tick(10)


if __name__ == "__main__":
    # 开始多阶段训练（总轮数30000）
    final_agent = multi_stage_train(total_episodes=30000, render_every=1000)
    # 训练完成后自动进入演示（可取消注释）
    # demo('qtable_final.pkl')
