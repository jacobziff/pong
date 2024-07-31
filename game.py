import pygame, sys, random

class Paddle:

    WHITE = pygame.Color(255, 255, 255)

    def __init__(self, x, y, width, height, velocity):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity

    def update_screen(self, window):
        pygame.draw.rect(window, self.WHITE, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.velocity
        else:
            self.y += self.velocity

class Ball:

    WHITE = pygame.Color(255, 255, 255)

    def __init__(self, x, y, radius, max_vel):
        self.x = x
        self.y = y
        self.radius = radius
        self.MAX_VEL = max_vel * {True: 1, False: -1} [random.randint(0, 1) == 0] # Random direction after every point
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    def update_screen(self, window):
        # pygame.draw.circle(window, self.WHITE, (self.x, self.y), self.radius)
        pygame.draw.rect(window, self.WHITE, (self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2))

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

class Game:

    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255, 255, 255)

    def __init__(self, speed, width, height, paddle_h, paddle_w, paddle_v, ball_r, max_ball_vel, winning_score):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Pong")

        self.SPEED = speed
        self.WIDTH = width
        self.HEIGHT = height
        self.PADDLE_HEIGHT = paddle_h
        self.PADDLE_WIDTH = paddle_w
        self.PADDLE_V = paddle_v
        self.BALL_R = ball_r
        self.MAX_VEL = max_ball_vel
        self.WINNING_SCORE = winning_score

        self.fps_controller = pygame.time.Clock()
        self.game_window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.font = pygame.font.SysFont(None, self.WIDTH // 12)

        self.left_paddle = Paddle(10, (self.HEIGHT // 2) - (self.PADDLE_HEIGHT // 2), self.PADDLE_WIDTH, self.PADDLE_HEIGHT, self.PADDLE_V)
        self.right_paddle = Paddle(self.WIDTH - 10 - self.PADDLE_WIDTH, (self.HEIGHT // 2) - (self.PADDLE_HEIGHT // 2), self.PADDLE_WIDTH, self.PADDLE_HEIGHT, self.PADDLE_V)
        self.ball = Ball(self.WIDTH // 2, self.HEIGHT // 2, self.BALL_R, max_ball_vel)

        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0

    def reset(self):
        self.__init__(self.SPEED, self.WIDTH, self.HEIGHT, self.PADDLE_HEIGHT, self.PADDLE_WIDTH, self.PADDLE_V, self.BALL_R, self.MAX_VEL, self.WINNING_SCORE)

    def do_collision(self):
        # Check which paddle collided with
        value = 0

        # Floor and ceiling bounces
        if self.ball.y + self.ball.radius >= self.HEIGHT:
            self.ball.y_vel *= -1
        elif self.ball.y - self.ball.radius <= 0:
            self.ball.y_vel *= -1

        # Left paddle check
        if self.ball.x_vel < 0:
            if self.ball.y >= self.left_paddle.y and self.ball.y <= self.left_paddle.y + self.left_paddle.height:
                if self.ball.x - self.ball.radius <= self.left_paddle.x + self.PADDLE_WIDTH:
                    self.ball.x_vel *= -1
                    middle_y = self.left_paddle.y + (self.left_paddle.height / 2)
                    y_diff = middle_y - self.ball.y
                    red_factor = (self.left_paddle.height / 2) / abs(self.ball.MAX_VEL)
                    y_vel = y_diff / red_factor * -1
                    self.ball.y_vel = y_vel
                    value = 1
        else:
            # Right paddle check
            if self.ball.y >= self.right_paddle.y and self.ball.y <= self.right_paddle.y + self.right_paddle.height:
                if self.ball.x + self.ball.radius >= self.right_paddle.x:
                    self.ball.x_vel *= -1
                    middle_y = self.right_paddle.y + (self.right_paddle.height / 2)
                    y_diff = middle_y - self.ball.y
                    red_factor = (self.right_paddle.height / 2) / abs(self.ball.MAX_VEL)
                    y_vel = y_diff / red_factor * -1
                    self.ball.y_vel = y_vel
                    value = 2
        return value

    def update_screen(self):
        self.game_window.fill(self.BLACK)
        
        # Draw paddles
        self.left_paddle.update_screen(self.game_window)
        self.right_paddle.update_screen(self.game_window)
        self.ball.update_screen(self.game_window)

        # Draw scores
        text_surface = self.font.render(str(self.left_score), False, (255, 255, 255))
        self.game_window.blit(text_surface, (self.WIDTH // 4, self.HEIGHT // 40))
        text_surface = self.font.render(str(self.right_score), False, (255, 255, 255))
        self.game_window.blit(text_surface, (3 * self.WIDTH // 4, self.HEIGHT // 40))

        # Draw center line
        counter = -1
        for i in range(10, self.HEIGHT, self.HEIGHT // 20):
            counter += 1
            if counter % 2 == 1:
                continue
            pygame.draw.rect(self.game_window, self.WHITE, (self.WIDTH // 2 - 5, i, 8, self.HEIGHT // 20))

    def play_step(self, action_left=[1, 0, 0], action_right=[1, 0, 0]):

        reward_left = 0
        reward_right = 0
        done = 0

        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        # Paddle movements
        if action_left[1]:
            if self.left_paddle.y - self.left_paddle.velocity >= 0:
                self.left_paddle.move(True)
        if action_left[2]:
            if self.left_paddle.y + self.left_paddle.velocity + self.left_paddle.height <= self.HEIGHT:
                self.left_paddle.move(False)
        if action_right[1]:
            if self.right_paddle.y - self.right_paddle.velocity >= 0:
                self.right_paddle.move(True)
        if action_right[2]:
            if self.right_paddle.y + self.right_paddle.velocity + self.right_paddle.height <= self.HEIGHT:
                self.right_paddle.move(False)

        # Adjust game speed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.SPEED <= 200:
            self.SPEED += 5
        if keys[pygame.K_DOWN] and self.SPEED >= 10:
            self.SPEED -= 5

        # Ball movements
        self.ball.move()
        collision = self.do_collision()
        if collision == 1:
            y_diff = abs(self.left_paddle.y - self.ball.y)
            reward_left = (y_diff / (self.left_paddle.height / 2) * 4) + 3
            self.left_hits += 1
        elif collision == 2:
            y_diff = abs(self.right_paddle.y - self.ball.y)
            reward_right = (y_diff / (self.right_paddle.height / 2) * 4) + 3
            self.right_hits += 1

        # Score updating
        if self.ball.x < 10:
            reward_left = -10
            self.right_score += 1
            self.ball = Ball(self.WIDTH // 2, self.HEIGHT // 2, self.ball.radius, self.MAX_VEL)
            self.ball.x_vel *= -1
            self.left_paddle.y = (self.HEIGHT // 2) - (self.PADDLE_HEIGHT // 2)
            self.right_paddle.y = (self.HEIGHT // 2) - (self.PADDLE_HEIGHT // 2)
        elif self.ball.x > self.WIDTH - 10 - self.PADDLE_WIDTH:
            reward_right = -10
            self.left_score += 1
            self.ball = Ball(self.WIDTH // 2, self.HEIGHT // 2, self.ball.radius, self.MAX_VEL)
            self.left_paddle.y = (self.HEIGHT // 2) - (self.PADDLE_HEIGHT // 2)
            self.right_paddle.y = (self.HEIGHT // 2) - (self.PADDLE_HEIGHT // 2)

        score_left = self.left_score
        score_right = self.right_score

        # Find accuracies of paddles
        left_acc = 0.0
        right_acc = 0.0

        if (self.left_hits + self.right_score) > 0:
            left_acc = (self.left_hits / (self.left_hits + self.right_score))
        left_acc = int(round(left_acc, 2) * 100)

        if (self.right_hits + self.left_score) > 0:
            right_acc = (self.right_hits / (self.right_hits + self.left_score))
        right_acc = int(round(right_acc, 2) * 100)

        # Determine winner
        if self.left_score >= self.WINNING_SCORE:
            done = 1
            reward_right = -20
            self.reset()
        elif self.right_score >= self.WINNING_SCORE:
            done = 1
            reward_left = -20
            self.reset()

        self.update_screen()
        pygame.display.update()

        self.fps_controller.tick(self.SPEED)

        return (reward_left, reward_right, done, score_left, score_right, left_acc, right_acc)