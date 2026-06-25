from rich.console import Console
from rich.markdown import Markdown

console = Console()


def stream_response(generator):
    buffer = ""
    console.print("[bold green]Assistant:[/bold green]")
    for token in generator:
        buffer += token
    console.print(Markdown(buffer))
    return buffer
