import pygame
import random
import numpy as np

class SnakeGame:
    def __init__(self, grid_size=20, cell_size=25, poison_enabled=False):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.margin = 30
        self.game_width = grid_size * cell_size
        self.game_height = grid_size * cell_size
        self.width = self.game_width + 2 * self.margin
        self.height = self.game_height + 2 * self.margin
        self.poison_enabled = poison_enabled

        self.snake = None
        self.direction = None
        self.food = None
        self.poison = None
        self.score = None
        self.done = None
        self.steps = None
        self.last_action = None
        self.last_reward = None

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

        self.poison = None
        self.poison_generate_time = 0
        self.poison_state = 0
        self.poison_blink_start = 0

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
            if self.poison is None and (current_time - self.game_start_time > self.POISON_START_DELAY):
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
            reward = -20
        else:
            self.snake.insert(0, new_head)
            if ate_food:
                self.score += 10
                reward = 10
                self.food = self._place_food()
                self.food_generate_time = current_time
                self.food_state = 0
            elif ate_poison:
                self.score -= 5
                reward = -8
                self.poison = self._place_poison()
                self.poison_generate_time = current_time
                self.poison_state = 0
            else:
                self.snake.pop()
                reward = -0.1
                # 毒药接近惩罚：仅在相邻格（距离≤1）时惩罚，避免蛇过度恐慌
                if self.poison_enabled and self.poison is not None:
                    poison_dist = abs(self.poison[0] - new_head[0]) + abs(self.poison[1] - new_head[1])
                    if poison_dist <= 1:
                        reward -= 1.0  # 相邻格惩罚
                    # 如果希望奖励远离，可在此处添加 elif poison_dist >= 5: reward += 0.1 等逻辑

        self.last_action = action
        self.last_reward = reward
        return self._get_state(), reward, self.done

    def render(self, screen):
        """绘制游戏画面（只绘制游戏区域）"""
        screen.fill((0, 0, 0))
        offset = self.margin

        game_rect = pygame.Rect(offset, offset, self.game_width, self.game_height)
        pygame.draw.rect(screen, (10, 10, 10), game_rect)

        for x in range(0, self.game_width + 1, self.cell_size):
            pygame.draw.line(screen, (40, 40, 40), (offset + x, offset),
                             (offset + x, offset + self.game_height))
        for y in range(0, self.game_height + 1, self.cell_size):
            pygame.draw.line(screen, (40, 40, 40), (offset, offset + y),
                             (offset + self.game_width, offset + y))

        for i, segment in enumerate(self.snake):
            if i == 0:
                continue
            color = (0, 200, 0)
            rect = pygame.Rect(offset + segment[0] * self.cell_size,
                               offset + segment[1] * self.cell_size,
                               self.cell_size, self.cell_size)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 100, 0), rect, 2)

        head = self.snake[0]
        head_center = (offset + head[0] * self.cell_size + self.cell_size // 2,
                       offset + head[1] * self.cell_size + self.cell_size // 2)
        head_radius = self.cell_size // 2 - 2
        pygame.draw.circle(screen, (0, 255, 0), head_center, head_radius)
        pygame.draw.circle(screen, (0, 150, 0), head_center, head_radius, 2)
        eye_offset = head_radius // 2
        eye_radius = 2
        if self.direction == (1, 0):
            eye1 = (head_center[0] + eye_offset, head_center[1] - eye_offset)
            eye2 = (head_center[0] + eye_offset, head_center[1] + eye_offset)
        elif self.direction == (-1, 0):
            eye1 = (head_center[0] - eye_offset, head_center[1] - eye_offset)
            eye2 = (head_center[0] - eye_offset, head_center[1] + eye_offset)
        elif self.direction == (0, -1):
            eye1 = (head_center[0] - eye_offset, head_center[1] - eye_offset)
            eye2 = (head_center[0] + eye_offset, head_center[1] - eye_offset)
        else:
            eye1 = (head_center[0] - eye_offset, head_center[1] + eye_offset)
            eye2 = (head_center[0] + eye_offset, head_center[1] + eye_offset)
        pygame.draw.circle(screen, (255, 255, 255), eye1, eye_radius)
        pygame.draw.circle(screen, (255, 255, 255), eye2, eye_radius)

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
            if self.food_state == 1:
                if (current_time // 200) % 2 == 0:
                    color = (255, 200, 0)
                else:
                    color = (255, 100, 0)
            else:
                color = (255, 215, 0)
            pygame.draw.polygon(screen, color, points)
            pygame.draw.circle(screen, (255, 255, 255), (food_x - 2, food_y - 2), 2)

        if self.poison_enabled and self.poison is not None:
            poison_x = offset + self.poison[0] * self.cell_size + self.cell_size // 2
            poison_y = offset + self.poison[1] * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 2 - 2
            current_time = pygame.time.get_ticks()
            if self.poison_state == 1:
                if (current_time // 200) % 2 == 0:
                    base_color = (128, 0, 128)
                else:
                    base_color = (255, 0, 255)
            else:
                base_color = (128, 0, 128)
            pygame.draw.circle(screen, base_color, (poison_x, poison_y), radius)
            pygame.draw.circle(screen, (255, 255, 255), (poison_x, poison_y), radius, 2)
            offset_cross = radius // 2
            pygame.draw.line(screen, (255, 255, 255),
                             (poison_x - offset_cross, poison_y - offset_cross),
                             (poison_x + offset_cross, poison_y + offset_cross), 2)
            pygame.draw.line(screen, (255, 255, 255),
                             (poison_x + offset_cross, poison_y - offset_cross),
                             (poison_x - offset_cross, poison_y + offset_cross), 2)