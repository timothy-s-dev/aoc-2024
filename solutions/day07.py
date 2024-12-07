from enum import Enum
import time
from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox
import pyperclip

from solutions.base_solution import BaseSolution


class Operator(Enum):
    ADD = 1
    MULTIPLY = 2
    CONCAT = 3

    def can_apply(self, target, numbers):
        return {
            self.ADD: lambda: target >= numbers[-1],
            self.MULTIPLY: lambda: target % numbers[-1] == 0,
            self.CONCAT: lambda: str(target) != str(numbers[-1]) and str(target).endswith(str(numbers[-1])),
        }[self]()

    def apply(self, target, numbers):
        return {
            self.ADD: lambda: (target - numbers[-1], numbers[:-1]),
            self.MULTIPLY: lambda: (target // numbers[-1], numbers[:-1]),
            self.CONCAT: lambda: (int(str(target)[:-len(str(numbers[-1]))]), numbers[:-1]),
        }[self]()


class Equation:
    def __init__(self, solution, numbers):
        self.solution = solution
        self.numbers = numbers

    @classmethod
    def from_input(cls, input_line):
        solution_str, numbers_str = input_line.split(': ')
        return cls(int(solution_str), [int(x) for x in numbers_str.split(' ')])

    def can_solve(self, allow_concat):
        if len(self.numbers) == 1 and self.solution == self.numbers[0]:
            return True
        if self.solution <= 0 or len(self.numbers) == 0:
            return False
        potential_solutions = []
        potential_operators = [Operator.ADD, Operator.MULTIPLY]
        if allow_concat:
            potential_operators.append(Operator.CONCAT)
        for operator in potential_operators:
            if operator.can_apply(self.solution, self.numbers):
                result = operator.apply(self.solution, self.numbers)
                potential_solutions.append(Equation(result[0], result[1]))
        if len(potential_solutions) == 0:
            return False
        return any(x.can_solve(allow_concat) for x in potential_solutions)


def load_equations(input_file):
    equations = []
    for line in input_file:
        equations.append(Equation.from_input(line))
    return equations

class Day07(BaseSolution):
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
        equations = load_equations(input_file)
        result = 0
        self.progress.update(total=len(equations), progress=0)
        for equation in equations:
            can_solve = equation.can_solve(part == 2)
            self.rich_log.write(f'Solution {'found' if can_solve else 'not found'} for {equation.solution}: {equation.numbers}')
            if can_solve:
                result += equation.solution
                self.digits.update(str(result))
            self.progress.advance(1)
            if not self.fast_forward:
                time.sleep(0.05)
