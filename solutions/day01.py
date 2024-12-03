from textual import work
from textual.containers import Center, Middle
from textual.widget import Widget
from textual.widgets import ProgressBar, RichLog, Digits

from solutions.base_solution import BaseSolution


class Day01(BaseSolution):
    def __init__(self, rich_log: RichLog, progress: ProgressBar, *children: Widget):
        super().__init__(rich_log, progress, *children)
        self.digits = Digits(value='0', classes="results_digits")

    def compose(self):
        with Center():
            with Middle():
                yield self.digits

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part):
        column1, column2 = self.process_file(input_file)
        result = 0
        self.rich_log.write("Calculating...")
        self.progress.update(total=len(column1), progress=0)
        for i in range(0, len(column1)):
            if part == 1:
                result += abs(column1[i] - column2[i])
            else:
                occurrences = column2.count(column1[i])
                result += column1[i] * occurrences
            self.progress.advance(1)
            self.digits.update(str(result))
        self.rich_log.write(f"[bold green]Done, Result:[/bold green] {result}")

    def process_file(self, input_file):
        self.rich_log.write("Processing File...")
        column1 = []
        column2 = []
        for line in input_file:
            val1, val2 = [int(x) for x in line.split('   ')]
            column1.append(val1)
            column2.append(val2)
        self.rich_log.write(f"Loaded {len(column1)} rows, sorting lists...")
        column1.sort()
        column2.sort()
        return column1, column2
