from enum import Enum
import time
from itertools import combinations

from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox, Label
import pyperclip

from solutions.base_solution import BaseSolution


def inside_rect(position, width, height):
    return 0 <= position[0] < width and 0 <= position[1] < height

class Day08(BaseSolution):
    def __init__(self, rich_log: RichLog, progress: ProgressBar, *children: Widget):
        super().__init__(rich_log, progress, *children)
        self.digits = Digits(value='0', classes="results_digits top_margin_1")
        self.fast_forward = False
        self.grid_display = Label("...\n...\n...")

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

    def update_grid_display(self, width, height, antinodes, antenna_reverse_lookup):
        output = ""
        for y in range(0, height):
            for x in range(0, width):
                if (x, y) in antinodes:
                    output += "#"
                elif (x, y) in antenna_reverse_lookup.keys():
                    output += antenna_reverse_lookup[(x, y)]
                else:
                    output += "."
            output += "\n"
        self.grid_display.update(output)

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part):
        antennas = {}
        antenna_reverse_lookup = {}
        y = 0
        width = 0
        for line in input_file:
            width = len(line)
            x = 0
            for char in line.strip():
                if char == ".":
                    x += 1
                    continue
                if not char in antennas:
                    antennas[char] = []
                antennas[char].append((x, y))
                antenna_reverse_lookup[(x, y)] = char
                x += 1
            y += 1
        height = y

        self.rich_log.write(antennas)

        antenna_pairs = list(map(lambda a: (a, list(combinations(antennas[a], 2))), antennas.keys()))
        total_antenna_pairs = sum(len(x) for x in antenna_pairs)

        for pair in antenna_pairs:
            self.rich_log.write(f"{pair[0]}: {pair[1]}")

        self.progress.update(total=total_antenna_pairs, progress=0)
        antinodes = []
        for antenna_pairs_set in antenna_pairs:
            for antenna_pair in antenna_pairs_set[1]:
                x_offset = antenna_pair[0][0] - antenna_pair[1][0]
                y_offset = antenna_pair[0][1] - antenna_pair[1][1]
                first_position = (antenna_pair[0][0] + x_offset, antenna_pair[0][1] + y_offset)
                second_position = (antenna_pair[1][0] - x_offset, antenna_pair[1][1] - y_offset)

                added_antinode = False
                if inside_rect(first_position, width, height):
                    added_antinode = True
                    antinodes.append(first_position)
                if inside_rect(second_position, width, height):
                    added_antinode = True
                    antinodes.append(second_position)

                if added_antinode:
                    self.digits.update(str(len(list(set(antinodes)))))
                    self.update_grid_display(width, height, antinodes, antenna_reverse_lookup)
                    if not self.fast_forward:
                        time.sleep(0.05)
                self.progress.advance(1)

        self.rich_log.write(f"Antinodes: {antinodes}")
        self.rich_log.write(
            f"[bold green]Done, Result:[/bold green] {len(list(set(antinodes)))}"
        )
