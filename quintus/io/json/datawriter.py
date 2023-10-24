from quintus.io.datawriter import DataWriter
from quintus.structures import Component
from typing import Iterator
from pathlib import Path
import json


class JSONDataWriter(DataWriter):
    def __init__(
        self,
        file,
        override=True,
    ) -> None:
        self.file = Path(file)
        if self.file.exists() and override:
            with self.file.open("+w") as fp:
                fp.write("[]")

    def write_entry(self, entry: Component, filter: dict = None):
        content = list()
        if self.file.exists():
            with self.file.open() as fp:
                content = json.load(fp)
        new_content = json.loads(entry.json(exclude_unset=True, exclude_none=True))
        content.append(new_content)
        with self.file.open("+w") as fp:
            json.dump(content, fp)

    def get_entry(self, id: str) -> Iterator[dict]:
        with self.file.open() as fp:
            content = json.load(fp)
        return content.get("id")
