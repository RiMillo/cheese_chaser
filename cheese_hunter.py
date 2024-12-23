import random
import tkinter as tk
import turtle
from functools import partial

GRID_SIZE = 400
CANVAS_WH = (GRID_SIZE, GRID_SIZE)
TILE_SIZE = 60
FONT = ("Helvetica", "18")
BOLD_FONT = *FONT, "bold"
BTN_DIR_KWARGS = {"width": 3, "height": 3, "font": BOLD_FONT}
# BTN_DIR_KWARGS = {"font": BOLD_FONT}

UP = {"name": "up", "text": "↑", "delta": turtle.Vec2D(0, 1), "color": "light blue"}
DOWN = {"name": "down", "text": "↓", "delta": turtle.Vec2D(0, -1), "color": "green"}
RIGHT = {"name": "right", "text": "→", "delta": turtle.Vec2D(1, 0), "color": "yellow"}
LEFT = {"name": "left", "text": "←", "delta": turtle.Vec2D(-1, 0), "color": "orange"}
MOVES = {move["name"]: move for move in [UP, DOWN, RIGHT, LEFT]}


class App(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("Cheese Chaser 🐭 🧀")
        self.n_tiles = 4
        self.tag_ID = 0
        self.wall_color = "red"
        self.cur_pos_n = turtle.Vec2D(0, 0)
        self.cheese_pos = turtle.Vec2D(self.n_tiles - 1, self.n_tiles - 1)
        self.n_walls = 5
        self.walls = set()
        self.generate_walls()
        # Buttons
        ## Directions
        self.up_btn = tk.Button(self, text=UP["text"], bg=UP["color"], **BTN_DIR_KWARGS)
        self.up_btn.grid(column=1, row=0, columnspan=2)
        self.left_btn = tk.Button(
            self, text=LEFT["text"], bg=LEFT["color"], **BTN_DIR_KWARGS
        )
        self.left_btn.grid(column=1, row=1)
        self.right_btn = tk.Button(
            self, text=RIGHT["text"], bg=RIGHT["color"], **BTN_DIR_KWARGS
        )
        self.right_btn.grid(column=2, row=1)
        self.down_btn = tk.Button(
            self, text=DOWN["text"], bg=DOWN["color"], **BTN_DIR_KWARGS
        )
        self.down_btn.grid(column=1, row=2, columnspan=2)
        self.undo_btn = tk.Button(self, text="Correggi")
        self.undo_btn.grid(column=1, row=3, columnspan=2)
        ## Game management
        self.play_btn = tk.Button(self, text="Parti!")
        self.play_btn.grid(row=4, column=0)
        self.reset_btn = tk.Button(self, text="Reset")
        self.reset_btn.grid(row=4, column=1)
        self.new_game_btn = tk.Button(self, text="Nuovo gioco")
        self.new_game_btn.grid(row=4, column=2)
        self.close_btn = tk.Button(self, text="Chiudi", command=parent.destroy)
        self.close_btn.grid(row=4, column=3)
        # Commands
        self.commands = []
        tk.Label(self, text="Comandi").grid(column=0, row=5)
        self.text_commands = tk.Text(self, height=2, width=30)
        self.text_commands.configure(font=BOLD_FONT)
        self.text_commands.grid(column=0, row=6, columnspan=4)

        def _direction_btn(direction):
            self.commands.append(direction["name"])
            self.text_commands.insert(tk.END, direction["text"])
            tID = f"cmd{self.tag_ID}"
            self.text_commands.tag_add(tID, "end-2c", "end-1c")
            self.text_commands.tag_config(tID, background=direction["color"])
            self.tag_ID += 1

        self.up_btn.configure(command=partial(_direction_btn, UP))
        self.down_btn.configure(command=partial(_direction_btn, DOWN))
        self.right_btn.configure(command=partial(_direction_btn, RIGHT))
        self.left_btn.configure(command=partial(_direction_btn, LEFT))

        def _undo():
            if self.commands:
                self.commands.pop(-1)
            self.text_commands.delete("end-2c", tk.END)

        self.undo_btn.configure(command=_undo)

        # Canvas
        self.canvas = tk.Canvas(self, width=CANVAS_WH[0], height=CANVAS_WH[1])
        self.canvas.grid(row=0, column=4, rowspan=10)
        # Turtle
        self.default_turtle_size = 4
        self.default_turtle_speed = "slow"
        self.turtle = turtle.RawTurtle(self.canvas)
        # Screen
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.bgcolor("black")
        # This one is not done, I don't understand why, but it is necessary to make the
        # otherones
        self.turtle.pensize(10)
        self.turtle.color("blue")
        self.turtle.forward(self.grid_size)

        self.start_pos = turtle.Vec2D(
            (TILE_SIZE - self.grid_size) / 2, (TILE_SIZE - self.grid_size) / 2
        )
        self.draw_board()
        self.turtle.teleport(*self.start_pos)

        # Main function
        def _chase():
            while self.commands:
                move = MOVES[self.commands.pop(0)]
                self.turtle.color(move["color"])
                won, message = self.check_move(move["delta"])
                if message is not None:
                    self.turtle.goto(self.turtle.pos() + TILE_SIZE / 2 * move["delta"])
                    tk.messagebox.showerror(title="OH NOOOOOO!", message=message)
                    break
                self.cur_pos_n += move["delta"]
                self.turtle.goto(self.turtle.pos() + TILE_SIZE * move["delta"])
                if won:
                    tk.messagebox.showinfo(
                        title="YEEEEEAH!",
                        message="Bravo! Hai trovato il formaggio",
                    )
                    break

        self.play_btn.configure(command=_chase)

        def _reset():
            # Handle commands
            self.commands.clear()
            self.text_commands.delete("1.0", tk.END)
            # Handle turtle
            self.turtle.clear()
            self.draw_board()
            self.turtle.teleport(*self.start_pos)
            self.cur_pos_n = turtle.Vec2D(0, 0)

        self.reset_btn.configure(command=_reset)

        def _new_game():
            self.generate_walls()
            _reset()
        self.new_game_btn.configure(command=_new_game)

    def reset_turtle_config(self, pos=None):
        self.turtle.speed(self.default_turtle_speed)
        self.turtle.pensize(self.default_turtle_size)
        if pos is not None:
            self.turtle.teleport(*pos)

    def draw_board(self, cheese_n_pos=None):
        self._draw_grid()
        self._draw_starting_point()
        self._draw_cheese(cheese_n_pos)
        self._draw_walls()

    def _draw_grid(self):
        # https://stackoverflow.com/questions/69122940/create-grid-with-turtles-in-python
        orig_pos = self.turtle.pos()
        self.turtle.speed("fastest")
        self.turtle.teleport(-self.grid_size / 2, self.grid_size / 2)
        self.turtle.pensize(2)
        angle = 90
        self.turtle.color("grey")
        for _ in range(2):
            for _ in range(1, self.n_tiles):
                self.turtle.forward(TILE_SIZE)
                self.turtle.right(angle)
                self.turtle.forward(self.grid_size)
                self.turtle.left(angle)

                angle = -angle

            self.turtle.forward(TILE_SIZE)
            self.turtle.right(angle)
        self.turtle.teleport(-self.grid_size / 2, self.grid_size / 2)
        self.turtle.pensize(self.default_turtle_size)
        self.turtle.color(self.wall_color)
        for _ in range(4):
            self.turtle.forward(self.grid_size)
            self.turtle.right(angle)
        #
        self.reset_turtle_config(orig_pos)

    def _draw_starting_point(self):
        orig_pos = self.turtle.pos()
        self.turtle.speed("fastest")
        self.turtle.color("purple")
        self.turtle.teleport(*(self.start_pos - turtle.Vec2D(0, TILE_SIZE / 8)))
        self.turtle.begin_fill()
        self.turtle.circle(TILE_SIZE / 6)
        self.turtle.end_fill()
        #
        self.reset_turtle_config(orig_pos)

    def _draw_cheese(self, n_xy=None):
        orig_pos = self.turtle.pos()
        cheese_pos = self.start_pos + TILE_SIZE * (
            turtle.Vec2D(*n_xy)
            if n_xy is not None
            else turtle.Vec2D(self.n_tiles - 1, self.n_tiles - 1)
        )
        # Recenter in tile
        cheese_pos -= turtle.Vec2D(0, TILE_SIZE / 8)
        self.turtle.teleport(*cheese_pos)
        self.turtle.speed("fastest")
        self.turtle.color("yellow")
        self.turtle.begin_fill()
        # Draws a triangle
        self.turtle.circle(TILE_SIZE / 4, steps=3)
        self.turtle.end_fill()
        #
        self.reset_turtle_config(orig_pos)

    def _draw_walls(self):
        orig_pos = self.turtle.pos()
        #
        self.turtle.speed("fastest")
        self.turtle.color(self.wall_color)
        for c1, c2 in self.walls:
            wall_dir = (c2 - c1).rotate(90)
            start = TILE_SIZE * (c1 + c2 - wall_dir) * 0.5 + self.start_pos
            self.turtle.teleport(*start)
            self.turtle.goto(start + TILE_SIZE * wall_dir)
        #
        self.reset_turtle_config(orig_pos)

    @property
    def grid_size(self):
        return self.n_tiles * TILE_SIZE

    def is_valid_move(self, n_pos):
        return all(0 <= n_xy < self.n_tiles for n_xy in n_pos)

    def check_move(self, delta):
        won, message = False, None
        new_pos = self.cur_pos_n + delta
        if self.cheese_pos[0] == new_pos[0] and self.cheese_pos[1] == new_pos[1]:
            won = True
        elif not self.is_valid_move(new_pos):
            message = "Sei uscito dall'area di gioco!"
        elif (self.cur_pos_n, new_pos) in self.walls:
            message = "Sei andato contro un muro!"
        return won, message

    def get_random_pos(self):
        return turtle.Vec2D(
            random.randrange(self.n_tiles), random.randrange(self.n_tiles)
        )

    @staticmethod
    def get_random_move():
        x = random.randrange(-1, 2)
        y = 0 if x != 0 else random.choice([-1, 1])
        return turtle.Vec2D(x, y)

    def generate_walls(self):
        # TODO: check if cheese is reachable
        self.walls.clear()
        while len(self.walls) < self.n_walls:
            start = self.get_random_pos()
            end = start + self.get_random_move()
            if self.is_valid_move(end):
                self.walls.add((start, end))


if __name__ == "__main__":
    w = tk.Tk()
    App(w).pack()  # side="top", fill="both", expand=True)
    w.mainloop()
