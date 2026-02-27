import pygame
import random
import numpy as np

class SnakeGame:
    def __init__(self, grid_size=20, cell_size=25, poison_enabled=False, poison_immediate=False):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.margin = 50
        self.game_width = grid_size * cell_size
        self.game_height = grid_size * cell_size
        self.width = self.game_width + 2 * self.margin
        self.height = self.game_height + 2 * self.margin
        self.poison_enabled = poison_enabled
        self.poison_immediate = poison_immediate

        self.snake = None
        self.direction = None
        self.food = None
        self.poison = None
        self.score = None
        self.done = None
        self.steps = None
        self.last_action = None
        self.last_reward = None

        # 用于引导奖励的上一步距离
        self.prev_food_dist = None
        self.prev_poison_dist = None

        self.game_start_time = 0
        self.food_generate_time = 0
        self.food_state = 0
        self.food_blink_start = 0
        self.poison_generate_time = 0
        self.poison_state = 0
        self.poison_blink_start = 0

        self.FOOD_LIFETIME = 5000
        self.FOOD_BLINK = 3000
        self.POISON_LIFETIME = 5000
        self.POISON_BLINK = 3000
        self.POISON_START_DELAY = 10000

        self.reset()

    def reset(self):
        mid = self.grid_size // 2
        self.snake = [(mid, mid), (mid-1, mid), (mid-2, mid)]
        self.direction = (1, 0)
        self.score = 0
        self.done = False
        self.steps = 0
        self.last_action = None
        self.last_reward = None

        self.game_start_time = pygame.time.get_ticks()
        self.food = self._place_food()
        self.food_generate_time = self.game_start_time
        self.food_state = 0
        self.food_blink_start = 0

        # 毒药初始化：根据 poison_immediate 决定是否立即放置
        if self.poison_enabled and self.poison_immediate:
            self.poison = self._place_poison()
            self.poison_generate_time = self.game_start_time
        else:
            self.poison = None
        self.poison_generate_time = 0
        self.poison_state = 0
        self.poison_blink_start = 0

        # 初始化距离记录
        head = self.snake[0]
        self.prev_food_dist = abs(head[0] - self.food[0]) + abs(head[1] - self.food[1])
        self.prev_poison_dist = None
        if self.poison is not None:
            self.prev_poison_dist = abs(head[0] - self.poison[0]) + abs(head[1] - self.poison[1])

        return self._get_state()

    def _place_food(self):
        while True:
            pos = (random.randint(0, self.grid_size-1),
                   random.randint(0, self.grid_size-1))
            if pos not in self.snake:
                return pos

    def _place_poison(self):
        while True:
            pos = (random.randint(0, self.grid_size-1),
                   random.randint(0, self.grid_size-1))
            if pos not in self.snake and pos != self.food:
                return pos

    def _get_state(self):
        head = self.snake[0]
        head_norm = (head[0] / self.grid_size, head[1] / self.grid_size)
        food_norm = (self.food[0] / self.grid_size, self.food[1] / self.grid_size)

        dx_food = (self.food[0] - head[0]) / self.grid_size
        dy_food = (self.food[1] - head[1]) / self.grid_size

        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        distances = []
        for d in dirs:
            dist = 0
            nx, ny = head[0] + d[0], head[1] + d[1]
            while 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and (nx, ny) not in self.snake[1:]:
                dist += 1
                nx += d[0]
                ny += d[1]
            distances.append(min(dist, 3))

        if self.poison_enabled and self.poison is not None:
            poison_exists = 1
            dx_poison = (self.poison[0] - head[0]) / self.grid_size
            dy_poison = (self.poison[1] - head[1]) / self.grid_size
            poison_dist = abs(self.poison[0] - head[0]) + abs(self.poison[1] - head[1])
            poison_dist_norm = poison_dist / (2 * self.grid_size)
        else:
            poison_exists = 0
            dx_poison = 0.0
            dy_poison = 0.0
            poison_dist_norm = 0.0

        state = np.array([
            head_norm[0], head_norm[1],
            food_norm[0], food_norm[1],
            dx_food, dy_food,
            distances[0], distances[1], distances[2], distances[3],
            poison_exists, dx_poison, dy_poison, poison_dist_norm
        ], dtype=np.float32)
        return state

    def _handle_item_lifetime(self, current_time):
        if self.food_state == 0:
            if current_time - self.food_generate_time > self.FOOD_LIFETIME:
                self.food_state = 1
                self.food_blink_start = current_time
        else:
            if current_time - self.food_blink_start > self.FOOD_BLINK:
                self.food = self._place_food()
                self.food_generate_time = current_time
                self.food_state = 0

        if self.poison_enabled:
            # 仅在非立即模式下，且毒药为None时，检查延迟生成
            if not self.poison_immediate and self.poison is None and (current_time - self.game_start_time > self.POISON_START_DELAY):
                self.poison = self._place_poison()
                self.poison_generate_time = current_time
                self.poison_state = 0

            if self.poison is not None:
                if self.poison_state == 0:
                    if current_time - self.poison_generate_time > self.POISON_LIFETIME:
                        self.poison_state = 1
                        self.poison_blink_start = current_time
                else:
                    if current_time - self.poison_blink_start > self.POISON_BLINK:
                        self.poison = self._place_poison()
                        self.poison_generate_time = current_time
                        self.poison_state = 0

    def step(self, action):
        action_map = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        new_dir = action_map[action]

        if len(self.snake) > 1 and (new_dir[0] * -1, new_dir[1] * -1) == self.direction:
            new_dir = self.direction

        self.direction = new_dir
        new_head = (self.snake[0][0] + new_dir[0], self.snake[0][1] + new_dir[1])

        old_food_dist = self.prev_food_dist
        old_poison_dist = self.prev_poison_dist

        reward = 0
        self.steps += 1
        current_time = pygame.time.get_ticks()

        self._handle_item_lifetime(current_time)

        ate_food = (new_head == self.food)
        ate_poison = False
        if self.poison_enabled and self.poison is not None and new_head == self.poison:
            ate_poison = True

        collided = False
        if (new_head[0] < 0 or new_head[0] >= self.grid_size or
                new_head[1] < 0 or new_head[1] >= self.grid_size):
            collided = True
        elif new_head in self.snake[1:]:
            collided = True

        if collided:
            self.done = True
            reward = -200
        else:
            self.snake.insert(0, new_head)
            if ate_food:
                self.score += 10
                reward = 50
                self.food = self._place_food()
                self.food_generate_time = current_time
                self.food_state = 0
                self.prev_food_dist = abs(new_head[0] - self.food[0]) + abs(new_head[1] - self.food[1])
            elif ate_poison:
                self.score -= 5
                reward = -50
                self.poison = self._place_poison()
                self.poison_generate_time = current_time
                self.poison_state = 0
                self.prev_poison_dist = abs(new_head[0] - self.poison[0]) + abs(new_head[1] - self.poison[1])
            else:
                self.snake.pop()
                reward = -0.1

                new_food_dist = abs(new_head[0] - self.food[0]) + abs(new_head[1] - self.food[1])
                new_poison_dist = None if self.poison is None else abs(new_head[0] - self.poison[0]) + abs(
                    new_head[1] - self.poison[1])

                guide_reward = 0

                # 接近食物奖励
                if new_food_dist == 1:
                    guide_reward += 0.5
                elif new_food_dist == 2:
                    guide_reward += 0.3

                # 计算两个惩罚值
                penalty = 0
                # 远离食物惩罚
                far_from_food = (new_food_dist > old_food_dist)
                if far_from_food:
                    penalty = -0.3  # 考虑与毒药惩罚比较

                # 靠近毒药惩罚
                poison_penalty = 0
                if self.poison is not None and new_poison_dist is not None:
                    if new_poison_dist <= 1:
                        poison_penalty = -0.5
                    elif new_poison_dist == 2:
                        poison_penalty = -0.3

                # 取最负的惩罚（min因为都是负数）
                worst_penalty = min(penalty, poison_penalty)
                guide_reward += worst_penalty

                reward += guide_reward

                self.prev_food_dist = new_food_dist
                self.prev_poison_dist = new_poison_dist

        self.last_action = action
        self.last_reward = reward
        return self._get_state(), reward, self.done

    def render(self, screen):
        """绘制游戏画面（白色背景，彩色元素）"""
        # 填充白色背景
        screen.fill((255, 255, 255))
        offset = self.margin

        # 绘制游戏区域背景（浅灰色，可选）
        game_rect = pygame.Rect(offset, offset, self.game_width, self.game_height)
        pygame.draw.rect(screen, (240, 240, 240), game_rect)  # 极浅灰背景

        # 绘制网格线（浅灰色）
        grid_color = (200, 200, 200)
        for x in range(0, self.game_width + 1, self.cell_size):
            pygame.draw.line(screen, grid_color, (offset + x, offset),
                             (offset + x, offset + self.game_height))
        for y in range(0, self.game_height + 1, self.cell_size):
            pygame.draw.line(screen, grid_color, (offset, offset + y),
                             (offset + self.game_width, offset + y))

        # 绘制蛇身（深绿色，与白色背景对比）
        for i, segment in enumerate(self.snake):
            if i == 0:
                continue
            color = (0, 150, 0)  # 深绿
            rect = pygame.Rect(offset + segment[0] * self.cell_size,
                               offset + segment[1] * self.cell_size,
                               self.cell_size, self.cell_size)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 80, 0), rect, 2)  # 深绿色边框

        # 绘制蛇头（圆形，亮绿色）
        head = self.snake[0]
        head_center = (offset + head[0] * self.cell_size + self.cell_size // 2,
                       offset + head[1] * self.cell_size + self.cell_size // 2)
        head_radius = self.cell_size // 2 - 2
        pygame.draw.circle(screen, (0, 200, 0), head_center, head_radius)
        pygame.draw.circle(screen, (0, 100, 0), head_center, head_radius, 2)

        # 眼睛位置（根据方向计算）
        eye_offset = head_radius // 2
        eye_radius = 2
        if self.direction == (1, 0):  # 右
            eye1 = (head_center[0] + eye_offset, head_center[1] - eye_offset)
            eye2 = (head_center[0] + eye_offset, head_center[1] + eye_offset)
        elif self.direction == (-1, 0):  # 左
            eye1 = (head_center[0] - eye_offset, head_center[1] - eye_offset)
            eye2 = (head_center[0] - eye_offset, head_center[1] + eye_offset)
        elif self.direction == (0, -1):  # 上
            eye1 = (head_center[0] - eye_offset, head_center[1] - eye_offset)
            eye2 = (head_center[0] + eye_offset, head_center[1] - eye_offset)
        else:  # 下
            eye1 = (head_center[0] - eye_offset, head_center[1] + eye_offset)
            eye2 = (head_center[0] + eye_offset, head_center[1] + eye_offset)

        # 绘制眼睛：根据是否死亡选择画圆或画X
        if self.done:
            # 死亡时画X（黑色）
            x_size = eye_radius * 2
            for eye in (eye1, eye2):
                pygame.draw.line(screen, (0, 0, 0),
                                 (eye[0] - x_size, eye[1] - x_size),
                                 (eye[0] + x_size, eye[1] + x_size), 2)
                pygame.draw.line(screen, (0, 0, 0),
                                 (eye[0] + x_size, eye[1] - x_size),
                                 (eye[0] - x_size, eye[1] + x_size), 2)
        else:
            # 正常时画圆
            pygame.draw.circle(screen, (0, 0, 0), eye1, eye_radius)
            pygame.draw.circle(screen, (0, 0, 0), eye2, eye_radius)

        # 绘制食物（金色菱形，消失时闪烁）
        if self.food is not None:
            food_x = offset + self.food[0] * self.cell_size + self.cell_size // 2
            food_y = offset + self.food[1] * self.cell_size + self.cell_size // 2
            points = [
                (food_x, food_y - self.cell_size // 2 + 2),
                (food_x + self.cell_size // 2 - 2, food_y),
                (food_x, food_y + self.cell_size // 2 - 2),
                (food_x - self.cell_size // 2 + 2, food_y),
            ]
            current_time = pygame.time.get_ticks()
            if self.food_state == 1:  # 闪烁状态
                if (current_time // 200) % 2 == 0:
                    color = (255, 215, 0)  # 金色
                else:
                    color = (255, 165, 0)  # 橙色
            else:
                color = (255, 215, 0)  # 金色
            pygame.draw.polygon(screen, color, points)
            # 高光（小白点）
            pygame.draw.circle(screen, (255, 255, 255), (food_x - 2, food_y - 2), 2)

        # 绘制毒药（圆形，中间有红色高光）
        if self.poison_enabled and self.poison is not None:
            poison_x = offset + self.poison[0] * self.cell_size + self.cell_size // 2
            poison_y = offset + self.poison[1] * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 2 - 2
            current_time = pygame.time.get_ticks()

            # 确定颜色（闪烁效果）
            if self.poison_state == 1:  # 闪烁状态
                if (current_time // 200) % 2 == 0:
                    base_color = (128, 0, 128)  # 紫色
                else:
                    base_color = (255, 255, 255)  # 白色
            else:
                base_color = (128, 0, 128)  # 紫色

            # 绘制圆形
            pygame.draw.circle(screen, base_color, (poison_x, poison_y), radius)

            # 绘制红色高光（中心小圆）
            highlight_radius = max(2, radius // 3)
            highlight_color = (255, 100, 100)  # 亮红色
            pygame.draw.circle(screen, highlight_color, (poison_x, poison_y), highlight_radius)

            # 白色边框
            pygame.draw.circle(screen, (255, 255, 255), (poison_x, poison_y), radius, 1)
