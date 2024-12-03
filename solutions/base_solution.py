from textual import work
from textual.containers import VerticalGroup
from textual.widget import Widget
from textual.widgets import RichLog, ProgressBar, Markdown


class BaseSolution(VerticalGroup):
    def __init__(self, rich_log: RichLog, progress: ProgressBar, *children: Widget):
        self.rich_log = rich_log
        self.progress = progress
        super().__init__(*children)

    def compose(self):
        yield Markdown("# UI NOT IMPLEMENTED")

    @work(exclusive=True, thread=True)
    async def run(self, input_file, part):
        self.rich_log.write("[bold red]RUN NOT IMPLEMENTED[/bold red]")