import torch
import random
import numpy as np
from collections import deque
from game import Game
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100000
BATCH_SIZE = 1000

class Agent:

    def __init__(self, g=0.9, lr=0.001):
        self.num_games = 0
        self.epsilon = 0
        self.gamma = g
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(10, 256, 3)
        self.trainer = QTrainer(self.model, lr=lr, gamma=self.gamma)

    def get_state(self, game : Game, isLeft):

        # Determine paddles
        if isLeft:
            paddle = game.left_paddle
            opposing_paddle = game.right_paddle
        else:
            paddle = game.right_paddle
            opposing_paddle = game.left_paddle
        
        # Location of ball
        ball_above_full = game.ball.y < paddle.y
        ball_below_full = game.ball.y > paddle.y + paddle.height

        ball_above_center = game.ball.y < (paddle.y - (paddle.height // 2))
        ball_below_center = game.ball.y > (paddle.y + (paddle.height // 2))

        ball_in_left = game.ball.x < (game.WIDTH / 2)
        ball_in_right = not ball_in_left

        # Direction of ball
        ball_x_vel_pos = game.ball.x_vel > 0
        ball_y_vel_pos = game.ball.y_vel > 0

        # Location of opposing paddle
        opposing_above = opposing_paddle.y > paddle.y
        opposing_below = not opposing_above

        return np.array([ball_above_full, ball_below_full, ball_above_center, ball_below_center, ball_in_left, ball_in_right, ball_x_vel_pos, ball_y_vel_pos, opposing_above, opposing_below], dtype=int)

    def remember(self, old_state, final_move, reward, new_state, done):
        self.memory.append((old_state, final_move, reward, new_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        
        states = []
        actions = []
        rewards = []
        next_states = []
        dones = []
        for s, a, r, n, d in mini_sample:
            states.append(s)
            actions.append(a)
            rewards.append(r)
            next_states.append(n)
            dones.append(d)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, old_state, final_move, reward, new_state, done):
        self.trainer.train_step(old_state, final_move, reward, new_state, done)

    def get_action(self, state):
        self.epsilon = 30 - self.num_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

# Game info 
WIDTH = 800
HEIGHT = 600
SPEED = 40
PADDLE_HEIGHT = WIDTH // 8
PADDLE_WIDTH = HEIGHT // 30
PADDLE_V = HEIGHT // 75
BALL_RADIUS = WIDTH // 80
MAX_BALL_VEL = WIDTH // 80
WINNING_SCORE = 7

def train():
    accuracies_left = []
    accuracies_right = []
    agent_left = Agent(0.9, 0.001)
    agent_right = Agent(0.9, 0.001)
    game_num = 0
    game = Game(SPEED, WIDTH, HEIGHT, PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_V, BALL_RADIUS, MAX_BALL_VEL, WINNING_SCORE)
    while True:
        old_state_left = agent_left.get_state(game, True)
        old_state_right = agent_right.get_state(game, False)

        final_move_left = agent_left.get_action(old_state_left)
        final_move_right = agent_right.get_action(old_state_right)

        reward_left, reward_right, done, score_left, score_right, left_acc, right_acc = game.play_step(final_move_left, final_move_right)
        new_state_left = agent_left.get_state(game, True)
        new_state_right = agent_right.get_state(game, False)

        agent_left.train_short_memory(old_state_left, final_move_left, reward_left, new_state_left, done)
        agent_right.train_short_memory(old_state_right, final_move_right, reward_right, new_state_right, done)

        agent_left.remember(old_state_left, final_move_left, reward_left, new_state_left, done)
        agent_right.remember(old_state_right, final_move_right, reward_right, new_state_right, done)

        if done:

            # Print game info
            game_num += 1
            if score_left > score_right:
                print('Game #' + str(game_num) + ' |', 'Left wins :', score_left, '-', score_right, '| Accuracy:', str(left_acc) + '%', '-', str(right_acc) + '%')
            elif score_right > score_left:
                print('Game #' + str(game_num) + ' |', 'Right wins:', score_left, '-', score_right, '| Accuracy:', str(left_acc) + '%', '-', str(right_acc) + '%')

            agent_left.num_games += 1
            agent_right.num_games += 1
            agent_left.train_long_memory()
            agent_right.train_long_memory()
            
            accuracies_left.append(left_acc)
            accuracies_right.append(right_acc)
            game.reset()

if __name__ == '__main__':
    train()