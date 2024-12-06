from functools import cmp_to_key
import time
from textual import work
from textual.containers import Center, Middle, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox
import re
import pyperclip

from solutions.base_solution import BaseSolution


order_regex = re.compile(r"(\d{2})\|(\d{2})")

class Day05(BaseSolution):
    def __init__(self, rich_log: RichLog, progress: ProgressBar, *children: Widget):
        super().__init__(rich_log, progress, *children)
        self.digits = Digits(value='0', classes="results_digits top_margin_1")
        self.fast_forward = False

    def compose(self):
         with VerticalGroup():
                with Center():
                    with HorizontalGroup(classes="top_margin_1 width_auto"):
                        yield Button("Copy", id="copy")
                        yield Checkbox(label="Fast Forward")
                with Center():
                    yield self.digits

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "copy":
            pyperclip.copy(self.digits.value)

    def on_checkbox_changed(self, event: Checkbox.Changed):
        self.fast_forward = event.checkbox.value

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part):
        unique_pages = set()
        ordering_rules = {}
        updates = []

        self.rich_log.write("Loading input...")
        reading_ordering_rules = True
        for line in input_file:
            if line.strip() == "":
                reading_ordering_rules = False
            elif reading_ordering_rules:
                first, second = [int(x) for x in line.split('|')]
                unique_pages.add(first)
                unique_pages.add(second)
                if first not in ordering_rules:
                    ordering_rules[first] = []
                ordering_rules[first].append(second)
            else:
                updates.append([int(x) for x in line.split(',')])

        for page in unique_pages:
            if page not in ordering_rules:
                ordering_rules[page] = []

        def compare_page(a, b):
            if b in ordering_rules[a]:
                return -1
            elif a in ordering_rules[b]:
                return 1
            return 0
        
        self.rich_log.write(f"Processing {len(updates)} updates...")
        self.progress.update(total=len(updates), progress=0)
        result = 0
        update_index = 0
        for update in updates:
            sorted_update = sorted(update, key=cmp_to_key(compare_page))
            if (update == sorted_update):
                self.rich_log.write(f"[green]{update} == {sorted_update}")
            else:
                self.rich_log.write(f"[red]{update} != {sorted_update}")
            if (part == 1 and update == sorted_update) or (part == 2 and update != sorted_update):
                middle_value = sorted_update[len(sorted_update) // 2]
                result += middle_value
                self.digits.update(str(result))
                if not self.fast_forward:
                    time.sleep(0.05)
            self.progress.advance(1)
            update_index += 1

        self.rich_log.write(f"[bold green]Done, Result:[/bold green] {result}")
