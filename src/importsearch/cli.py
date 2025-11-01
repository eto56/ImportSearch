import argparse
from pathlib import Path

import typer
from typing_extensions import Annotated

from .main import importsearch

import_search_app = typer.Typer(
    help="Import Search -- A tool to analyze Python import dependencies."
)


@import_search_app.command()
def main(
    file_path: Annotated[
        Path,
        typer.Argument(help="The target Python file to analyze"),
    ],
    root_path: Annotated[
        Path | None,
        typer.Option("--root", "-r", help="The root directory to search for imports"),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option(
            "--output-format", "-o", help="Output format: print, text or json"
        ),
    ] = "print",
    output_path: Annotated[
        Path | None,
        typer.Option("--output-file", "-of", help="File to write the output to"),
    ] = Path("output"),
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
):
    from pathlib import Path

    if root_path is None:
        root_path = Path.cwd()

    args = argparse.Namespace(
        file_path=file_path,
        root_path=root_path,
        output_format=output_format,
        output_path=output_path,
        verbose=verbose,
    )
    print_args(args)

    search = importsearch(args)
    search.search(file_path)
    search.summary()


def print_args(args: argparse.Namespace) -> None:
    print("Arguments:")
    for arg, value in vars(args).items():
        print(f"  {arg}: {value}")
