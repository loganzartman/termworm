from termpixels import App, Buffer, Color 
from termpixels.drawing import draw_box, BOX_CHARS_DOUBLE
from termpixels.util import terminal_len
from random import randint, choice
import time

MODE_GAME = "game"
MODE_GAMEOVER = "gameover"

K_LEFT = "left"
K_RIGHT = "right"
K_UP = "up"
K_DOWN = "down"

def load_hiscore():
    try:
        with open("hiscore", "x") as f:
            f.write("0")
    except:
        pass
    with open("hiscore", "r") as f:
        return int(f.read())

def save_hiscore(score):
    with open("hiscore", "w") as f:
        f.write(str(score))

class GameOver(BaseException):
    def __init__(self, message=""):
        super().__init__(message)

class Worm:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 1
        self.vy = 0
        self.length = 20
        self.old = []

    def update(self, buffer):
        self.old += [(self.x, self.y)]
        if len(self.old) > self.length:
            self.old.pop(0)

        for i, (x, y) in enumerate(self.old):
            col = Color.rgb(1,1,0)
            buffer.print("██", x * 2, y, fg=col)

        if self.intersecting(self.x + self.vx, self.y + self.vy):
            raise GameOver()

        self.x += self.vx
        self.y += self.vy
        self.wrap(buffer)

    def intersecting(self, x, y):
        return any(x == pos[0] and y == pos[1] for pos in self.old[1:])

    def wrap(self, buffer):
        w = buffer.w // 2
        h = buffer.h
        if self.x < 0:
            self.x = w - 1
        if self.y < 0:
            self.y = h - 1
        if self.x >= w:
            self.x = 0
        if self.y >= h:
            self.y = 0

def print_hcenter(buffer, text, *, y, **kwargs):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        x = int(buffer.w / 2 - terminal_len(line) / 2)
        buffer.print(line, x, y + i, **kwargs)

def multiply_buffer(buffer, f):
    for x in range(buffer.w):
        for y in range(buffer.h):
            buffer[x,y].fg *= f
            buffer[x,y].bg *= f

def main():
    app = App(framerate=20)

    ui_height = 3
    game_buffer = Buffer(0,0)

    score = 0
    hiscore = load_hiscore()
    mode = None
    worm = None
    food_x = 0
    food_y = 0
    control_x = 0
    control_y = 0

    def move_food():
        nonlocal food_x, food_y
        w = game_buffer.w // 2
        h = game_buffer.h
        positions = [(x,y) for x in range(w) for y in range(h)
                     if not worm.intersecting(x, y)]
        food_x, food_y = choice(positions)

    @app.on("start")
    def start():
        nonlocal score, mode, worm
        score = 0
        worm = Worm(randint(0, app.screen.w - 1), randint(0, app.screen.h - 1))
        mode = MODE_GAME
    
    @app.on("start")
    @app.on("resize")
    def resize():
        game_buffer.resize(app.screen.w, app.screen.h - ui_height)
        move_food()

    @app.on("key")
    def key(k):
        nonlocal control_x, control_y
        if mode == MODE_GAME:
            if k == K_UP:
                control_y = -1
            if k == K_DOWN:
                control_y = 1
            if k == K_LEFT:
                control_x = -1
            if k == K_RIGHT:
                control_x = 1
        elif mode == MODE_GAMEOVER:
            if k == "\n":
                app.emit("start")

    def frame_game():
        nonlocal control_x, control_y
        nonlocal score, hiscore
        nonlocal mode
        
        # handle input
        if control_x != 0 and not worm.intersecting(worm.x + control_x, worm.y):
            worm.vx = control_x
            worm.vy = 0
            control_x = 0
        if control_y != 0 and not worm.intersecting(worm.x, worm.y + control_y):
            worm.vy = control_y
            worm.vx = 0
            control_y = 0

        if worm.intersecting(food_x, food_y):
            score += 1
            worm.length += 1
            hiscore = max(hiscore, score)
            save_hiscore(hiscore)
            move_food()
        
        game_buffer.clear()
        game_buffer.print("░░", food_x * 2, food_y)

        try:
            worm.update(game_buffer)
        except GameOver:
            mode = MODE_GAMEOVER
            multiply_buffer(game_buffer, 0.4)
            return
        
        # draw
        app.screen.clear()
        app.screen.print("~TermWorm~", 0, 0)
        app.screen.print("Score: {}".format(score), 0, 1, fg=Color.rgb(.7,.7,.7))
        app.screen.print("  Hi: {}".format(hiscore), fg=Color.rgb(.7,.7,0))
        draw_box(app.screen, 0, 2, app.screen.w, 1, chars=BOX_CHARS_DOUBLE)
        app.screen.blit(game_buffer, 0, ui_height)
        app.screen.update()
    
    def frame_gameover():
        dark = Color.rgb(0.2,0.2,0.2)
        app.screen.clear()
        app.screen.blit(game_buffer, 0, ui_height)
        print_hcenter(app.screen, "Game over!", y=3, fg=Color.rgb(1,1,0), bg=dark)
        print_hcenter(app.screen, "Press enter to restart", y=4, fg=Color.rgb(0.75,0.75,0.75), bg=dark)
        print_hcenter(app.screen, "Press escape to exit", y=5, fg=Color.rgb(0.75,0.75,0.75), bg=dark)
        app.screen.update()

    @app.on("frame")
    def frame():
        if mode == "game":
            frame_game()
        elif mode == "gameover":
            frame_gameover()
        else:
            raise Exception("Invalid mode: {}".format(mode))
    
    @app.on("after_stop")
    def after_stop():
        print("Thanks for playing TermWorm!")

    app.run()

if __name__ == "__main__":
    main()
