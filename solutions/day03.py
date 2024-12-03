from textual import work
from textual.containers import Center, Middle
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits
import re
import pyperclip

from solutions.base_solution import BaseSolution


regex = re.compile(r"(do)\(\)|(don't)\(\)|(mul)\((\d{1,3}),(\d{1,3})\)")

class Day03(BaseSolution):
    def __init__(self, rich_log: RichLog, progress: ProgressBar, *children: Widget):
        super().__init__(rich_log, progress, *children)
        self.digits = Digits(value='0', classes="results_digits")

    def compose(self):
        with Center():
            with Middle():
                yield Button(id="copy")
                yield self.digits

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "copy":
            pyperclip.copy(self.digits.value)

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part):
        result = 0
        lines = '\n'.join(input_file.readlines())
        self.rich_log.write("Finding valid calls...")
        matches = regex.findall(lines)
        self.progress.update(total=len(matches), progress=0)
        self.rich_log.write("Calculating...")
        enabled = True
        for match in matches:
            if (match[0] == "do" and part == 2):
                self.rich_log.write("[green]ENABLE")
                enabled = True
            elif (match[1] == "don't" and part == 2):
                self.rich_log.write("[red]DISABLE")
                enabled = False
            elif (match[2] == "mul" and enabled):
                self.rich_log.write(f"[blue]Result += {match[3]} * {match[4]} = {int(match[3]) * int(match[4])}")
                result += int(match[3]) * int(match[4])
            self.progress.advance(1)
            self.digits.update(str(result))
        self.rich_log.write(f"[bold green]Done, Result:[/bold green] {result}")
