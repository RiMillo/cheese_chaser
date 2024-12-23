import random
import tkinter as tk
import turtle
from functools import partial, partialmethod

GRID_SIZE = 400
CANVAS_WH = (GRID_SIZE, GRID_SIZE)
TILE_SIZE = 60
FONT = ("Helvetica", "18")
BOLD_FONT = *FONT, "bold"
BTN_DIR_KWARGS = {"width": 3, "height": 3, "font": BOLD_FONT}
BTN_HANDLE_KWARGS = {"width": 10}

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
        self.cheese_pos = self.generate_cheese()
        self.n_walls = 5
        self.walls = set()
        self.generate_walls()
        # Buttons
        ## Directions
        self.up_btn = tk.Button(self, text=UP["text"], bg=UP["color"], **BTN_DIR_KWARGS)
        self.up_btn.grid(column=0, row=0, columnspan=4)
        self.left_btn = tk.Button(
            self, text=LEFT["text"], bg=LEFT["color"], **BTN_DIR_KWARGS
        )
        self.left_btn.grid(column=0, row=1, columnspan=2)
        self.right_btn = tk.Button(
            self, text=RIGHT["text"], bg=RIGHT["color"], **BTN_DIR_KWARGS
        )
        self.right_btn.grid(column=2, row=1, columnspan=2)
        self.down_btn = tk.Button(
            self, text=DOWN["text"], bg=DOWN["color"], **BTN_DIR_KWARGS
        )
        self.down_btn.grid(column=0, row=2, columnspan=4)
        self.undo_btn = tk.Button(self, text="Correggi", **BTN_HANDLE_KWARGS)
        self.undo_btn.grid(column=0, row=3, columnspan=4)
        ## Game management
        self.play_btn = tk.Button(self, text="Parti!", **BTN_HANDLE_KWARGS)
        self.play_btn.grid(row=4, column=0)
        self.reset_btn = tk.Button(self, text="Reset", **BTN_HANDLE_KWARGS)
        self.reset_btn.grid(row=4, column=1)
        self.new_game_btn = tk.Button(self, text="Nuovo gioco", **BTN_HANDLE_KWARGS)
        self.new_game_btn.grid(row=4, column=2)
        self.close_btn = tk.Button(
            self, text="Chiudi", command=parent.destroy, **BTN_HANDLE_KWARGS
        )
        self.close_btn.grid(row=4, column=3)
        # Commands
        self.commands = []
        tk.Label(self, text="Comandi").grid(column=0, row=5)
        self.text_commands = tk.Text(self, height=2, width=30)
        self.text_commands.configure(font=BOLD_FONT)
        self.text_commands.grid(column=0, row=6, columnspan=4)

        def _direction_func(direction, event):
            # Event is unused but left because is needed in key-binding below
            self.commands.append(direction["name"])
            self.text_commands.insert(tk.END, direction["text"])
            tID = f"cmd{self.tag_ID}"
            self.text_commands.tag_add(tID, "end-2c", "end-1c")
            self.text_commands.tag_config(tID, background=direction["color"])
            self.tag_ID += 1
        # Bind buttons and keys to direction functions
        self.up_btn.configure(command=partial(_direction_func, UP, None))
        self.parent.bind("<Up>", partial(_direction_func, UP))
        self.down_btn.configure(command=partial(_direction_func, DOWN, None))
        self.parent.bind("<Down>", partial(_direction_func, DOWN))
        self.right_btn.configure(command=partial(_direction_func, RIGHT, None))
        self.parent.bind("<Right>", partial(_direction_func, RIGHT))
        self.left_btn.configure(command=partial(_direction_func, LEFT, None))
        self.parent.bind("<Left>", partial(_direction_func, LEFT))

        def _undo(event):
            # Event is unused but left because is needed in key-binding below
            if self.commands:
                self.commands.pop(-1)
            self.text_commands.delete("end-2c", tk.END)

        self.undo_btn.configure(command=partial(_undo, None))
        self.parent.bind("<BackSpace>", _undo)

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
        def _chase(event):
            # Event is unused but left because is needed in key-binding below
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

        self.play_btn.configure(command=partial(_chase, None))
        self.parent.bind("<Return>", _chase)

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
            # Regenerate random pos
            self.generate_walls()
            self.cheese_pos = self.generate_cheese()
            # Redraw
            _reset()

        self.new_game_btn.configure(command=_new_game)

    def reset_turtle_config(self, pos=None):
        self.turtle.speed(self.default_turtle_speed)
        self.turtle.pensize(self.default_turtle_size)
        if pos is not None:
            self.turtle.teleport(*pos)

    def draw_board(self):
        self._draw_grid()
        self._draw_starting_point()
        self._draw_cheese()
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
        pos = self.start_pos - turtle.Vec2D(0, TILE_SIZE / 5)
        # Ears
        delta_ear_x = TILE_SIZE / 8
        delta_ear_y = TILE_SIZE / 4
        for dx in [delta_ear_x, -delta_ear_x]:
            ear_pos = pos + (dx, delta_ear_y)
            self.turtle.teleport(*ear_pos)
            self.turtle.begin_fill()
            self.turtle.color("grey")
            self.turtle.circle(TILE_SIZE / 10)
            self.turtle.color("pink")
            self.turtle.circle(2)
            self.turtle.end_fill()
        # Main head
        self.turtle.color("grey")
        self.turtle.teleport(*pos)
        self.turtle.begin_fill()
        self.turtle.circle(TILE_SIZE / 6)
        self.turtle.end_fill()
        # Nose
        self.turtle.color("pink")
        self.turtle.begin_fill()
        self.turtle.teleport(*pos)
        self.turtle.circle(2)
        self.turtle.end_fill()
        #
        self.reset_turtle_config(orig_pos)

    def _draw_cheese(self):
        orig_pos = self.turtle.pos()
        cheese_pos = self.start_pos + TILE_SIZE * self.cheese_pos
        # Recenter in tile
        cheese_pos -= turtle.Vec2D(0, TILE_SIZE / 8)
        self.turtle.teleport(*cheese_pos)
        self.turtle.speed("fastest")
        self.turtle.color("yellow")
        self.turtle.begin_fill()
        # Draws a triangle
        self.turtle.circle(TILE_SIZE / 4, steps=3)
        self.turtle.end_fill()
        # Holes
        self.turtle.color("black")
        for delta in [
            (-TILE_SIZE / 20, TILE_SIZE / 8),
            (TILE_SIZE / 12, TILE_SIZE / 4),
            (-TILE_SIZE / 6, TILE_SIZE / 3),
        ]:
            self.turtle.teleport(*(cheese_pos + delta))
            self.turtle.begin_fill()
            self.turtle.circle(1)
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

    def is_inside_board(self, n_pos):
        return all(0 <= n_xy < self.n_tiles for n_xy in n_pos)

    @staticmethod
    def get_wall(cell1, cell2):
        # Ensure order, it makes it easier to check for existence in a list
        return tuple(sorted((cell1, cell2)))

    def check_move(self, delta):
        won, message = False, None
        new_pos = self.cur_pos_n + delta
        if self.cheese_pos[0] == new_pos[0] and self.cheese_pos[1] == new_pos[1]:
            won = True
        elif not self.is_inside_board(new_pos):
            message = "Sei uscito dall'area di gioco!"
        elif self.get_wall(self.cur_pos_n, new_pos) in self.walls:
            message = "Sei andato contro un muro!"
        return won, message

    def get_random_pos(self, min_pos=None):
        min_pos = min_pos if min_pos is not None else 0
        return turtle.Vec2D(
            random.randrange(min_pos, self.n_tiles),
            random.randrange(min_pos, self.n_tiles),
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
            if self.is_inside_board(end):
                self.walls.add(self.get_wall(start, end))

    generate_cheese = partialmethod(get_random_pos, 2)


if __name__ == "__main__":
    w = tk.Tk()
    App(w).pack()  # side="top", fill="both", expand=True)
    w.mainloop()
