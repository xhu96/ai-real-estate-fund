from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .models import PropertyInput


def _coerce_value(value: str) -> str | int | float:
    value = value.strip()
    if value == "":
        return value
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_property(path: str | Path) -> PropertyInput:
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Property JSON must contain one object")
    return PropertyInput.from_dict(data)


def load_properties(path: str | Path) -> list[PropertyInput]:
    path = Path(path)
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return [PropertyInput.from_dict(data)]
        if isinstance(data, list):
            return [PropertyInput.from_dict(item) for item in data]
        raise ValueError("JSON must be an object or a list of objects")
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as fh:
            rows = csv.DictReader(fh)
            return [PropertyInput.from_dict({k: _coerce_value(v) for k, v in row.items()}) for row in rows]
    raise ValueError("Supported input formats: .json, .csv")


def write_json(path: str | Path, payload: object) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")


def iter_json_examples(paths: Iterable[str | Path]) -> list[PropertyInput]:
    properties: list[PropertyInput] = []
    for path in paths:
        properties.extend(load_properties(path))
    return properties
