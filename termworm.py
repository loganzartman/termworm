from pytermfx import Terminal, Color, Style
from pytermfx.tools import Screensaver
from random import randint, choice
import time

K_UP = "up"
K_DOWN = "down"
K_RIGHT = "right"
K_LEFT = "left"

t = Terminal()
w = int(t.w / 2)
h = t.h
def resize():
    global w,h
    w = int(t.w / 2)
    h = t.h
resize()
t.add_resize_handler(resize)

class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.length = 12
        self.old = []

    def update(self):
        self.old += [(self.x, self.y)]
        if len(self.old) > self.length:
            old = self.old.pop(0)
            t.cursor_to(old[0] * 2, old[1])
            t.write("  ")

        self.x += self.vx
        self.y += self.vy
        self.wrap()
        t.cursor_to(snake.x * 2, snake.y)
        t.style(Color.hsl(time.clock() * 5, 1.0, 0.7))
        t.write("██")
        t.flush()

    def intersecting(self, x, y):
        return any(x == pos[0] and y == pos[1] for pos in self.old)

    def wrap(self):
        if self.x < 0:
            self.x = w-1
        if self.y < 0:
            self.y = h-1
        if self.x >= w:
            self.x = 0
        if self.y >= h:
            self.y = 0

input_q = []
score = 0
snake = Snake(int(w/2), int(h/2))
food_x = snake.x
food_y = snake.y
def update():
    global food_x, food_y, score, app
    app.framerate = int(min(20, score / 5) + 10)
    process_input()
    snake.update()
    if snake.x == food_x and snake.y == food_y:
        move_food()
        snake.length += 1
        score += 1

def move_food():
    global food_x, food_y, snake
    positions = [(x,y) for x in range(w) for y in range(h)
        if not snake.intersecting(x, y)]
    food_x, food_y = choice(positions)
    t.cursor_to(food_x * 2, food_y)
    t.write("▞▞")
    t.flush()

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
