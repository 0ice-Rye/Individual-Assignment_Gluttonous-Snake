# Individual-Assignment_Gluttonous-Snake
# Gluttonous Snake - Q-learning Based Snake AI

This project is a reinforcement learning game that trains a Snake AI using the Q-learning algorithm. The game includes two elements: food (gems) and poison. Through multi-stage learning, the AI learns to avoid poison while collecting as many gems as possible. The interface supports manual control, AI demo, dynamic speed adjustment, pause, and real-time action/reward display.

## Features

### **Game Mechanics**：
- Food (Gem): +10 score, internal reward +50. Blinks for 3 seconds after 5 seconds, then respawns.
- Poison: -5 score, internal reward -50. Appears 10 seconds after game start (configurable), blinks for 3 seconds after 5 seconds, then respawns.
- Wall collision / self-collision: internal reward -200, game over.
- Step penalty: -0.1 to encourage faster food collection.
- Guidance reward (to accelerate learning):
   - Approaching food: +0.5 for distance 1 cell, +0.3 for distance 2 cells.
   - Moving away from food: -0.3.
   - Approaching poison: -0.5 for distance ≤1 cell, -0.3 for distance = 2 cells.
   - When multiple penalties are triggered simultaneously, only the most negative one is applied (no stacking).
### **AI Learning**：
- **State Space**: 14-dimensional features, including:
   - Normalized coordinates of snake head
   - Normalized coordinates and relative direction of food
   - Distance levels (0–3) in four directions
   - Poison existence flag, relative direction, normalized distance
- **Action Space**: Four discrete actions: up, down, left, right.
- **Q-learning**：
   - Q-table discretization: (food direction, danger encoding, poison direction, poison distance level)
   - Food direction: 8 types
   - Danger encoding: distance levels in four directions encoded as 8-bit integer (256 types)
   - Poison direction: 8 types + 1 type "no poison"
   - Poison distance level: 4 levels (0–2 for distance, 3 for no poison)
   - Total state count ≈ 73,728, manageable Q-table.
   - Hyperparameters: α = 0.05, γ = 0.95, ε decays from 1.0 to 0.01, decay rate 0.999.
- **Multi-stage Training**：
 1. No-poison stage: learn basic pathfinding and obstacle avoidance (40% of total episodes).
 2. Poison-delay stage: poison appears after 10s delay, adapt to poison presence (30%).
 3. Poison-immediate stage: poison exists throughout, enhance avoidance ability (30%).

   - Total training episodes: 30,000, average score recorded every 1000 episodes.
   - Save Q-table after each stage (qtable_phase1.pkl, qtable_phase2.pkl, qtable_final.pkl).

### **User Interface**：
- **Main Menu**：Select**Manual Mode** or **AI AI Demo Mode**.
- **Manual Mode**：
  - Control with arrow keys.
  - Real-time display: score, game time, current speed (FPS), last action and reward.
  - Speed changes dynamically with score:
    - <20：3 fps
    - ≥20：4 fps
    - ≥40：5 fps
    - ≥70：6 fps
    - ≥90：7 fps
    - ≥120：8 fps
    - ≥150：9 fps
    - ≥180：10 fps
  - Pause / resume (button in top-right corner).
  - Game-over overlay with replay or exit options.
- **AI Demo Mode**：
  - Load pre-trained Q-table (qtable_final.pkl) and play automatically.
  - Same interface information as manual mode.
  - "Exit" button in top-right corner returns to main menu.
- **Visual Style**：
  - White background, black text, light gray game grid.
  - Snake: dark green body, round head with directional eyes (black when alive, X when dead).
  - Food: golden diamond (blinks before disappearing).
  - Poison: purple circle with red highlight in center (blinks before disappearing).

## Install Dependencies
Make sure Python 3.8+ is installed, then install required libraries using pip:
```bash
pip install -r requirements.txt
```

## 文件结构
```
Snake/
├── button.py            # Simple button class
├── game_env.py          # Game environment class
├── main.py              # Main program (menu + manual/AI mode)
├── menu.py              # Main menu interface
├── ql_agent.py          # Q-learning agent
├── train.py             # Multi-stage training script
├── test.py              # Test script
├── requirements.txt     # Dependency list
├── README.md            # Project documentation
├── multi_stage_curve.png # Training curve (generated after running train.py)
├── qtable_phase1.pkl    # Stage 1 Q-table (generated)
├── qtable_phase2.pkl    # Stage 2 Q-table (generated)
└── qtable_final.pkl     # Final Q-table (generated)
```

## Usage
1. Train AI Model
Run the training script. By default, it performs 30,000 episodes of three-stage training, rendered every 1,000 episodes:
```bash
python train.py
```
  - Average score of the last 1,000 episodes is printed every 1,000 episodes during training.
  - After training, a combined learning curve multi_stage_curve.png is generated, and the final Q-table is saved as qtable_final.pkl.
  - To speed up training, set render_every in train.py to 0 to disable rendering.

2. Run the Game
After training, start the main program:
```bash
python main.py
```
Select mode via menu:
  - Start Game – Control the snake with keyboard arrow keys.
  - AI Demo – Watch the trained AI play automatically.
  - Exit – Quit the program.

## Custom Configuration
| File | Parameter | Description |
| :------: | :------: | :------: |
| game_env.py |  grid_size, cell_size  | Change board size |
| game_env.py |  POISON_START_DELAY  | Poison appearance delay (ms) |
| game_env.py |  FOOD_LIFETIME, POISON_LIFETIME  | Item lifetime (ms) |
| game_env.py |  Reward values in step()  | Modify internal rewards励 |
| main.py |  get_speed_from_score()  | Adjust speed thresholds |
| train.py |  total_episodes  | Change total training episodes |
| train.py |  Episode ratio of each stage  | Adjust stage length |
| ql_agent.py |  alpha, gamma, epsilon_decay  | Adjust learning hyperparameters |

## Training Result Example
After 30,000 training episodes, the AI's average score (over the last 1,000 episodes) usually improves significantly. The figure below shows the three-stage training curve:
https://multi_stage_curve.png

## Notes
  - Training may take a long time. Set render_every=0 to disable rendering for faster training.
  - AI demo requires the pre-trained Q-table file qtable_final.pkl. If missing, run train.py first.
  - This project uses a discretized Q-table; performance is limited by discretization granularity. For more complex behaviors, consider upgrading to DQN.
  - Press "Pause" in manual mode to pause the game. The central "Play" button resumes after a 3-second countdown.


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

