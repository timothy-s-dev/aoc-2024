from enum import Enum
from functools import lru_cache
import time
from itertools import chain

from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox, Label
import pyperclip

from solutions.base_solution import BaseSolution

    
@lru_cache(maxsize=None)
def get_num_rocks(val, blink_count):
    if blink_count == 0:
        return 1
    if val == 0:
        return get_num_rocks(1, blink_count - 1)
    elif len(str(val)) % 2 == 0:
        midpoint = len(str(val)) // 2
        return (get_num_rocks(int(str(val)[:midpoint]), blink_count - 1)
            + get_num_rocks(int(str(val)[midpoint:]), blink_count - 1))
    else:
        return get_num_rocks(val * 2024, blink_count - 1)

class Day11(BaseSolution):
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
        values = [int(x) for x in input_file.read().strip().split(' ')]
        
        steps = 25 if part == 1 else 75
        total_rocks = 0
        self.progress.update(total=len(values), progress=0)
        for value in values:
            total_rocks += get_num_rocks(value, steps)
            self.progress.advance(1)
            self.digits.update(value=str(total_rocks))

        self.rich_log.write(f"[bold green]Done, Result:[/bold green] {total_rocks}")


