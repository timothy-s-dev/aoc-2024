import importlib
from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalGroup, VerticalGroup, Center
from textual.widgets import Button, Footer, Header, ProgressBar, RichLog
import argparse
import pyperclip


parser = argparse.ArgumentParser(
    prog='AoC 2024',
    description='Runs solutions for Advent of Code 2024'
)
parser.add_argument('day', type=int, choices=range(1, 26))
parser.add_argument('part', type=int, choices=[1, 2])
parser.add_argument('-t', '--test', action='store_true',
                    help="Use to run on example/test file.")

args = parser.parse_args()

rich_log = RichLog(highlight=True, markup=True)
progress_bar = ProgressBar(id="main_progress_bar")
widget = None
file = None

class AoCApp(App):
    CSS = """
    .top_margin_1 {
        margin-top: 1;
    }
    .width_auto { 
        width: auto;
    }
    #main_progress_bar {
        margin-top: 1;
    }
    .results_digits {
        border: double green;
        width: auto;
    }
    """
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Horizontal():
            yield widget
            with VerticalGroup():
                with HorizontalGroup():
                    with Center():
                        yield progress_bar
                    yield Button("Run", id="run")
                yield rich_log

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run":
            widget.run(file, args.part)

if __name__ == "__main__":
    try:
        day_str = str(args.day).rjust(2, "0")
        module_name = f'solutions.day{day_str}'
        module = importlib.import_module(module_name)
        widget = getattr(module, f'Day{day_str}')(rich_log, progress_bar)
        if widget:
            input_file_name = f'inputs/day{day_str}{'-test' if args.test else ''}.txt'
            file = open(input_file_name, 'r')
    except ModuleNotFoundError:
        print(f'No implementation for day {args.day} found.')
    except OSError:
        print(f'Input file for day {args.day} {'(test) ' if args.test else ''}not found.')

    app = AoCApp()
    app.run()
