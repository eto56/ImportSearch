import io
import ast
import argparse
from contextlib import redirect_stdout
from dataclasses import dataclass
from importlib.util import resolve_name
from pathlib import Path
from typing import Iterable, Mapping
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from importsearch.tree import print_tree


@dataclass(frozen=True)
class Dependency:
    """Light wrapper to distinguish unresolved modules from concrete files."""

    target: Path | None
    name: str

    @classmethod
    def from_path(cls, path: Path, root: Path) -> "Dependency":
        absolute = path.resolve()
        rel = _relativize(absolute, root)
        return cls(absolute, rel)

    @classmethod
    def unresolved(cls, module: str) -> "Dependency":
        return cls(None, module)

    @property
    def is_path(self) -> bool:
        return self.target is not None


class importsearch:
    def __init__(self, args: argparse.Namespace) -> None:
        if args is None:
            raise ValueError("Arguments are required")

        self.verbose: bool = bool(getattr(args, "verbose", False))
        raw_root = getattr(args, "root_path", Path("."))
        raw_file = getattr(args, "file_path", Path("main.py"))
        raw_output = getattr(args, "output_path", Path("output"))

        self.root_path: Path = Path(raw_root).expanduser().resolve()
        self.target_file: Path = self._coerce_target(raw_file)
        self.output_format: str = getattr(args, "output_format", "text")
        self.output_path: Path = Path(raw_output)

        self.visited: set[Path] = set()
        self.dependency_graph: dict[Path, list[Dependency]] = {}
        self.console = Console()

    def _coerce_target(self, candidate: Path | str) -> Path:
        path = Path(candidate)
        if not path.is_absolute():
            path = self.root_path / path
        if path.is_dir():
            candidate_path = path / "__init__.py"
            if candidate_path.exists():
                return candidate_path
        if path.suffix != ".py":
            path = path.with_suffix(".py")
        return path

    def search(self, file_path: Path | None = None) -> None:
        start = self._coerce_target(file_path or self.target_file)
        self._visit(start)

    def _visit(self, file_path: Path) -> None:
        file_path = file_path.resolve()
        if file_path in self.visited:
            return
        if not file_path.exists():
            if self.verbose:
                self.console.log(f"[importsearch] skipping missing file: {file_path}")
            return

        self.visited.add(file_path)
        dependencies = self.extract_imports(file_path)
        if dependencies:
            self.dependency_graph[file_path] = dependencies

        for dep in dependencies:
            if dep.target:
                self._visit(dep.target)

    def extract_imports(self, filename: Path) -> list[Dependency]:
        """Parse the target file and resolve its import statements."""
        try:
            source = filename.read_text(encoding="utf-8")
        except FileNotFoundError:
            if self.verbose:
                self.console.log(f"[importsearch] file not found: {filename}")
            return []

        tree = ast.parse(source, str(filename))
        dependencies: list[Dependency] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    resolved = self._resolve_absolute(alias.name)
                    dependencies.append(resolved)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        resolved = self._resolve_from(
                            current=filename,
                            module=node.module,
                            level=node.level,
                            target_name=None,
                        )
                        dependencies.append(resolved)
                    else:
                        resolved = self._resolve_from(
                            current=filename,
                            module=node.module,
                            level=node.level,
                            target_name=alias.name,
                        )
                        dependencies.append(resolved)
        return dependencies

    def _resolve_absolute(self, module_path: str) -> Dependency:
        resolved = self._resolve_module(module_path)
        if resolved:
            return Dependency.from_path(resolved, self.root_path)
        return Dependency.unresolved(module_path)

    def _resolve_from(
        self,
        current: Path,
        module: str | None,
        level: int,
        target_name: str | None,
    ) -> Dependency:
        package = self._module_name(current)
        leading = "." * level
        base = module or ""

        candidates: list[str] = []

        if target_name is None:
            candidate = leading + base if base else leading or "."
            candidates.append(candidate)
        else:
            qualified = ".".join(filter(None, [base, target_name]))
            candidate = (leading + qualified) if (leading or base) else target_name
            candidates.append(candidate)
            if base:
                base_candidate = leading + base if leading else base
                candidates.append(base_candidate)

        for candidate in candidates:
            resolved_name = self._resolve_relative_name(candidate, package)
            if not resolved_name:
                continue
            resolved_path = self._resolve_module(resolved_name)
            if resolved_path:
                return Dependency.from_path(resolved_path, self.root_path)

        fallback = candidates[-1] if candidates else ""
        display = fallback.lstrip(".")
        if not display:
            display = package or fallback.strip(".")
        return Dependency.unresolved(display or target_name or base or "")

    def _resolve_module(self, module_path: str) -> Path | None:
        pieces = module_path.split(".")
        candidate = self.root_path.joinpath(*pieces).with_suffix(".py")
        if candidate.exists():
            return candidate.resolve()
        package_init = self.root_path.joinpath(*pieces, "__init__.py")
        if package_init.exists():
            return package_init.resolve()
        return None

    def _module_parts(self, path: Path) -> list[str]:
        try:
            rel = path.resolve().relative_to(self.root_path)
        except ValueError:
            rel = path.resolve()
        stripped = rel.with_suffix("")
        parts = list(stripped.parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        return parts

    def _module_name(self, path: Path) -> str:
        parts = self._module_parts(path)
        return ".".join(parts)

    def _resolve_relative_name(self, name: str, package: str) -> str | None:
        candidate = name.strip()

        if not candidate:
            return package or None

        if candidate.startswith("."):
            if not package:
                return None
            try:
                return resolve_name(candidate, package)
            except (ImportError, ValueError):
                return None

        return candidate

    def summary(self) -> None:
        summary_map = self._normalize_summary_map(self.dependency_graph)

        if self.output_format == "print":
            self._print_summary(summary_map)
        elif self.output_format == "text":
            output = self._txt_summary(summary_map)
            self._write_output(output, suffix="txt")
        elif self.output_format == "json":
            self._write_output(self._json_summary(summary_map), suffix="json")
        else:
            raise ValueError(
                f"Unknown output format: {self.output_format}. use print, text or json instead."
            )

    def _write_output(self, content: str, *, suffix: str) -> None:
        print(content)
        output_file = self.output_path.with_suffix(f".{suffix}")
        try:
            output_file.write_text(content, encoding="utf-8")
            if self.verbose:
                self.console.log(f"[importsearch] summary written to {output_file}")
        except OSError as exc:
            print(f"Error writing to {output_file}: {exc}")

    def _txt_summary(self, summary_map: Mapping[str, list[str]]) -> str:
        lines: list[str] = []
        for key in summary_map:
            lines.append(f"\nFile: {key}\n")
            lines.append(str(summary_map[key]) + "\n")
            lines.append("-----------------------\n")
        visited = sorted(_relativize(p, self.root_path) for p in self.visited)
        lines.append("\nVisited files: " + str(visited) + "\n")
        lines.append("-----------------------\n")
        lines.append("import-tree\n\n")
        return "".join(lines)

    def _json_summary(self, summary_map: Mapping[str, list[str]]) -> str:
        import json

        payload = {
            "summary": summary_map,
            "visited": sorted(_relativize(p, self.root_path) for p in self.visited),
        }
        return json.dumps(payload, indent=2)

    def _print_summary(self, summary_map: Mapping[str, list[str]]) -> None:
        table = Table(
            title="Import Summary",
            box=box.ROUNDED,
            show_lines=True,
            header_style="bold white",
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Dependencies", style="magenta")
        for key, values in summary_map.items():
            dependency_block = Text(
                "\n".join(values) if values else "None",
                style="magenta" if values else "dim",
            )
            table.add_row(Text(key, style="cyan"), dependency_block)

        self.console.print(table)

        visited = sorted(_relativize(p, self.root_path) for p in self.visited)
        visited_text = Text(
            "\n".join(visited) if visited else "None",
            style="green" if visited else "dim",
        )
        self.console.print(
            Panel(
                visited_text, title="Visited Files", border_style="green", expand=False
            )
        )

        self.console.rule("Import Tree")
        tree_map: dict[Path, list[Path]] = {
            Path(_relativize(key, self.root_path)): [
                Path(dep.name) for dep in dependencies if dep.target
            ]
            for key, dependencies in self.dependency_graph.items()
        }
        tree_root = Path(_relativize(self.target_file, self.root_path))
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            print_tree(tree_map, tree_root)
        tree_output = buffer.getvalue().strip()
        if tree_output:
            self.console.print(tree_output)
        else:
            self.console.print("[dim]No import tree to display[/dim]")

    def _normalize_summary_map(
        self, graph: Mapping[Path, Iterable[Dependency]]
    ) -> dict[str, list[str]]:
        normalized: dict[str, list[str]] = {}
        for key, dependencies in graph.items():
            normalized[str(_relativize(key, self.root_path))] = [
                dep.name for dep in dependencies
            ]
        return normalized


def _relativize(path: Path, root: Path) -> str:
    try:
        rel = path.relative_to(root)
        return rel.as_posix()
    except ValueError:
        return path.as_posix()
