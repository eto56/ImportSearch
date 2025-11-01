from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from textwrap import dedent

import pytest
from typer.testing import CliRunner

from importsearch.main import Dependency, importsearch
from importsearch.cli import import_search_app

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "dependency_demo"


def make_searcher(root_path: Path, filename: str) -> importsearch:
    args = Namespace(
        file_path=filename,
        root_path=root_path,
        output_format="text",
        output_path=root_path / "output",
        verbose=False,
    )
    return importsearch(args)


def dep_names(deps: list[Dependency]) -> list[str]:
    return [dep.name for dep in deps]


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def test_extract_imports_returns_dependency_names(tmp_path: Path) -> None:
    module = tmp_path / "sample.py"
    module.write_text(
        dedent(
            """
            import os
            import typing as t
            from pathlib import Path
            from package.sub import thing
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    searcher = make_searcher(tmp_path, "sample.py")
    imports = searcher.extract_imports(module)

    assert dep_names(imports) == ["os", "typing", "pathlib", "package.sub"]


def test_search_populates_dependency_graph_and_visited(tmp_path: Path) -> None:
    (tmp_path / "module_b.py").write_text("import json\n", encoding="utf-8")
    (tmp_path / "module_a.py").write_text("import module_b\n", encoding="utf-8")
    main_file = tmp_path / "main.py"
    main_file.write_text(
        dedent(
            """
            import module_a
            import json
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    searcher = make_searcher(tmp_path, "main.py")
    searcher.search()

    summary = searcher._normalize_summary_map(searcher.dependency_graph)

    assert summary["main.py"] == ["module_a.py", "json"]
    assert summary["module_a.py"] == ["module_b.py"]
    assert summary["module_b.py"] == ["json"]

    visited = {rel(path, tmp_path) for path in searcher.visited}
    assert {"main.py", "module_a.py", "module_b.py"} <= visited


def test_fixture_project_builds_expected_graph() -> None:
    searcher = make_searcher(FIXTURE_ROOT, "entry.py")
    searcher.search()

    summary = searcher._normalize_summary_map(searcher.dependency_graph)

    assert summary["entry.py"] == ["pkg/alpha.py", "utilities/logger.py"]
    assert summary["pkg/alpha.py"] == ["pkg/beta.py", "pkg/shared/helpers.py"]
    assert summary["pkg/beta.py"] == ["utilities/logger.py"]
    assert summary["utilities/logger.py"] == ["utilities/formatters/json_formatter.py"]
    assert summary["utilities/formatters/json_formatter.py"] == ["json"]

    visited = {rel(path, FIXTURE_ROOT) for path in searcher.visited}
    expected = {
        "entry.py",
        "pkg/alpha.py",
        "pkg/beta.py",
        "pkg/shared/helpers.py",
        "utilities/logger.py",
        "utilities/formatters/json_formatter.py",
    }
    assert expected <= visited


def test_relative_imports_are_resolved(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("from .module import do\n", encoding="utf-8")
    (pkg / "module.py").write_text("def do():\n    return 1\n", encoding="utf-8")
    main_file = tmp_path / "main.py"
    main_file.write_text("import pkg\n", encoding="utf-8")

    searcher = make_searcher(tmp_path, "main.py")
    searcher.search()

    summary = searcher._normalize_summary_map(searcher.dependency_graph)

    assert summary["main.py"] == ["pkg/__init__.py"]
    assert summary["pkg/__init__.py"] == ["pkg/module.py"]


def test_cli_text_output_generates_report(tmp_path: Path) -> None:
    (tmp_path / "module.py").write_text(
        "def run():\n    return 'ok'\n", encoding="utf-8"
    )
    main_file = tmp_path / "main.py"
    main_file.write_text("import module\n", encoding="utf-8")
    output_stub = tmp_path / "dependency_report"

    runner = CliRunner()
    result = runner.invoke(
        import_search_app,
        [
            str(main_file),
            "--root",
            str(tmp_path),
            "--output-format",
            "text",
            "--output-file",
            str(output_stub),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    output_file = output_stub.with_suffix(".txt")
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "File: main.py" in content
    assert "module.py" in content


def test_cli_accepts_file_relative_to_root(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("from .module import value\n", encoding="utf-8")
    (pkg / "module.py").write_text("value = 1\n", encoding="utf-8")

    root = tmp_path
    # note: relative file path with root option
    runner = CliRunner()
    result = runner.invoke(
        import_search_app,
        [
            "pkg/__init__.py",
            "--root",
            str(root),
            "--output-format",
            "json",
            "--output-file",
            str(root / "out"),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    content = (root / "out.json").read_text(encoding="utf-8")
    assert '"pkg/__init__.py"' in content


def test_cli_handles_paths_already_prefixed_with_root(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    entry = pkg / "entry.py"
    entry.write_text("import sys\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        import_search_app,
        [
            str(pkg / "entry.py"),
            "--root",
            str(tmp_path),
            "--output-format",
            "print",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
