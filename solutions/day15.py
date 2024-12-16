import re
from enum import Enum

from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox
import pyperclip

from solutions.base_solution import BaseSolution





class TileType(Enum):
    EMPTY = 0
    WALL = 1
    ROCK = 2
    FROZEN_ROCK = 3

    @staticmethod
    def from_char(c):
        if c == '.':
            return TileType.EMPTY
        elif c == '#':
            return TileType.WALL
        elif c == 'O':
            return TileType.ROCK
        elif c == '@':
            return None
        else:
            raise ValueError("Invalid tile input")

    def to_char(self):
        if self == TileType.EMPTY:
            return '.'
        elif self == TileType.WALL:
            return '#'
        else:
            return 'O'


class Warehouse:
    def __init__(self, input):
        self.grid = [[TileType.from_char(c) for c in row] for row in input.split('\n')]
        self.width = len(self.grid[0])
        self.height = len(self.grid)
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] is None:
                    self.grid[row][col] = TileType.EMPTY
                    self.start_col = col
                    self.start_row = row

    def can_push(self, row, col, instruction):
        offset = instruction.get_new_position((0, 0))
        check_row = row + offset[0]
        check_col = col + offset[1]
        while self.grid[check_row][check_col] == TileType.ROCK:
            check_row += offset[0]
            check_col += offset[1]
        return self.grid[check_row][check_col] == TileType.EMPTY, check_row, check_col

class Instruction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

    def get_new_position(self, pos):
        if self == Instruction.LEFT:
            return pos[0], pos[1] - 1
        elif self == Instruction.RIGHT:
            return pos[0], pos[1] + 1
        elif self == Instruction.UP:
            return pos[0] - 1, pos[1]
        elif self == Instruction.DOWN:
            return pos[0] + 1, pos[1]
        else:
            raise ValueError("Invalid instruction input")

    @staticmethod
    def from_char(c):
        if c == '<':
            return Instruction.LEFT
        elif c == '>':
            return Instruction.RIGHT
        elif c == '^':
            return Instruction.UP
        elif c == 'v':
            return Instruction.DOWN
        else:
            raise ValueError("Invalid instruction input")


class Day15(BaseSolution):
    def __init__(self, rich_log: RichLog, progress: ProgressBar, *children: Widget):
        super().__init__(rich_log, progress, *children)
        self.digits = Digits(value='0', classes="results_digits top_margin_1")
        self.fast_forward = False

    def compose(self):
         with VerticalGroup():
                with HorizontalGroup():
                    with Center():
                        yield self.digits
                    yield Button("Copy", id="copy", classes="top_margin_1")
                    yield Checkbox(label="Fast Forward", classes="top_margin_1")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "copy":
            pyperclip.copy(self.digits.value)

    def on_checkbox_changed(self, event: Checkbox.Changed):
        self.fast_forward = event.checkbox.value

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part, test):
        (grid_input, instructions_input) = input_file.read().split('\n\n')
        warehouse = Warehouse(grid_input)
        col = warehouse.start_col
        row = warehouse.start_row
        instructions = [Instruction.from_char(c) for c in ''.join(instructions_input.split('\n'))]

        for instruction in instructions:
            (new_col, new_row)  = (col, row)
            if instruction == Instruction.LEFT:
                new_col -= 1
            elif instruction == Instruction.RIGHT:
                new_col += 1
            elif instruction == Instruction.UP:
                new_row -= 1
            elif instruction == Instruction.DOWN:
                new_row += 1

            if warehouse.grid[new_row][new_col] in [TileType.FROZEN_ROCK, TileType.WALL]:
                continue
            elif warehouse.grid[new_row][new_col] == TileType.EMPTY:
                col = new_col
                row = new_row
            else:
                can_push, dest_row, dest_col = warehouse.can_push(row, col, instruction)
                if can_push:
                    warehouse.grid[new_row][new_col] = TileType.EMPTY
                    warehouse.grid[dest_row][dest_col] = TileType.ROCK
                    col = new_col
                    row = new_row

        output_grid = [[t.to_char() for t in row] for row in warehouse.grid]
        for row in output_grid:
            self.rich_log.write(''.join(row))

        result = 0
        for row in range(warehouse.height):
            for col in range(warehouse.width):
                if warehouse.grid[row][col] == TileType.ROCK:
                    result += (row * 100) + col

        self.rich_log.write("[bold green]Result:[/bold green] " + str(result))
        self.digits.update(str(result))


        
