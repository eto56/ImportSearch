import argparse
from pathlib import Path

import importsearch

if __name__ == "__main__":
    args = argparse.Namespace(
        file_path=Path("target.py"),
        root_path=Path("."),
        output_format="print",
        output_path=Path("sample-output"),
        verbose=True,
    )
    instance = importsearch.importsearch(args)
    instance.search()
    instance.summary()
