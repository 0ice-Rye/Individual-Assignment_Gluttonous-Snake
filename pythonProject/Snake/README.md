# Individual-Assignment_Gluttonous-Snake
Q-learning Gluttonous Snake
# Snake RL - Q-learning based Snake AI

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
```Snake/
├── game.py          # Game environment class
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

During training, the average score of the last 1,000 episodes is printed every 1,000 episodes. After training, a learning curve training_curve.png is generated, and the Q-table is saved as qtable.pkl.

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
Training can be time-consuming; set render_every=0 to disable rendering and speed up training.
If AI demo cannot find qtable.pkl, please run train.py first to generate the model file.
This project uses a discretized Q-table, so performance is limited by the discretization granularity. For higher performance, consider using DQN.

## License
This project is for educational purposes only. Licensed under the MIT License.


# Snake RL - 基于 Q-learning 的贪吃蛇 AI

本项目是一个使用 Q-learning 算法训练贪吃蛇 AI 的强化学习游戏。游戏包含食物（宝石）和毒药两种元素，AI 需要学会吃到食物并避开毒药。游戏界面支持手动控制、AI 演示、动态速度、暂停、实时动作/奖励显示等功能。

## 功能特点

- **游戏机制**：
  - 食物（宝石）：+10 分，5秒后闪烁3秒后消失并重新生成。
  - 毒药：-5 分，游戏开始10秒后出现，5秒后闪烁3秒后消失并重新生成。
  - 撞墙或撞身：-20 分，游戏结束。
  - 每步惩罚：-0.1，鼓励快速找到食物。
  - 毒药接近惩罚：与毒药相邻时额外 -1.0，引导远离毒药。
- **状态空间**：14维特征，包含蛇头坐标、食物坐标、相对方向、四个方向的距离等级、毒药信息。
- **动作空间**：上、下、左、右四个离散动作。
- **Q-learning**：
  - 使用 Q-table 存储状态-动作值，状态经离散化（食物方向、危险编码、毒药方向、毒药距离等级）。
  - 超参数：α=0.05, γ=0.95, ε 从 1.0 衰减至 0.01，衰减率 0.998。
  - 训练 10000 轮，每 1000 轮记录平均得分。
- **用户界面**：
  - 主菜单选择手动模式或 AI 演示模式。
  - 手动模式：键盘方向键控制，实时显示得分、时间、速度、动作、奖励。
  - 速度随得分动态变化：得分<20 速度3，≥20 速度4，≥50 速度5，≥90 速度6。
  - 支持暂停/继续（手动模式）。
  - AI 演示模式：加载训练好的 Q-table，自动游戏。
  - 游戏结束弹窗，可选择重玩或退出。

## 安装依赖
确保已安装 Python 3.8+，然后使用 pip 安装所需库：
```bash
pip install -r requirements.txt
```

## 文件结构
```Snake_RL/
├── game.py          # 游戏环境类
├── ql_agent.py      # Q-learning智能体
├── train.py         # 训练脚本
├── main.py          # 主程序（菜单+手动/AI模式）
├── menu.py          # 主菜单界面
├── button.py        # 按钮类
├── requirements.txt # 依赖列表
├── README.md        # 项目说明
└── training_curve.png # 训练曲线（运行train.py后生成）
```

## 使用方法
1. 训练AI模型
运行以下命令开始训练（默认10000轮，每1000轮渲染一次）：
```bash
python train.py
```
训练过程中每1000轮输出一次最近1000轮的平均得分，训练结束后生成学习曲线training_curve.png，并保存Q表为qtable.pkl。

2. 运行游戏
训练完成后，启动主程序：
```bash
python main.py
```
  - 选择 开始游戏 ：使用键盘方向键控制蛇，体验游戏。
  - 选择 AI训练演示：加载训练好的qtable.pkl，观看AI自动游戏。
  - 选择 退出：退出程序。

## 自定义
  - 训练参数：在train.py中调整episodes、render_every等。
  - 游戏规则：在game.py中调整奖励值、毒药出现时间、速度阈值等。
  - UI布局：在main.py中调整文字位置、按钮坐标等。

## 训练结果示例
经过10000轮训练，AI的平均得分逐渐提升，最终能稳定获得一定分数。下图展示了训练曲线：
https://training_curve.png

## 注意事项
  -训练耗时可能较长，建议设置render_every=0关闭渲染以加速训练。
  -若AI演示时找不到qtable.pkl，请先运行train.py生成模型文件。
  -本项目的Q-table采用离散化方法，状态空间有限，因此性能受限于离散化粒度。如需更高性能，可尝试DQN。

