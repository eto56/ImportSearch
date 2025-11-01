from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Set, Any


def print_tree(
    import_tree: Mapping[Path, Iterable[Path]],
    node: Path,
    indent: str = "|-",
    visited: Set[Path] | None = None,
) -> None:
    coerced_tree = _coerce_tree(import_tree)
    normalized = edit_map(coerced_tree)
    if not normalized:
        return

    node_path = _as_path(node)
    seen: Set[Path] = visited if visited is not None else set()

    def _walk(current: Path, prefix: str) -> None:
        if current in seen:
            print(prefix + str(current))
            return
        seen.add(current)
        print(prefix + str(current))
        for child in normalized.get(current, []):
            _walk(child, "  " + prefix)

    _walk(node_path, indent)


def edit_map(tree: Mapping[Path, Iterable[Path]]) -> dict[Path, list[Path]]:
    normalized: dict[Path, list[Path]] = {
        key: list(children) for key, children in tree.items()
    }

    key_set = set(normalized.keys())
    for key, children in normalized.items():
        adjusted: list[Path] = []
        for child in children:
            candidate = _append_py_suffix(child)
            if child.suffix != ".py" and candidate in key_set:
                adjusted.append(candidate)
            else:
                adjusted.append(child)
        normalized[key] = adjusted
    return normalized


def _coerce_tree(tree: Mapping[Path, Iterable[Path]]) -> dict[Path, list[Path]]:
    return {
        _as_path(key): [_as_path(child) for child in children]
        for key, children in tree.items()
    }


def _append_py_suffix(path: Path) -> Path:
    if path.suffix == ".py":
        return path
    return path.with_name(path.name + ".py")


def _as_path(value: Any) -> Path:
    return value if isinstance(value, Path) else Path(value)
