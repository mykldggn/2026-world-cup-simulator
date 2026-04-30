from dataclasses import dataclass
from typing import Dict, List


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

    def power_components(self) -> List[Dict[str, float]]:
        components = [
            {
                "key": "rankingAnchor",
                "label": "Ranking Anchor",
                "raw": self.ranking_anchor,
                "weight": 0.34,
                "contribution": round(self.ranking_anchor * 0.34, 2),
            },
            {
                "key": "rating",
                "label": "Squad Prior",
                "raw": self.rating,
                "weight": 0.10,
                "contribution": round(self.rating * 0.10, 2),
            },
            {
                "key": "attack",
                "label": "Attack",
                "raw": self.attack,
                "weight": 0.18,
                "contribution": round(self.attack * 0.18, 2),
            },
            {
                "key": "midfield",
                "label": "Midfield",
                "raw": self.midfield,
                "weight": 0.14,
                "contribution": round(self.midfield * 0.14, 2),
            },
            {
                "key": "defense",
                "label": "Defense",
                "raw": self.defense,
                "weight": 0.16,
                "contribution": round(self.defense * 0.16, 2),
            },
            {
                "key": "keeper",
                "label": "Keeper",
                "raw": self.keeper,
                "weight": 0.05,
                "contribution": round(self.keeper * 0.05, 2),
            },
            {
                "key": "form",
                "label": "Recent Form",
                "raw": self.form,
                "weight": 1.60,
                "contribution": round(self.form * 1.60, 2),
            },
        ]
        if self.host:
            components.append(
                {
                    "key": "host",
                    "label": "Host Boost",
                    "raw": 1.0,
                    "weight": 2.00,
                    "contribution": 2.0,
                }
            )
        total = max(sum(item["contribution"] for item in components), 0.01)
        for item in components:
            item["share"] = round(item["contribution"] / total, 4)
        return components

    def strengths(self) -> List[Dict[str, float]]:
        metrics = [
            {"label": "Attack", "value": self.attack},
            {"label": "Midfield", "value": self.midfield},
            {"label": "Defense", "value": self.defense},
            {"label": "Keeper", "value": self.keeper},
            {"label": "Ranking Anchor", "value": self.ranking_anchor},
            {"label": "Form", "value": round(70 + (self.form * 10), 2)},
        ]
        return sorted(metrics, key=lambda item: item["value"], reverse=True)[:3]

    def risks(self) -> List[Dict[str, float]]:
        metrics = [
            {"label": "Attack", "value": self.attack},
            {"label": "Midfield", "value": self.midfield},
            {"label": "Defense", "value": self.defense},
            {"label": "Keeper", "value": self.keeper},
            {"label": "Ranking Anchor", "value": self.ranking_anchor},
            {"label": "Form", "value": round(70 + (self.form * 10), 2)},
        ]
        return sorted(metrics, key=lambda item: item["value"])[:2]

    @property
    def ranking_anchor(self) -> float:
        return round(max(67.0, 96.0 - ((self.fifa_rank - 1) * 0.33)), 2)

    @property
    def power(self) -> float:
        return round(sum(item["contribution"] for item in self.power_components()), 2)

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
            "powerBreakdown": self.power_components(),
            "strengths": self.strengths(),
            "risks": self.risks(),
        }
