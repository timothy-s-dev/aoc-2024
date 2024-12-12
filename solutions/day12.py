from enum import Enum
import time
from itertools import combinations
from collections import namedtuple

from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox, Label
import pyperclip

from solutions.base_solution import BaseSolution


Coord = namedtuple('Coord', ['row', 'col'])
Edge = namedtuple('Edge', ['coord', 'side'])

class Side(Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3

def get_adjacent(coord):
    x, y = coord
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

def is_available(processed, coord):
    x, y = coord
    return 0 <= x < len(processed[0]) and 0 <= y < len(processed) and not processed[x][y]

def get_edges(region):
    edges = []
    for coord in region:
        if (coord[0] - 1, coord[1]) not in region:
            edges.append(Edge(coord, Side.TOP))
        if (coord[0] + 1, coord[1]) not in region:
            edges.append(Edge(coord, Side.BOTTOM))
        if (coord[0], coord[1] - 1) not in region:
            edges.append(Edge(coord, Side.LEFT))
        if (coord[0], coord[1] + 1) not in region:
            edges.append(Edge(coord, Side.RIGHT))
    return edges

def calculate_perimeter(region):
    return len(get_edges(region))

class Day12(BaseSolution):
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

    def count_sides(self, region):
        edges = get_edges(region)
        sides = 0
        for edge in edges:
            if edge.side == Side.TOP or edge.side == Side.BOTTOM:
                left = (edge.coord[0], edge.coord[1] - 1)
                if (left, edge.side) not in edges:
                    sides += 1
            if edge.side == Side.LEFT or edge.side == Side.RIGHT:
                top = (edge.coord[0] - 1, edge.coord[1])
                if (top, edge.side) not in edges:
                    sides += 1
        return sides

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part):
        grid = [list(line.strip()) for line in input_file.readlines()]
        processed = [[False for _ in row] for row in grid]
        regions = []
        self.progress.update(total=len(grid) * len(grid[0]), progress=0)
        for row in range(0, len(grid)):
            for col in range(0, len(grid[row])):
                if not processed[row][col]:
                    regions.append(self.find_region(grid, processed, row, col))
                self.progress.advance(1)

        result = 0
        for region in regions:
            root = next(iter(region))
            region_id = grid[root[0]][root[1]]
            size = len(region)
            mult = calculate_perimeter(region) if part == 1 else self.count_sides(region)
            cost = size * mult
            self.rich_log.write(f"Region {region_id} will cost {size} x {mult} = {cost}")
            result += cost
            self.digits.update(str(result))

    def find_region(self, grid, processed, row, col):
        region = set([(row, col)])
        processed[row][col] = True
        frontier = get_adjacent((row, col))
        while len(frontier) > 0:
            next = frontier.pop()

            if not is_available(processed, next):
                continue
            if grid[next[0]][next[1]] != grid[row][col]:
                continue

            processed[next[0]][next[1]] = True
            region.add(next)
            frontier.extend(get_adjacent(next))
        return region
        
