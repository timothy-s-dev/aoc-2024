from enum import Enum
import time
from itertools import combinations

from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox, Label
import pyperclip

from solutions.base_solution import BaseSolution


def find_trails(grid, path):
    path_end = path[-1]
    if path_end[0] < 0 or path_end[0] >= len(grid) or path_end[1] < 0 or path_end[1] >= len(grid[0]):
        return []
    last_value = grid[path_end[0]][path_end[1]]
    if len(path) > 1:
        previous_value = grid[path[-2][0]][path[-2][1]]
        if previous_value != last_value - 1:
            return []
    if last_value == 9:
        return [path]

    return (find_trails(grid, path + [(path_end[0] + 1, path_end[1] + 0)])
        + find_trails(grid, path + [(path_end[0] + 0, path_end[1] + 1)])
        + find_trails(grid, path + [(path_end[0] - 1, path_end[1] + 0)])
        + find_trails(grid, path + [(path_end[0] + 0, path_end[1] - 1)]))

class Day10(BaseSolution):
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
    async def run(self, input_file, part):
        grid = [[int(c) for c in line.strip()] for line in input_file.readlines()]
        starts = []
        for y in range(0, len(grid)):
            for x in range(0, len(grid[0])):
                if grid[y][x] == 0:
                    starts.append((y, x))

        self.progress.update(total=len(starts), progress=0)
        self.rich_log.write(f"Examining {len(starts)} starts")
        results = 0
        for start in starts:
            trails = find_trails(grid, [start])
            trailhead_score = len(set(map(lambda trail: trail[-1], trails))) if part == 1 else len(trails)
            results += trailhead_score
            self.rich_log.write(
                f"Start {start} has {trailhead_score} trails"
            )
            self.digits.update(str(results))
            self.progress.advance(1)
            if not self.fast_forward:
                time.sleep(0.05)

        self.rich_log.write(f"[bold green]Done, Result:[/bold green] {results}")


