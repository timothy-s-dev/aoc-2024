from textual import work
from textual.containers import Center, Middle
from textual.widget import Widget
from textual.widgets import ProgressBar, RichLog, Digits

from solutions.base_solution import BaseSolution


class Day02(BaseSolution):
    def __init__(self, rich_log: RichLog, progress: ProgressBar, *children: Widget):
        super().__init__(rich_log, progress, *children)
        self.digits = Digits(value='0', classes="results_digits")

    def compose(self):
        with Center():
            with Middle():
                yield self.digits

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part):
        result = 0
        lines = input_file.readlines()
        self.rich_log.write("Calculating...")
        self.progress.update(total=len(lines), progress=0)
        for line in lines:
            values = [int(x) for x in line.split(' ')]
            if is_safe(values):
                result += 1
            elif part == 2:
                for i in range(0, len(values)):
                    if is_safe(values[:i] + values[i + 1:]):
                        result += 1
                        break
            self.progress.advance(1)
            self.digits.update(str(result))
        self.rich_log.write(f"[bold green]Done, Result:[/bold green] {result}")

def is_safe(values):
    deltas = [values[i+1] - values[i] for i in range(0, len(values) - 1)]

    positive = [x > 0 for x in deltas]
    negative = [x < 0 for x in deltas]
    if not all(positive) and not all(negative):
        return False

    small = [1 <= abs(x) <= 3 for x in deltas]
    return all(small)