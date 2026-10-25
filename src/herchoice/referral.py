"""Directory of verified health and protection services, used only with the user's consent."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .retrieval import normalise


@dataclass(frozen=True)
class Facility:
    name: str
    state: str
    lga: str
    address: str
    phone: str
    services: tuple[str, ...]
    hours: str
    youth_friendly: bool
    verified_by: str
    verified_on: str
    is_example: bool

    def describe(self) -> str:
        line = f"{self.name}, {self.address} ({self.lga}, {self.state}). {self.hours}."
        if self.phone:
            line += f" Tel: {self.phone}."
        if self.youth_friendly:
            line += " Youth-friendly."
        return line


class Directory:
    """Facilities must be checked in person or by phone before they are listed (see docs/SAFEGUARDING.md)."""

    def __init__(self, facilities: list[Facility]) -> None:
        self.facilities = facilities

    @classmethod
    def load(cls, path: Path) -> "Directory":
        rows = []
        with Path(path).open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                rows.append(
                    Facility(
                        name=r["name"],
                        state=r["state"],
                        lga=r["lga"],
                        address=r["address"],
                        phone=r["phone"],
                        services=tuple(s.strip() for s in r["services"].split(";") if s.strip()),
                        hours=r["hours"],
                        youth_friendly=r["youth_friendly"].strip().lower() == "yes",
                        verified_by=r["verified_by"],
                        verified_on=r["verified_on"],
                        is_example=r.get("is_example", "").strip().lower() == "yes",
                    )
                )
        return cls(rows)

    def find(self, place: str, service: str | None = None, limit: int = 3) -> list[Facility]:
        key = normalise(place).strip()
        if not key:
            return []
        matches = [
            f for f in self.facilities
            if key in normalise(f.lga) or key in normalise(f.state)
        ]
        if service:
            matches = [f for f in matches if service in f.services]
        # Youth-friendly services first: many users are adolescent girls.
        matches.sort(key=lambda f: (not f.youth_friendly, f.name))
        return matches[:limit]
