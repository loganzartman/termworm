from termpixels import App, Color 
from random import randint, choice
import time

K_UP = "up"
K_DOWN = "down"
K_RIGHT = "right"
K_LEFT = "left"

game_x = 0
game_y = 3
game_w = 4
game_h = 4

class GameOver(BaseException):
    def __init__(self, message=""):
        super().__init__(message)

class TermwormApp(App):
    def on_start(self):
        self.mode = "game"
        self.worm = Worm(int(game_w/2), int(game_h/2))
        
        self.score = 0
        self.hiscore = 0
        self.t0 = time.perf_counter()

        self.on_resize()
        self.food_x = self.worm.x
        self.food_y = self.worm.y

    def on_resize(self):
        global game_w, game_h
        game_w = int(self.screen.w / 2 - game_x)
        game_h = self.screen.h - game_y
        self.move_food()

    def on_frame(self):
        if self.mode == "game":
            delay = max(0.1 - self.score / 50 * 0.1, 0.)
            if time.perf_counter() - self.t0 >= delay:
                self.t0 = time.perf_counter()
                try:
                    self.update_game()
                except GameOver:
                    self.mode = "game-over"
        if self.mode == "game-over":
            self.update_endgame()

    def on_key(self, c):
        if c == K_LEFT:
            if not self.worm.intersecting(self.worm.x-1, self.worm.y):
                self.worm.vx = -1
                self.worm.vy = 0
        elif c == K_RIGHT:
            if not self.worm.intersecting(self.worm.x+1, self.worm.y):
                self.worm.vx = 1
                self.worm.vy = 0
        elif c == K_UP:
            if not self.worm.intersecting(self.worm.x, self.worm.y-1):
                self.worm.vx = 0
                self.worm.vy = -1
        elif c == K_DOWN:
            if not self.worm.intersecting(self.worm.x, self.worm.y+1):
                self.worm.vx = 0
                self.worm.vy = 1
        
    def update_game(self):
        # app.framerate = int(min(20, score / 5) + 10)
        self.screen.clear()
        self.worm.update(self.screen)
        if self.worm.x == self.food_x and self.worm.y == self.food_y:
            self.move_food()
            self.worm.length += 1
            self.score += 1
            self.hiscore = max(self.hiscore, self.score)
        self.draw_ui()
        self.draw_food()
        self.screen.update()

    def update_endgame(self):
        # Draw endgame screen
        self.screen.clear()
        w = self.screen.w
        h = self.screen.h
        self.screen.print("Game over!", w // 2 - 5, h // 3, fg=Color.rgb(1,1,0))
        self.screen.print("You scored: {}".format(self.score), w // 2 - 7, h // 3 + 1, fg=Color.rgb(1,1,1))
        self.screen.print("Press CTRL+C to quit.", w // 2 - 10, h // 3 + 2, fg=Color.rgb(0.5,0.5,0.5))
        self.screen.update()

    def draw_ui(self):
        self.screen.print("~TermWorm~", 0, 0, fg=Color.rgb(1,1,1))
        self.screen.print("░ Score: {}".format(self.score), 0, 1, fg=Color.rgb(0.5,0.5,0.5))
        self.screen.print("─" * self.screen.w, 0, 2, fg=Color.rgb(0.5,0.5,0.5))

    def draw_food(self):
        self.screen.print("░░", self.food_x * 2 + game_x, self.food_y + game_y)

    def move_food(self):
        positions = [(x,y) for x in range(game_w) for y in range(game_h)
                     if not self.worm.intersecting(x, y)]
        self.food_x, self.food_y = choice(positions)

class Worm:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 1
        self.vy = 0
        self.length = 5
        self.old = []

    def update(self, screen):
        self.old += [(self.x, self.y)]
        if len(self.old) > self.length:
            self.old.pop(0)

        for x, y in self.old:
            col = Color.hsl(time.monotonic() * 0.1, 1.0, 0.7)
            screen.print("██", x * 2 + game_x, y + game_y, fg=col)

        if self.intersecting(self.x + self.vx, self.y + self.vy):
            raise GameOver()

        self.x += self.vx
        self.y += self.vy
        self.wrap()

    def intersecting(self, x, y):
        return any(x == pos[0] and y == pos[1] for pos in self.old[1:])

    def wrap(self):
        if self.x < 0:
            self.x = game_w - 1
        if self.y < 0:
            self.y = game_h - 1
        if self.x >= game_w:
            self.x = 0
        if self.y >= game_h:
            self.y = 0

TermwormApp().start()
