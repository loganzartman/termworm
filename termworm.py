from pytermfx import Terminal, Color, Style
from pytermfx.tools import Screensaver
import time

K_UP = 119 
K_DOWN = 115
K_RIGHT = 100
K_LEFT = 97

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

    def wrap(self):
        if self.x < 0:
            self.x = w-1
        if self.y < 0:
            self.y = h-1
        if self.x >= w:
            self.x = 0
        if self.y >= h:
            self.y = 0

snake = Snake(int(w/2), int(h/2))
def update():
    snake.update()

def on_input(c):
    i = ord(c)
    if i == K_LEFT:
        snake.vx = -1
        snake.vy = 0
    elif i == K_RIGHT:
        snake.vx = 1
        snake.vy = 0
    elif i == K_UP:
        snake.vx = 0
        snake.vy = -1
    elif i == K_DOWN:
        snake.vx = 0
        snake.vy = 1

app = Screensaver(t, 20, update = update, on_input = on_input)
app.start()
