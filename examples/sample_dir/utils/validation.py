def ensure_colors(colors: list[dict[str, str]]) -> None:
    if not colors:
        raise ValueError("colors list cannot be empty")
    for color in colors:
        if "name" not in color or "hex" not in color:
            raise ValueError(f"invalid color definition: {color}")
