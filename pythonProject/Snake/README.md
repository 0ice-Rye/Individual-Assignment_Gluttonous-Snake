# Individual-Assignment_Gluttonous-Snake
# Gluttonous Snake - Q-learning based Snake AI

This project is a reinforcement learning game that uses the Q-learning algorithm to train a snake AI. The game includes food (gems) and poison elements. The AI needs to learn to eat food and avoid poison. The game interface supports manual control, AI demonstration, dynamic speed, pause, real-time action/reward display, and more.

## Features

- **Game Mechanics**:
  - Food (gem): +10 points, disappears after 5 seconds (blinks for the last 3 seconds) and regenerates.
  - Poison: -5 points, appears 10 seconds after the game starts, disappears after 5 seconds (blinks for the last 3 seconds) and regenerates.
  - Wall or self-collision: -20 points, game over.
  - Step penalty: -0.1 to encourage faster food reaching.
  - Proximity penalty to poison: additional -1.0 when adjacent to poison, guiding the snake away from it.
- **State Space**: 14-dimensional features, including snake head coordinates, food coordinates, relative direction, distance levels in four directions, and poison information.
- **Action Space**: Four discrete actions: up, down, left, right.
- **Q-learning**:
  - Uses a Q-table to store state-action values, with states discretized into (food direction, danger code, poison direction, poison distance level).
  - Hyperparameters: α=0.05, γ=0.95, ε decays from 1.0 to 0.01 with decay rate 0.998.
  - Trained for 10,000 episodes, average score recorded every 1,000 episodes.
- **User Interface**:
  - Main menu to select manual mode or AI demo mode.
  - Manual mode: Control the snake with arrow keys; real-time display of score, time, speed, action, and reward.
  - Speed dynamically changes based on score: speed 3 (<20), 4 (≥20), 5 (≥50), 6 (≥90).
  - Pause/resume supported in manual mode.
  - AI demo mode: Loads trained Q-table and plays automatically.
  - Game over popup with "Play Again" and "Exit" buttons.

## Installation

Make sure you have Python 3.8+ installed, then install the required libraries using pip:

```bash
pip install -r requirements.txt
```

## File Structure
```
Snake/
├── game_env.py          # Game environment class
├── ql_agent.py      # Q-learning agent
├── train.py         # Training script
├── main.py          # Main program (menu + manual/AI mode)
├── menu.py          # Main menu interface
├── button.py        # Button class
├── requirements.txt # Dependency list
├── README.md        # Project documentation
└── training_curve.png # Training curve (generated after running train.py)
```

## Usage
1. Train the AI Model
Run the following command to start training (default: 10,000 episodes, render every 1,000 episodes):
python train.py

  - During training, the average score of the last 1,000 episodes is printed every 1,000 episodes. After training, a learning curve training_curve.png is generated, and the Q-table is saved as qtable.pkl.

2. Run the Game
After training, start the main program:

```bash
python main.py
```

  - Select Start Game: Control the snake with arrow keys and experience the game.
  - Select AI Demo: Load the trained qtable.pkl and watch the AI play automatically.
  - Select Exit: Quit the program.

## Customization
Training parameters: Adjust episodes, render_every, etc., in train.py.
Game rules: Modify reward values, poison appearance time, speed thresholds, etc., in game.py.
UI layout: Adjust text positions, button coordinates, etc., in main.py.

## Example Training Result
After 10,000 episodes of training, the AI's average score gradually improves, eventually stabilizing at a certain level. The figure below shows the training curve:
https://training_curve.png

## Notes
  - Training can be time-consuming; set render_every=0 to disable rendering and speed up training.
  - If AI demo cannot find qtable.pkl, please run train.py first to generate the model file.
  - This project uses a discretized Q-table, so performance is limited by the discretization granularity. For higher performance, consider using DQN.

## License
This project is for educational purposes only. Licensed under the MIT License.


# Gluttonous Snake - 基于 Q-learning 的贪吃蛇 AI

本项目是一个使用 Q-learning 算法训练贪吃蛇 AI 的强化学习游戏。游戏包含食物（宝石）和毒药两种元素，通过多阶段学习，AI 学会在躲避毒药的同时尽可能多地吃到宝石。界面支持手动控制、AI 演示、动态速度调整、暂停、实时动作/奖励显示等功能。

## 功能特点

### **游戏机制**：
- 食物（宝石）：+10 分，内部奖励 +50。5 秒后闪烁 3 秒，然后重新生成。
- 毒药：-5 分，内部奖励 -50。游戏开始 10 秒后出现（可配置），5 秒后闪烁 3 秒，然后重新生成。
- 撞墙/撞身：内部奖励 -200，游戏结束。
- 每步惩罚：-0.1，鼓励尽快吃到食物。
- 引导奖励（加速学习）：
   - 接近食物：距离 1 格 +0.5，距离 2 格 +0.3。
   - 远离食物：-0.3。
   - 接近毒药：距离 ≤1 格 -0.5，距离 =2 格 -0.3。
   - 当多个惩罚同时触发时，只取最负的一个（不叠加）。
### **AI学习**：
- **状态空间**：14 维特征，包括：
   - 蛇头归一化坐标
   - 食物归一化坐标及相对方向
   - 四个方向的距离等级（0～3）
   - 毒药存在标志、相对方向、归一化距离
