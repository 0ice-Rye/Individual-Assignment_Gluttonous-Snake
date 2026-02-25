import numpy as np
import random
from collections import defaultdict

class QLAgent:
    def __init__(self, action_size=4, alpha=0.05, gamma=0.95,
                 epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.998):
        self.action_size = action_size
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table = defaultdict(lambda: np.zeros(action_size))

    def _discretize_state(self, state):
        """将14维连续状态转换为离散键"""
        # 食物方向（8方向）
        dx_food, dy_food = state[4], state[5]
        angle_food = np.arctan2(dy_food, dx_food)
        food_dir = int((angle_food + np.pi) / (2 * np.pi / 8)) % 8

        # 四个方向的距离等级（0-3），编码为一个8位整数
        dist_right = int(state[6])
        dist_left = int(state[7])
        dist_down = int(state[8])
        dist_up = int(state[9])
        danger_code = (dist_up << 6) | (dist_down << 4) | (dist_left << 2) | dist_right

        # 毒药信息
        poison_exists = int(state[10])
        if poison_exists == 1:
            dx_poison, dy_poison = state[11], state[12]
            poison_dist_norm = state[13]
            angle_poison = np.arctan2(dy_poison, dx_poison)
            poison_dir = int((angle_poison + np.pi) / (2 * np.pi / 8)) % 8
            poison_dist_level = int(poison_dist_norm * 3)  # 0-2
        else:
            poison_dir = 8
            poison_dist_level = 3  # 特殊值表示无毒药

        return (food_dir, danger_code, poison_dir, poison_dist_level)

    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        else:
            state_key = self._discretize_state(state)
            q_values = self.q_table[state_key]
            return int(np.argmax(q_values))

    def update(self, state, action, reward, next_state, done):
        state_key = self._discretize_state(state)
        next_state_key = self._discretize_state(next_state)
        current_q = self.q_table[state_key][action]
        if done:
            target = reward
        else:
            next_max_q = np.max(self.q_table[next_state_key])
            target = reward + self.gamma * next_max_q
        self.q_table[state_key][action] += self.alpha * (target - current_q)
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, filepath):
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load(self, filepath):
        import pickle
        with open(filepath, 'rb') as f:
            self.q_table = defaultdict(lambda: np.zeros(self.action_size), pickle.load(f))