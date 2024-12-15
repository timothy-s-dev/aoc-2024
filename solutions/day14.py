import re

from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox
import pyperclip

from solutions.base_solution import BaseSolution


number_regex = re.compile(r'(-?\d+)')


class Robot:
    def __init__(self, input):
        (
            self.pos_x,
            self.pos_y,
            self.vel_x,
            self.vel_y,
        ) = map(int, number_regex.findall(input))
    
    def get_position(self, steps, width, height):
        return (
            (self.pos_x + (self.vel_x * steps)) % width,
             (self.pos_y + (self.vel_y * steps)) % height,
        )

    def get_quadrant(self, steps, width, height):
        (x, y) = self.get_position(steps, width, height)
        if x < width // 2 and y < height // 2:
            return 0
        elif x > width // 2 and y < height // 2:
            return 1
        elif x < width // 2 and y > height // 2:
            return 2
        elif x > width // 2 and y > height // 2:
            return 3
        else:
            return None

class Day14(BaseSolution):
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

    def flood_count(self, start_x, start_y, positions):
        valid_positions = set(positions)
        frontier = [(start_x, start_y)]
        total = 0
        while frontier:
            (x, y) = frontier.pop()
            if (x, y) in valid_positions:
                total += 1
                valid_positions.remove((x, y))
                frontier.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
        return total

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part, test):
        lines = input_file.read().split('\n')
        steps = 100
        width = 11 if test else 101
        height = 7 if test else 103

        if part == 1:
            self.progress.update(total=len(lines), progress=0)
            robots = [0, 0, 0, 0]
            for line in lines:
                robot = Robot(line)
                quadrant = robot.get_quadrant(steps, width, height)
                if quadrant is not None:
                    robots[quadrant] += 1
                self.progress.advance(1)

            safety_factor = robots[0] * robots[1] * robots[2] * robots[3]
            self.digits.update(str(safety_factor))
            self.rich_log.write("[bold green]Safety Factor:[/bold green] " + str(safety_factor))
        else:
            max_search_time = 10_000
            self.progress.update(total=max_search_time, progress=0)
            robots = list(map(lambda line: Robot(line), lines))
            for steps in range(0, max_search_time):
                robots_by_row = [0 for _ in range(height)]
                positions = set()
                for robot in robots:
                    pos = robot.get_position(steps, width, height)
                    robots_by_row[pos[1]] += 1
                    positions.add(pos)

                largest_flood = 0
                for position in positions:
                    pattern_size = self.flood_count(position[0], position[1], positions)
                    largest_flood = max(largest_flood, pattern_size)

                if largest_flood > 50:
                    self.rich_log.write("Pattern found at step " + str(steps))
                    grid = [[(x, y) in positions for x in range(width)] for y in range(height)]
                    grid_chars = [['#' if x else '.' for x in row] for row in grid]
                    for row in grid_chars:
                        self.rich_log.write(''.join(row))
                self.progress.advance(1)


        