- **动作空间**：上、下、左、右四个离散动作。
- **Q-learning**：
   - Q 表离散化：(食物方向, 危险编码, 毒药方向, 毒药距离等级)
   - 食物方向：8 种
   - 危险编码：四个方向距离等级编码为 8 位整数（256 种）
   - 毒药方向：8 种 + 1 种“无毒药”
   - 毒药距离等级：4 级（0～2 对应距离，3 表示无毒药）
   - 总状态数 ≈ 73,728，Q 表可管理。
   - 超参数：α = 0.05，γ = 0.95，ε 从 1.0 衰减至 0.01，衰减率 0.999。
- **多阶段训练**：
 1. 无毒药阶段：学习基础寻路和避障（总轮数 40%）。
 2. 毒药延迟阶段：毒药延迟 10 秒出现，适应毒药存在（30%）。
 3. 毒药立即阶段：毒药全程存在，强化躲避能力（30%）。

- 总训练轮数 30,000，每 1000 轮记录平均得分。
- 每阶段结束后保存 Q 表（qtable_phase1.pkl、qtable_phase2.pkl、qtable_final.pkl）。

### **用户界面**：
- **主菜单**：选择**手动模式**或**AI 演示模式**。
- **手动模式**：
  - 方向键控制。
  - 实时显示：得分、游戏时间、当前速度（帧率）、上一步动作及奖励。
  - 速度随得分动态变化：
   - <20：3 fps
   - ≥20：4 fps
   - ≥40：5 fps
   - ≥70：6 fps
   - ≥90：7 fps
   - ≥120：8 fps
   - ≥150：9 fps
   - ≥180：10 fps
  - 暂停/继续（右上角按钮）。
  - 游戏结束浮层，可选择重玩或退出。
- **AI 演示模式**：
  - 加载训练好的 Q 表（qtable_final.pkl），自动游戏。
  - 界面信息与手动模式相同。
  - 右上角“Exit”按钮返回主菜单。
- **视觉风格**：
  - 白色背景，黑色文字，游戏网格为浅灰色。
  - 蛇：深绿色身体，圆头带方向眼睛（存活时黑眼，死亡时画 X）。
  - 食物：金色菱形（消失前闪烁）。
  - 毒药：紫色圆形，中心红色高光（消失前闪烁）。

## 安装依赖
确保已安装 Python 3.8+，然后使用 pip 安装所需库：
```bash
pip install -r requirements.txt
```

## 文件结构
```
Snake/
├── button.py            # 简单按钮类
├── game_env.py          # 游戏环境类
├── main.py              # 主程序（菜单 + 手动/AI 模式）
├── menu.py              # 主菜单界面
├── ql_agent.py          # Q-learning 智能体
├── train.py             # 多阶段训练脚本
├── test.py              # 测试脚本
├── requirements.txt     # 依赖列表
├── README.md            # 项目说明
├── multi_stage_curve.png # 训练曲线（运行 train.py 后生成）
├── qtable_phase1.pkl    # 阶段1 Q 表（生成）
├── qtable_phase2.pkl    # 阶段2 Q 表（生成）
└── qtable_final.pkl     # 最终 Q 表（生成）
```

## 使用方法
1. 训练AI模型
运行训练脚本，默认进行 30,000 轮 三阶段训练，每 1,000 轮渲染一次：
```bash
python train.py
```
  - 训练过程中每 1,000 轮输出最近 1,000 轮的平均得分。
  - 训练结束后生成合并学习曲线 multi_stage_curve.png，最终 Q 表保存为 qtable_final.pkl。
  - 如需加速训练，可将 train.py 中的 render_every 设为 0 以关闭渲染。

2. 运行游戏
训练完成后，启动主程序：
```bash
python main.py
```
通过菜单选择模式：
  - 开始游戏 – 使用键盘方向键控制蛇，体验游戏。。
  - AI 演示 – 观看训练好的 AI 自动游戏。
  - 退出 – 退出程序。

## 自定义配置
| 文件 | 参数 | 说明 |
| :------: | :------: | :------: |
| game_env.py |  grid_size, cell_size  | 修改棋盘大小 |
| game_env.py |  POISON_START_DELAY  | 毒药出现延迟（毫秒） |
| game_env.py |  FOOD_LIFETIME, POISON_LIFETIME  | 物品存在时间（毫秒） |
| game_env.py |  step() 中的奖励值  | 修改内部奖励 |
| main.py |  get_speed_from_score()  | 调整速度阈值 |
| train.py |  total_episodes  | 修改总训练轮数 |
| train.py |  各阶段训练轮次比例  | 调整阶段长度 |
| ql_agent.py |  alpha, gamma, epsilon_decay  | 调整学习超参数 |

## 训练结果示例
经过 30,000 轮训练，AI 的平均得分（最近 1,000 轮）通常会有明显提升。下图展示了三阶段的训练曲线：
https://multi_stage_curve.png

## 注意事项
  - 训练耗时可能较长，可以设置render_every=0关闭渲染以加速训练。
  - AI 演示需要训练好的 Q 表文件 qtable_final.pkl，如果文件缺失，请先运行 train.py 进行训练。
  - 本项目采用离散化 Q 表，性能受限于离散化粒度。如需更复杂的行为，可考虑升级为 DQN。
  - 手动模式中按“Pause”可暂停游戏，中央的“Play”按钮会在 3 秒倒计时后继续游戏。

