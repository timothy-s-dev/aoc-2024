from enum import Enum
from functools import cmp_to_key
import time
from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox, Label
import re
import pyperclip

from solutions.base_solution import BaseSolution


class Direction(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

    def turn_right(self):
        if self == Direction.NORTH:
            return Direction.EAST
        elif self == Direction.EAST:
            return Direction.SOUTH
        elif self == Direction.SOUTH:
            return Direction.WEST
        elif self == Direction.WEST:
            return Direction.NORTH
    
    def get_x_offset(self):
        if self == Direction.EAST:
            return 1
        elif self == Direction.WEST:
            return -1
        return 0
    
    def get_y_offset(self):
        if self == Direction.SOUTH:
            return 1
        elif self == Direction.NORTH:
            return -1
        return 0


class Day06(BaseSolution):
    def __init__(self, rich_log: RichLog, progress: ProgressBar, *children: Widget):
        super().__init__(rich_log, progress, *children)
        self.digits = Digits(value='0', classes="results_digits top_margin_1")
        self.grid_display = Label("...\n...\n...")
        self.fast_forward = False

    def compose(self):
         with VerticalGroup():
                with HorizontalGroup():
                    with Center():
                        yield self.digits
                    yield Button("Copy", id="copy", classes="top_margin_1")
                    yield Checkbox(label="Fast Forward", classes="top_margin_1")
                yield self.grid_display

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "copy":
            pyperclip.copy(self.digits.value)

    def on_checkbox_changed(self, event: Checkbox.Changed):
        self.fast_forward = event.checkbox.value

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part):
        grid, start_x, start_y = self.load_grid(input_file)
        facing = Direction.NORTH
        
        visited_squares, _ = self.run_maze(grid, start_x, start_y, facing)

        if part == 1:
            self.digits.update(str(len(visited_squares)))
            self.rich_log.write(f"[bold green]Done, Result:[/bold green] {len(visited_squares)}")
        else:
            results = 0
            self.rich_log.write(f"Initial run complete, checking {len(visited_squares) - 1} potential obstacle locations...")
            self.progress.update(total=len(visited_squares) - 1, progress=0)
            for (x, y) in visited_squares:
                # Can't place an obstacle on the starting square
                if (x, y) == (start_x, start_y):
                    continue
                new_grid = self.add_obstacle_to_grid(grid, x, y)
                _, new_grid_looped = self.run_maze(new_grid, start_x, start_y, facing)
                if new_grid_looped:
                    results += 1
                    self.digits.update(str(results))
                self.progress.advance(1)
            self.rich_log.write(f"[bold green]Done, Result:[/bold green] {results}")

    def run_maze(self, grid, x, y, facing):
        visited = set([(x, y, facing)])
        visited_squares = set([(x, y)])

        while True:
            if not self.fast_forward:
                time.sleep(0.005)

            next_x = x + facing.get_x_offset()
            next_y = y + facing.get_y_offset()

            if not self.fast_forward:
                self.update_grid_display(grid, visited_squares, x, y)

            if next_x < 0 or next_x >= len(grid[0]) or next_y < 0 or next_y >= len(grid):
                return visited_squares, False
                break
            elif (next_x, next_y, facing) in visited:
                return visited_squares, True
                break
            elif grid[next_y][next_x] == '#':
                facing = facing.turn_right()
                visited.add((x, y, facing))
                visited_squares.add((x, y))
                continue
            elif grid[next_y][next_x] == '.':
                x, y = next_x, next_y
                visited.add((x, y, facing))
                visited_squares.add((x, y))
                continue

    def load_grid(self, input_file):
        input = input_file.readlines()
        grid = [[c for c in line.strip()] for line in input]
        start_x, start_y = 0, 0
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x] == '^':
                    start_x, start_y = x, y
                    grid[y][x] = '.'
        return grid, start_x, start_y
    
    def add_obstacle_to_grid(self, grid, x, y):
        output_grid = []
        for row in grid:
            output_grid.append(row.copy())
        output_grid[y][x] = '#'
        return output_grid
    
    def update_grid_display(self, grid, visited_squares, center_x, center_y):
        output_grid = []

        if len(grid[0]) <= 20:
            center_x = len(grid[0]) // 2
        elif center_x < 10:
            center_x = 10
        elif center_x > len(grid[0]) - 10:
            center_x = len(grid[0]) - 10

        if len(grid) <= 20:
            center_y = len(grid) // 2
        elif center_y < 10:
            center_y = 10
        elif center_y > len(grid) - 10:
            center_y = len(grid) - 10

        min_x = max(center_x - 10, 0)
        max_x = min(center_x + 10, len(grid[0]))
        min_y = max(center_y - 10, 0)
        max_y = min(center_y + 10, len(grid))

        for y in range(min_y, max_y):
            row = []
            for x in range(min_x, max_x):
                if (x, y) in visited_squares:
                    row.append('X')
                else:
                    row.append(grid[y][x])
            output_grid.append(row)

        self.grid_display.update("\n".join(["".join(row) for row in output_grid]))
