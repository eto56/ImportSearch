import utilities.formatters.json_formatter


def log(message: str) -> str:
    formatted = utilities.formatters.json_formatter.serialize(message)
    return formatted
