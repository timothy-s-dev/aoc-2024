from enum import Enum
import time
from itertools import combinations

from textual import work
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Button, ProgressBar, RichLog, Digits, Checkbox, Label
import pyperclip

from solutions.base_solution import BaseSolution


class Block:
    def __init__(self, id, size, is_file):
        self.id = id
        self.size = size
        self.is_file = is_file

    def __str__(self):
        return self.size * (format(self.id, 'x') if self.is_file else '.')


def get_last_file_block_index(blocks):
    for i in range(len(blocks) - 1, -1, -1):
        if blocks[i].is_file:
            return i
        
def get_first_open_block_index(blocks, min_size):
    for i in range(0, len(blocks)):
        if not blocks[i].is_file and blocks[i].size >= min_size:
            return i


class Day09(BaseSolution):
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
        input = input_file.read().strip()
        blocks = []
        block_id = 0
        reading_file = True
        for c in input:
            blocks.append(Block(block_id if reading_file else -1, int(c), reading_file))
            if reading_file:
                block_id += 1
            reading_file = not reading_file

        if (len(blocks) < 30):
            fs_str = ''.join(map(lambda x: str(x), blocks))
            self.rich_log.write(fs_str)

        empty_space = sum(map(lambda x: x.size, filter(lambda x: not x.is_file, blocks)))
        self.progress.update(total=empty_space, progress=0)

        self.rich_log.write("Defragmenting")

        if part == 1:
            while True:
                last_file_block_index = get_last_file_block_index(blocks)
                first_open_block_index = get_first_open_block_index(blocks, 1)
                if first_open_block_index >= last_file_block_index:
                    break

                # Shrink the file and delete if size is 0
                current_block_id = blocks[last_file_block_index].id
                blocks[last_file_block_index].size -= 1
                if blocks[last_file_block_index].size == 0:
                    blocks.pop(last_file_block_index)

                # Add an empty block at the end or expand the existing one
                if blocks[-1].is_file:
                    blocks.append(Block(-1, 1, False))
                else:
                    blocks[-1].size += 1

                # Shrink the first open block and remove it if size is 0
                blocks[first_open_block_index].size -= 1
                if blocks[first_open_block_index].size == 0:
                    blocks.pop(first_open_block_index)

                # Insert the new file block or expand it if the previous block has the same id
                if blocks[first_open_block_index - 1].id == current_block_id:
                    blocks[first_open_block_index - 1].size += 1
                else:
                    blocks.insert(first_open_block_index, Block(current_block_id, 1, True))
        else:
            self.progress.update(total=block_id, progress=0)
            for i in range(block_id - 1, -1, -1):
                self.progress.advance(1)
                # Find file block to check, and first open space it will fit in
                file_block_index = next((index for index, block in enumerate(blocks) if block.id == i), None)
                file_block = blocks[file_block_index]
                open_block_index = get_first_open_block_index(blocks, file_block.size)

                # If there is no open space, or if the space is right of the file block, skip
                if open_block_index is None or open_block_index >= file_block_index:
                    continue

                blocks.pop(file_block_index)

                # Insert a non-file block where the file block used to be, and combine with any adjacent non-file blocks
                blocks.insert(file_block_index, Block(-1, file_block.size, False))
                if file_block_index > 0 and not blocks[file_block_index - 1].is_file:
                    blocks[file_block_index - 1].size += blocks[file_block_index].size
                    blocks.pop(file_block_index)
                    file_block_index -= 1
                if file_block_index < len(blocks) - 1 and not blocks[file_block_index + 1].is_file:
                    blocks[file_block_index + 1].size += blocks[file_block_index].size
                    blocks.pop(file_block_index)
                
                # If the empty space is the same size as the file, remove it, otherwise shrink it
                if (file_block.size == blocks[open_block_index].size):
                    blocks.pop(open_block_index)
                else:
                    blocks[open_block_index].size -= file_block.size

                # Insert the file block where the open space was
                blocks.insert(open_block_index, Block(file_block.id, file_block.size, True))

                if (len(blocks) < 30):
                    fs_str = ''.join(map(lambda x: str(x), blocks))
                    self.rich_log.write(fs_str)

        if (len(blocks) < 30):
            fs_str = ''.join(map(lambda x: str(x), blocks))
            self.rich_log.write(fs_str)

        self.rich_log.write("Done defragmenting, calculating checksum")

        checksum = 0
        position = 0
        for block in blocks:
            if block.is_file:
                for i in range(0, block.size):
                    checksum += position * block.id
                    position += 1
                    self.digits.update(str(checksum))
            else:
                position += block.size
        self.rich_log.write(f"Result: {checksum}")
