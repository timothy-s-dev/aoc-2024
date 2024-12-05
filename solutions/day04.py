import time
from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup, Middle
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Label, Checkbox
import pyperclip

from solutions.base_solution import BaseSolution


offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
display_height = 20

class Day04(BaseSolution):
    def __init__(self, rich_log: RichLog, progress: ProgressBar, *children: Widget):
        super().__init__(rich_log, progress, *children)
        self.digits = Digits(value='0', classes="results_digits")
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

    def update_grid_display(self, grid, start_row):
        chunk = grid[start_row:start_row+display_height]
        self.grid_display.update("\n".join(["".join(row) for row in chunk]))

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part):
        result = 0
        input = input_file.readlines()
        result_grid = [['.' for _ in line.strip()] for line in input]
        self.update_grid_display(result_grid, 0)
        self.progress.update(total=len(input) * len(input[0]), progress=0)
        self.rich_log.write("Searching...")
        for row in range(0, len(input)):
            for col in range(0, len(input[row])):
                sleep = False
                if part == 1:
                    for offset in offsets:
                        if self.is_xmas(row, col, offset, input):
                            result += 1
                            result_grid = self.add_xmas_to_result_grid(row, col, offset, result_grid)
                            sleep = True
                else:
                    if self.is_x_mas(row, col, input):
                        result += 1
                        result_grid = self.add_x_mas_to_result_grid(row, col, input, result_grid)
                        sleep = True
                self.update_grid_display(result_grid, min(max(int(row - display_height / 2), 0), len(input) - display_height))
                self.progress.advance(1)
                self.digits.update(str(result))
                if sleep and not self.fast_forward:
                    time.sleep(0.05 if not self.fast_forward else 0.0001)
        self.rich_log.write(f"[bold green]Done, Result:[/bold green] {result}")

    def is_xmas(self, row, col, offset, input):
        # Check if we're inside the grid
        if not (0 <= row < len(input) and 0 <= col < len(input[row])):
            return False
        # Check if full offset is still inside the grid
        if not (0 <= row + offset[0]*3 < len(input) and 0 <= col + offset[1]*3 < len(input[row])):
            return False
        # Check if the current character is "X"
        if input[row][col] != "X":
            return False
        # Check if the next three characters are "M", "A" and "S"
        if input[row + offset[0]][col + offset[1]] != "M":
            return False
        if input[row + offset[0]*2][col + offset[1]*2] != "A":
            return False
        if input[row + offset[0]*3][col + offset[1]*3] != "S":
            return False
        return True
    
    def is_x_mas(self, row, col, input):
        # Check if we're inside the grid by at least 1 space
        if not (0 < row < len(input)-1 and 0 < col < len(input[row])-1):
            return False
        # Check if the current character is "A"
        if input[row][col] != "A":
            return False
        # Check if the crossing characters are "M" and "S"
        down_valid = (input[row-1][col-1] == "M" and input[row+1][col+1] == "S") or (input[row-1][col-1] == "S" and input[row+1][col+1] == "M")
        up_valid = (input[row-1][col+1] == "M" and input[row+1][col-1] == "S") or (input[row-1][col+1] == "S" and input[row+1][col-1] == "M")
        return down_valid and up_valid
    
    def add_xmas_to_result_grid(self, row, col, offset, result_grid):
        result_grid[row][col] = "X"
        result_grid[row + offset[0]][col + offset[1]] = "M"
        result_grid[row + offset[0]*2][col + offset[1]*2] = "A"
        result_grid[row + offset[0]*3][col + offset[1]*3] = "S"
        return result_grid
    
    def add_x_mas_to_result_grid(self, row, col, input, result_grid):
        result_grid[row][col] = input[row][col]
        result_grid[row-1][col-1] = input[row-1][col-1]
        result_grid[row+1][col+1] = input[row+1][col+1]
        result_grid[row-1][col+1] = input[row-1][col+1]
        result_grid[row+1][col-1] = input[row+1][col-1]
        return result_grid
        
