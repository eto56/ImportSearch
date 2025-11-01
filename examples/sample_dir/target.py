from color.palette import describe_palette
from services.lighting import configure_lighting
import json


def main() -> str:
    colors = describe_palette()
    result = configure_lighting(colors)
    return json.dumps(result)


if __name__ == "__main__":
    print(main())
