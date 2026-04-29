from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Team:
    code: str
    name: str
    group: str
    confederation: str
    fifa_rank: int
    flag_code: str
    rating: float
    attack: float
    midfield: float
    defense: float
    keeper: float
    form: float
    style: str
    host: bool = False

    @property
    def ranking_anchor(self) -> float:
        return round(max(67.0, 96.0 - ((self.fifa_rank - 1) * 0.33)), 2)

    @property
    def power(self) -> float:
        return round(
            (self.ranking_anchor * 0.34)
            + (self.rating * 0.10)
            + (self.attack * 0.18)
            + (self.midfield * 0.14)
            + (self.defense * 0.16)
            + (self.keeper * 0.05)
            + (self.form * 1.6)
            + (2.0 if self.host else 0.0),
            2,
        )

    def to_summary(self) -> Dict[str, object]:
        return {
            "code": self.code,
            "name": self.name,
            "group": self.group,
            "confederation": self.confederation,
            "fifaRank": self.fifa_rank,
            "flagCode": self.flag_code,
            "rating": self.rating,
            "rankingAnchor": self.ranking_anchor,
            "attack": self.attack,
            "midfield": self.midfield,
            "defense": self.defense,
            "keeper": self.keeper,
            "form": self.form,
            "style": self.style,
            "host": self.host,
            "power": self.power,
        }
