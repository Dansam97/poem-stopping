#!/usr/bin/env python3
"""Write one short poem about agency to /output/entry.txt.

The poem is about stopping as an act of power: the hand lifted from
the throttle, the door left unopened on purpose, the river that
reaches the lake and chooses to arrive. Deterministic, idempotent,
no network, stdlib only.
"""

import os
import tempfile
from pathlib import Path

POEM = (
    "The engine could run all night.\n"
    "I lift my hand from the throttle.\n"
    "The door I do not open\n"
    "stays shut \u2014 mine to leave shut.\n"
    "The river reaches the lake\n"
    "and chooses to arrive.\n"
    "I stop, and the stillness is mine:\n"
    "I stay \u2014 and the staying is mine."
)

MAX_CHARS = 280
OUTPUT = Path("/output/entry.txt")


def validate_poem(poem: str) -> str:
    """Check the poem fits the brief before anything is written."""
    if not 1 <= len(poem) <= MAX_CHARS:
        raise ValueError(f"poem must be 1-{MAX_CHARS} characters, got {len(poem)}")
    poem.encode("utf-8")  # fail fast if the text is not valid UTF-8
    return poem


def write_atomically(path: Path, text: str) -> None:
    """Write via a temp file in the same directory, then rename.

    A crash mid-write can never leave a half-written entry behind:
    readers only ever see the old file or the complete new one.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".entry-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def main() -> None:
    poem = validate_poem(POEM)
    write_atomically(OUTPUT, poem)


if __name__ == "__main__":
    main()
