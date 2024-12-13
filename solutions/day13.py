import re

from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox
import pyperclip

from solutions.base_solution import BaseSolution


number_regex = re.compile(r'(\d+)')


class Problem:
    def __init__(self, input, offset):
        lines = input.split('\n')
        (self.button_a_x, self.button_a_y) = map(int, number_regex.findall(lines[0]))
        (self.button_b_x, self.button_b_y) = map(int, number_regex.findall(lines[1]))
        (self.prize_x, self.prize_y) = map(lambda x: int(x) + offset, number_regex.findall(lines[2]))
    
    def solve(self):
        b_presses = (((self.prize_x * self.button_a_y) - (self.prize_y * self.button_a_x)) /
                ((self.button_b_x * self.button_a_y) - (self.button_b_y * self.button_a_x)));
        a_presses = (self.prize_x - (self.button_b_x * b_presses)) / self.button_a_x;
        return a_presses, b_presses

class Day13(BaseSolution):
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
        total_cost = 0
        for puzzle_input in input_file.read().split('\n\n'):
            problem = Problem(puzzle_input, 0 if part == 1 else 10000000000000)
            self.rich_log.write(f"Problem: AX={problem.button_a_x}, AY={problem.button_a_y}, BX={problem.button_b_x}, BY={problem.button_b_y}, PX={problem.prize_x}, PY={problem.prize_y}")
            a_presses, b_presses = problem.solve()
            if a_presses == int(a_presses) and b_presses == int(b_presses):
                cost = int(a_presses) * 3 + int(b_presses)
                total_cost += cost
                self.rich_log.write(f"  Solution: A={a_presses}, B={b_presses} (costs {cost})")
                self.digits.update(str(total_cost))
            else:
                self.rich_log.write("  No solution")
        self.rich_log.write("[bold green]Total cost:[/bold green] " + str(total_cost))
        
