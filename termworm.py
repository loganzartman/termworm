from pytermfx import Terminal, Color, Style
from pytermfx.tools import Screensaver, draw_hline
from random import randint, choice
import time

t = Terminal()

K_UP = "up"
K_DOWN = "down"
K_RIGHT = "right"
K_LEFT = "left"

game_x = 0
game_y = 3
game_w = 0
game_h = 0

def resize():
    global t, game_x, game_y, game_w, game_h
    game_w = int(t.w / 2 - game_x)
    game_h = t.h - game_y
t.add_resize_handler(resize)

class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.length = 36
        self.old = []

    def update(self):
        self.old += [(self.x, self.y)]
        if len(self.old) > self.length:
            old = self.old.pop(0)
            t.cursor_to(old[0] * 2 + game_x, old[1] + game_y)
            t.write("  ")

        self.x += self.vx
        self.y += self.vy
        self.wrap()
        t.cursor_to(snake.x * 2 + game_x, snake.y + game_y)
        t.style(Color.hsl(time.clock() * 5, 1.0, 0.7))
        t.write("██")
        t.flush()

    def intersecting(self, x, y):
        return any(x == pos[0] and y == pos[1] for pos in self.old)

    def wrap(self):
        if self.x < 0:
            self.x = game_w - 1
        if self.y < 0:
            self.y = game_h - 1
        if self.x >= game_w:
            self.x = 0
        if self.y >= game_h:
            self.y = 0

snake = Snake(int(game_w/2), int(game_h/2))
input_q = []
score = 24
hiscore = 0
food_x = snake.x
food_y = snake.y

def update():
    global food_x, food_y, score, hiscore, app
    app.framerate = int(min(20, score / 5) + 10)
    process_input()
    snake.update()
    if snake.x == food_x and snake.y == food_y:
        move_food()
        snake.length += 1
        score += 1
        hiscore = max(hiscore, score)
        draw_ui()

def draw_ui():
    global t, score, hiscore
    t.cursor_to(0, 0)
    t.style(Color.hex(0xFFFFFF)).writeln("~TermWorm~")
    t.style(Color.hex(0x777777)).writeln("▞ Score: ", score).flush()
    t.style(Color.hex(0x777777))
    draw_hline(t, 2)
t.add_resize_handler(draw_ui)

def move_food():
    global t, food_x, food_y, snake
    positions = [(x,y) for x in range(game_w) for y in range(game_h)
        if not snake.intersecting(x, y)]
    food_x, food_y = choice(positions)
    t.cursor_to(food_x * 2 + game_x, food_y + game_y)
    t.write("▞▞")
    t.flush()
t.add_resize_handler(move_food)

def process_input():
    global input_q
    for i, c in enumerate(input_q):
        if c == K_LEFT:
            if not snake.intersecting(snake.x-1, snake.y):
                snake.vx = -1
                snake.vy = 0
                input_q = input_q[i+1:]
        elif c == K_RIGHT:
            if not snake.intersecting(snake.x+1, snake.y):
                snake.vx = 1
                snake.vy = 0
                input_q = input_q[i+1:]
        elif c == K_UP:
            if not snake.intersecting(snake.x, snake.y-1):
                snake.vx = 0
                snake.vy = -1
                input_q = input_q[i+1:]
        elif c == K_DOWN:
            if not snake.intersecting(snake.x, snake.y+1):
                snake.vx = 0
                snake.vy = 1
                input_q = input_q[i+1:]

def on_input(c):
    global input_q
    input_q.append(c)

app = Screensaver(t, 10, update = update, on_input = on_input)
app.start()
