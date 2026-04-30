from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .data import SCENARIO_PRESETS, group_teams, load_teams
from .models import Team


GROUP_FIXTURES: Sequence[Tuple[int, int]] = (
    (0, 1),
    (2, 3),
    (0, 2),
    (1, 3),
    (0, 3),
    (1, 2),
)

ROUND_OF_32_BLUEPRINT = (
    {"id": "R32-1", "home": ("runner_up", "A"), "away": ("runner_up", "B")},
    {"id": "R32-2", "home": ("winner", "E"), "away": ("third", "slot1")},
    {"id": "R32-3", "home": ("winner", "F"), "away": ("runner_up", "C")},
    {"id": "R32-4", "home": ("winner", "C"), "away": ("runner_up", "F")},
    {"id": "R32-5", "home": ("winner", "I"), "away": ("third", "slot2")},
    {"id": "R32-6", "home": ("runner_up", "E"), "away": ("runner_up", "I")},
    {"id": "R32-7", "home": ("winner", "A"), "away": ("third", "slot3")},
    {"id": "R32-8", "home": ("winner", "L"), "away": ("third", "slot4")},
    {"id": "R32-9", "home": ("winner", "D"), "away": ("third", "slot5")},
    {"id": "R32-10", "home": ("winner", "G"), "away": ("third", "slot6")},
    {"id": "R32-11", "home": ("winner", "K"), "away": ("runner_up", "J")},
    {"id": "R32-12", "home": ("winner", "J"), "away": ("runner_up", "K")},
    {"id": "R32-13", "home": ("winner", "H"), "away": ("third", "slot7")},
    {"id": "R32-14", "home": ("winner", "B"), "away": ("third", "slot8")},
    {"id": "R32-15", "home": ("runner_up", "D"), "away": ("runner_up", "G")},
    {"id": "R32-16", "home": ("runner_up", "H"), "away": ("runner_up", "L")},
)

THIRD_SLOT_RULES = (
    ("slot1", "E"),
    ("slot2", "I"),
    ("slot3", "A"),
    ("slot4", "L"),
    ("slot5", "D"),
    ("slot6", "G"),
    ("slot7", "H"),
    ("slot8", "B"),
)

STAGE_DISPLAY = {
    "round_of_32": "Round of 32",
    "round_of_16": "Round of 16",
    "quarterfinal": "Quarterfinal",
    "semifinal": "Semifinal",
    "final": "Final",
    "champion": "Champion",
}

ROUND_STAGE_KEYS = {
    "Round of 32": "round_of_32",
    "Round of 16": "round_of_16",
    "Quarterfinals": "quarterfinal",
    "Semifinals": "semifinal",
    "Final": "final",
}

HOST_COUNTRIES = {
    "USA": "United States",
    "MEX": "Mexico",
    "CAN": "Canada",
}

GROUP_VENUES = {
    "A": {"city": "Mexico City", "country": "Mexico", "countryCode": "mx", "climate": "high-altitude", "altitudeM": 2240},
    "B": {"city": "Guadalajara", "country": "Mexico", "countryCode": "mx", "climate": "warm", "altitudeM": 1566},
    "C": {"city": "Vancouver", "country": "Canada", "countryCode": "ca", "climate": "cool", "altitudeM": 70},
    "D": {"city": "Los Angeles", "country": "United States", "countryCode": "us", "climate": "warm", "altitudeM": 93},
    "E": {"city": "Dallas", "country": "United States", "countryCode": "us", "climate": "hot", "altitudeM": 131},
    "F": {"city": "Toronto", "country": "Canada", "countryCode": "ca", "climate": "cool", "altitudeM": 76},
    "G": {"city": "Atlanta", "country": "United States", "countryCode": "us", "climate": "humid", "altitudeM": 320},
    "H": {"city": "Monterrey", "country": "Mexico", "countryCode": "mx", "climate": "hot", "altitudeM": 540},
    "I": {"city": "Kansas City", "country": "United States", "countryCode": "us", "climate": "continental", "altitudeM": 277},
    "J": {"city": "Miami", "country": "United States", "countryCode": "us", "climate": "humid", "altitudeM": 2},
    "K": {"city": "Seattle", "country": "United States", "countryCode": "us", "climate": "mild", "altitudeM": 52},
    "L": {"city": "Boston", "country": "United States", "countryCode": "us", "climate": "cool", "altitudeM": 43},
}

KNOCKOUT_VENUES = {
    "Round of 32": [
        {"city": "Houston", "country": "United States", "countryCode": "us", "climate": "humid", "altitudeM": 13},
        {"city": "Philadelphia", "country": "United States", "countryCode": "us", "climate": "temperate", "altitudeM": 12},
        {"city": "San Francisco Bay Area", "country": "United States", "countryCode": "us", "climate": "mild", "altitudeM": 16},
        {"city": "Mexico City", "country": "Mexico", "countryCode": "mx", "climate": "high-altitude", "altitudeM": 2240},
        {"city": "Guadalajara", "country": "Mexico", "countryCode": "mx", "climate": "warm", "altitudeM": 1566},
        {"city": "Toronto", "country": "Canada", "countryCode": "ca", "climate": "cool", "altitudeM": 76},
        {"city": "Dallas", "country": "United States", "countryCode": "us", "climate": "hot", "altitudeM": 131},
        {"city": "Atlanta", "country": "United States", "countryCode": "us", "climate": "humid", "altitudeM": 320},
        {"city": "Los Angeles", "country": "United States", "countryCode": "us", "climate": "warm", "altitudeM": 93},
        {"city": "Monterrey", "country": "Mexico", "countryCode": "mx", "climate": "hot", "altitudeM": 540},
        {"city": "Kansas City", "country": "United States", "countryCode": "us", "climate": "continental", "altitudeM": 277},
        {"city": "Miami", "country": "United States", "countryCode": "us", "climate": "humid", "altitudeM": 2},
        {"city": "Seattle", "country": "United States", "countryCode": "us", "climate": "mild", "altitudeM": 52},
        {"city": "Boston", "country": "United States", "countryCode": "us", "climate": "cool", "altitudeM": 43},
        {"city": "Vancouver", "country": "Canada", "countryCode": "ca", "climate": "cool", "altitudeM": 70},
        {"city": "New York / New Jersey", "country": "United States", "countryCode": "us", "climate": "temperate", "altitudeM": 7},
    ],
    "Round of 16": [
        {"city": "Los Angeles", "country": "United States", "countryCode": "us", "climate": "warm", "altitudeM": 93},
        {"city": "Dallas", "country": "United States", "countryCode": "us", "climate": "hot", "altitudeM": 131},
        {"city": "Toronto", "country": "Canada", "countryCode": "ca", "climate": "cool", "altitudeM": 76},
        {"city": "Mexico City", "country": "Mexico", "countryCode": "mx", "climate": "high-altitude", "altitudeM": 2240},
        {"city": "Atlanta", "country": "United States", "countryCode": "us", "climate": "humid", "altitudeM": 320},
        {"city": "Miami", "country": "United States", "countryCode": "us", "climate": "humid", "altitudeM": 2},
        {"city": "Seattle", "country": "United States", "countryCode": "us", "climate": "mild", "altitudeM": 52},
        {"city": "New York / New Jersey", "country": "United States", "countryCode": "us", "climate": "temperate", "altitudeM": 7},
    ],
    "Quarterfinals": [
        {"city": "Toronto", "country": "Canada", "countryCode": "ca", "climate": "cool", "altitudeM": 76},
        {"city": "Mexico City", "country": "Mexico", "countryCode": "mx", "climate": "high-altitude", "altitudeM": 2240},
        {"city": "Miami", "country": "United States", "countryCode": "us", "climate": "humid", "altitudeM": 2},
        {"city": "Seattle", "country": "United States", "countryCode": "us", "climate": "mild", "altitudeM": 52},
    ],
    "Semifinals": [
        {"city": "Dallas", "country": "United States", "countryCode": "us", "climate": "hot", "altitudeM": 131},
        {"city": "Los Angeles", "country": "United States", "countryCode": "us", "climate": "warm", "altitudeM": 93},
    ],
    "Final": [
        {"city": "New York / New Jersey", "country": "United States", "countryCode": "us", "climate": "temperate", "altitudeM": 7},
    ],
}

TRAVEL_LOAD_BY_CONFED = {
    "Concacaf": 0.015,
    "CONMEBOL": 0.035,
    "UEFA": 0.055,
    "CAF": 0.050,
    "AFC": 0.065,
    "OFC": 0.070,
}

COOL_WEATHER_CODES = {"CAN", "NZL", "NOR", "SWE", "SCO", "ENG"}
ALTITUDE_READY_CODES = {"MEX", "COL", "ECU"}


def clamp(low: float, value: float, high: float) -> float:
    return max(low, min(high, value))


def logistic(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def poisson_sample(expected: float, rng: random.Random) -> int:
    limit = math.exp(-expected)
    product = 1.0
    goals = 0
    while product > limit:
        goals += 1
        product *= rng.random()
    return goals - 1


class WorldCupSimulator:
    def __init__(self, teams: Optional[List[Team]] = None) -> None:
        self.teams = teams or load_teams()
        self.team_lookup = {team.code: team for team in self.teams}
        self.groups = group_teams(self.teams)

    def simulate(
        self,
        iterations: int = 400,
        scenario: str = "balanced",
        host_advantage: bool = True,
        featured_team: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, object]:
        iterations = max(50, min(3000, int(iterations)))
        scenario_key = scenario if scenario in SCENARIO_PRESETS else "balanced"
        scenario_config = SCENARIO_PRESETS[scenario_key]
        featured_code = featured_team if featured_team in self.team_lookup else None
        seed_value = seed if seed is not None else 20260611
        rng = random.Random(seed_value)

        champion_counts: Counter[str] = Counter()
        finalists: Counter[str] = Counter()
        stage_counts: Dict[str, Counter[str]] = {
            team.code: Counter() for team in self.teams
        }
        group_position_counts: Dict[str, Dict[str, Counter[int]]] = {
            group_name: {team.code: Counter() for team in teams}
            for group_name, teams in self.groups.items()
        }
        advance_counts: Counter[str] = Counter()
        avg_points_tracker: Dict[str, List[int]] = {team.code: [] for team in self.teams}
        avg_goals_for_tracker: Dict[str, List[int]] = {team.code: [] for team in self.teams}
        avg_goals_against_tracker: Dict[str, List[int]] = {team.code: [] for team in self.teams}
        expected_finish_sum: Dict[str, float] = defaultdict(float)
        avg_travel_load_tracker: Dict[str, List[float]] = {team.code: [] for team in self.teams}
        avg_venue_edge_tracker: Dict[str, List[float]] = {team.code: [] for team in self.teams}
        stage_opponent_counts: Dict[str, Dict[str, Counter[str]]] = {
            team.code: {key: Counter() for key in STAGE_DISPLAY}
            for team in self.teams
        }
        group_pattern_counts: Dict[str, Counter[Tuple[str, ...]]] = {
            group_name: Counter() for group_name in self.groups
        }
        upset_signature_counts: Counter[Tuple[str, str, str]] = Counter()
        total_goals = 0
        total_matches = 0
        upset_count = 0
        final_pairings: Counter[Tuple[str, str]] = Counter()
        sample_run: Optional[Dict[str, object]] = None

        for _ in range(iterations):
            run = self._simulate_single_tournament(
                rng=rng,
                scenario_config=scenario_config,
                host_advantage=host_advantage,
            )

            if sample_run is None:
                sample_run = run

            champion_counts[run["champion"]] += 1
            finalists[run["champion"]] += 1
            finalists[run["runner_up"]] += 1
            final_pair = tuple(sorted((run["champion"], run["runner_up"])))
            final_pairings[final_pair] += 1
            total_goals += int(run["stats"]["goals"])
            total_matches += int(run["stats"]["matches"])
            upset_count += int(run["stats"]["upsets"])

            for code in run["qualified_codes"]:
                advance_counts[code] += 1
            for code, stage_labels in run["stage_reached"].items():
                for label in stage_labels:
                    stage_counts[code][label] += 1
            for group in run["groups"]:
                group_name = str(group["group"])
                group_pattern_counts[group_name][
                    tuple(row["code"] for row in group["standings"])
                ] += 1
                for position, row in enumerate(group["standings"], start=1):
                    code = str(row["code"])
                    group_position_counts[group_name][code][position] += 1
                    avg_points_tracker[code].append(int(row["points"]))
                    avg_goals_for_tracker[code].append(int(row["gf"]))
                    avg_goals_against_tracker[code].append(int(row["ga"]))
                    expected_finish_sum[code] += position
            for match in run["allMatches"]:
                home_code = str(match["homeCode"])
                away_code = str(match["awayCode"])
                avg_travel_load_tracker[home_code].append(
                    float(match["venueAdjustments"]["home"]["travelLoad"])
                )
                avg_travel_load_tracker[away_code].append(
                    float(match["venueAdjustments"]["away"]["travelLoad"])
                )
                avg_venue_edge_tracker[home_code].append(
                    float(match["venueAdjustments"]["home"]["total"])
                )
                avg_venue_edge_tracker[away_code].append(
                    float(match["venueAdjustments"]["away"]["total"])
                )
                if int(match["upset"]) and match["winner"]:
                    loser_code = away_code if str(match["winner"]) == home_code else home_code
                    upset_signature_counts[
                        (str(match["winner"]), loser_code, str(match["stageDisplay"]))
                    ] += 1
            for round_payload in run["rounds"]:
                stage_key = str(round_payload["stageKey"])
                for match in round_payload["matches"]:
                    home_code = str(match["homeCode"])
                    away_code = str(match["awayCode"])
                    stage_opponent_counts[home_code][stage_key][away_code] += 1
                    stage_opponent_counts[away_code][stage_key][home_code] += 1

        assert sample_run is not None

        champion_odds = []
        team_stage_rows = []
        team_rows_by_code: Dict[str, Dict[str, object]] = {}
        for team in sorted(
            self.teams,
            key=lambda item: (-champion_counts[item.code], -item.power, item.name),
        ):
            champion_probability = champion_counts[team.code] / iterations
            final_probability = finalists[team.code] / iterations
            round_of_32_probability = stage_counts[team.code]["round_of_32"] / iterations
            round_of_16_probability = stage_counts[team.code]["round_of_16"] / iterations
            quarterfinal_probability = stage_counts[team.code]["quarterfinal"] / iterations
            semifinal_probability = stage_counts[team.code]["semifinal"] / iterations
            expected_finish = expected_finish_sum[team.code] / iterations
            position_counts = group_position_counts[team.group][team.code]
            most_likely_finish = position_counts.most_common(1)[0][0]
            avg_goals_for = sum(avg_goals_for_tracker[team.code]) / iterations
            avg_goals_against = sum(avg_goals_against_tracker[team.code]) / iterations
            avg_travel_load = sum(avg_travel_load_tracker[team.code]) / max(
                len(avg_travel_load_tracker[team.code]), 1
            )
            avg_venue_edge = sum(avg_venue_edge_tracker[team.code]) / max(
                len(avg_venue_edge_tracker[team.code]), 1
            )
            team_row = {
                "code": team.code,
                "name": team.name,
                "group": team.group,
                "confederation": team.confederation,
                "fifaRank": team.fifa_rank,
                "flagCode": team.flag_code,
                "power": team.power,
                "rankingAnchor": team.ranking_anchor,
                "style": team.style,
                "championProbability": round(champion_probability, 4),
                "finalProbability": round(final_probability, 4),
                "advanceProbability": round(advance_counts[team.code] / iterations, 4),
                "roundOf32Probability": round(round_of_32_probability, 4),
                "roundOf16Probability": round(round_of_16_probability, 4),
                "quarterfinalProbability": round(quarterfinal_probability, 4),
                "semifinalProbability": round(semifinal_probability, 4),
                "avgGroupPoints": round(sum(avg_points_tracker[team.code]) / iterations, 2),
                "avgGoalsFor": round(avg_goals_for, 2),
                "avgGoalsAgainst": round(avg_goals_against, 2),
                "expectedFinish": round(expected_finish, 2),
                "mostLikelyFinish": most_likely_finish,
                "avgTravelLoad": round(avg_travel_load, 3),
                "avgVenueEdge": round(avg_venue_edge, 3),
            }
            champion_odds.append(
                {
                    "code": team.code,
                    "name": team.name,
                    "group": team.group,
                    "confederation": team.confederation,
                    "fifaRank": team.fifa_rank,
                    "flagCode": team.flag_code,
                    "probability": round(champion_probability, 4),
                    "power": team.power,
                }
            )
            team_stage_rows.append(team_row)
            team_rows_by_code[team.code] = team_row

        group_outlook = []
        for group_name, teams in self.groups.items():
            rows = []
            for team in teams:
                position_counts = group_position_counts[group_name][team.code]
                team_row = team_rows_by_code[team.code]
                rows.append(
                    {
                        "code": team.code,
                        "name": team.name,
                        "confederation": team.confederation,
                        "fifaRank": team.fifa_rank,
                        "flagCode": team.flag_code,
                        "groupWinProbability": round(position_counts[1] / iterations, 4),
                        "runnerUpProbability": round(position_counts[2] / iterations, 4),
                        "thirdProbability": round(position_counts[3] / iterations, 4),
                        "fourthProbability": round(position_counts[4] / iterations, 4),
                        "advanceProbability": round(advance_counts[team.code] / iterations, 4),
                        "avgPoints": team_row["avgGroupPoints"],
                        "avgGF": team_row["avgGoalsFor"],
                        "avgGA": team_row["avgGoalsAgainst"],
                        "expectedFinish": team_row["expectedFinish"],
                        "mostLikelyFinish": team_row["mostLikelyFinish"],
                        "avgTravelLoad": team_row["avgTravelLoad"],
                        "championProbability": round(champion_counts[team.code] / iterations, 4),
                    }
                )
            rows.sort(
                key=lambda item: (
                    item["expectedFinish"],
                    -item["advanceProbability"],
                    -item["avgPoints"],
                    item["name"],
                )
            )
            pattern_codes, pattern_count = group_pattern_counts[group_name].most_common(1)[0]
            group_outlook.append(
                {
                    "group": group_name,
                    "averagePower": round(
                        sum(self.team_lookup[row["code"]].power for row in rows) / len(rows), 2
                    ),
                    "venue": GROUP_VENUES[group_name],
                    "volatilityIndex": round(self._group_volatility(rows), 3),
                    "mostLikelyTableProbability": round(pattern_count / iterations, 4),
                    "mostLikelyTable": [
                        {
                            "code": code,
                            "name": self.team_lookup[code].name,
                        }
                        for code in pattern_codes
                    ],
                    "teams": rows,
                }
            )

        group_outlook.sort(key=lambda item: item["group"])
        champion_odds.sort(key=lambda item: (-item["probability"], -item["power"], item["name"]))
        team_stage_rows.sort(
            key=lambda item: (
                -item["championProbability"],
                -item["semifinalProbability"],
                -item["advanceProbability"],
                item["name"],
            )
        )

        favorite = champion_odds[0]
        dark_horse = next(
            (
                row
                for row in champion_odds
                if row["power"] < 80 and row["probability"] > 0.01
            ),
            champion_odds[min(7, len(champion_odds) - 1)],
        )
        toughest_group = max(group_outlook, key=lambda item: item["averagePower"])
        most_volatile_group = max(group_outlook, key=lambda item: item["volatilityIndex"])
        most_common_final = final_pairings.most_common(1)[0]
        team_profiles = self._build_team_profiles(
            team_rows_by_code=team_rows_by_code,
            sample_run=sample_run,
            stage_opponent_counts=stage_opponent_counts,
            stage_counts=stage_counts,
            advance_counts=advance_counts,
            iterations=iterations,
        )
        featured_summary = team_profiles[featured_code or favorite["code"]]
        scenario_compare_iterations = min(iterations, 700)
        scenario_compare = self._build_scenario_compare_rows(
            featured_code=featured_summary["code"],
            host_advantage=host_advantage,
            iterations=scenario_compare_iterations,
            seed_value=seed_value,
            active_scenario=scenario_key,
        )
        upset_tracker = self._build_upset_tracker(
            upset_signature_counts=upset_signature_counts,
            group_outlook=group_outlook,
            team_rows_by_code=team_rows_by_code,
            iterations=iterations,
        )
        venue_lens = self._build_venue_lens(
            sample_run=sample_run,
            team_profiles=team_profiles,
        )
        sample_run["championName"] = self.team_lookup[sample_run["champion"]].name
        sample_run["runnerUpName"] = self.team_lookup[sample_run["runner_up"]].name
        sample_run["featuredPath"] = featured_summary["samplePath"]
        sample_run["finalVenue"] = sample_run["rounds"][-1]["matches"][0]["venue"]

        return {
            "metadata": {
                "iterations": iterations,
                "scenario": scenario_key,
                "hostAdvantage": host_advantage,
                "scenarioCompareIterations": scenario_compare_iterations,
                "runId": self._build_run_id(
                    scenario_key=scenario_key,
                    iterations=iterations,
                    featured_code=featured_summary["code"],
                    host_advantage=host_advantage,
                    seed_value=seed_value,
                ),
            },
            "summary": {
                "favorite": favorite,
                "darkHorse": dark_horse,
                "averageGoalsPerMatch": round(total_goals / max(total_matches, 1), 2),
                "upsetRate": round(upset_count / max(total_matches, 1), 4),
                "mostCommonFinal": {
                    "teams": [
                        self.team_lookup[most_common_final[0][0]].name,
                        self.team_lookup[most_common_final[0][1]].name,
                    ],
                    "probability": round(most_common_final[1] / iterations, 4),
                },
                "modelNotes": [
                    f"{favorite['name']} leads the field at {favorite['probability'] * 100:.1f}% to win the trophy.",
                    f"Group {toughest_group['group']} grades as the most difficult section by average power.",
                    f"Group {most_volatile_group['group']} carries the most volatile placement profile in the draw.",
                    f"{dark_horse['name']} profiles as the liveliest dark horse outside the top tier.",
                ],
            },
            "featuredTeam": featured_summary,
            "championOdds": champion_odds,
            "teamTable": team_stage_rows,
            "teamProfiles": team_profiles,
            "groupOutlook": group_outlook,
            "scenarioCompare": scenario_compare,
            "upsetTracker": upset_tracker,
            "venueLens": venue_lens,
            "modelInfo": self._build_model_info(),
            "shareCard": self._build_share_payload(
                metadata={
                    "runId": self._build_run_id(
                        scenario_key=scenario_key,
                        iterations=iterations,
                        featured_code=featured_summary["code"],
                        host_advantage=host_advantage,
                        seed_value=seed_value,
                    )
                },
                summary={
                    "favorite": favorite,
                    "darkHorse": dark_horse,
                    "featuredTeam": featured_summary,
                    "mostCommonFinal": {
                        "teams": [
                            self.team_lookup[most_common_final[0][0]].name,
                            self.team_lookup[most_common_final[0][1]].name,
                        ],
                        "probability": round(most_common_final[1] / iterations, 4),
                    },
                    "upsetRate": round(upset_count / max(total_matches, 1), 4),
                },
            ),
            "sampleTournament": sample_run,
        }

    def _build_run_id(
        self,
        scenario_key: str,
        iterations: int,
        featured_code: str,
        host_advantage: bool,
        seed_value: int,
    ) -> str:
        host_tag = "HOST" if host_advantage else "NEUTRAL"
        return f"WC26-{scenario_key.upper()}-{iterations}-{featured_code}-{host_tag}-{seed_value}"

    def _build_model_info(self) -> Dict[str, object]:
        return {
            "headline": "How the simulator works",
            "steps": [
                "Each team starts with a hybrid power score built from FIFA rank anchor, squad prior, attack, midfield, defense, keeper, recent form, and host status.",
                "Group matches sample goals from venue-adjusted expected-goals estimates and then rank tables with points, head-to-head, goal difference, goals scored, and pre-tournament power.",
                "Best third-place teams are reassigned into the Round of 32 without same-group clashes against seeded group winners.",
                "Knockout matches use extra time and a keeper-weighted penalty model when needed.",
            ],
            "assumptions": [
                "Scenario presets change volatility and finishing rather than team identity.",
                "Venue and travel effects are stylized nudges for climate, altitude, and North American travel burden.",
                "Results are Monte Carlo estimates, not market odds.",
            ],
        }

    def _build_share_payload(
        self,
        metadata: Dict[str, object],
        summary: Dict[str, object],
    ) -> Dict[str, object]:
        featured_team = summary["featuredTeam"]
        most_common_final = summary["mostCommonFinal"]
        lines = [
            f"Run ID: {metadata['runId']}",
            f"Favorite: {summary['favorite']['name']} ({summary['favorite']['probability'] * 100:.1f}% title odds)",
            f"Dark horse: {summary['darkHorse']['name']} ({summary['darkHorse']['probability'] * 100:.1f}% title odds)",
            f"Featured team: {featured_team['name']} ({featured_team['advanceProbability'] * 100:.1f}% to advance, {featured_team['championProbability'] * 100:.1f}% to win)",
            f"Most common final: {most_common_final['teams'][0]} vs {most_common_final['teams'][1]} ({most_common_final['probability'] * 100:.1f}% of runs)",
            f"Upset rate: {summary['upsetRate'] * 100:.1f}% of matches",
        ]
        return {
            "title": "2026 World Cup Simulator Snapshot",
            "lines": lines,
            "downloadName": f"{metadata['runId']}.json",
        }

    def _group_volatility(self, rows: Sequence[Dict[str, object]]) -> float:
        entropies = []
        for row in rows:
            probabilities = [
                float(row["groupWinProbability"]),
                float(row["runnerUpProbability"]),
                float(row["thirdProbability"]),
                float(row["fourthProbability"]),
            ]
            entropy = 0.0
            for probability in probabilities:
                if probability > 0:
                    entropy -= probability * math.log(probability, 2)
            entropies.append(entropy / 2.0)
        return sum(entropies) / max(len(entropies), 1)

    def _build_upset_tracker(
        self,
        upset_signature_counts: Counter[Tuple[str, str, str]],
        group_outlook: Sequence[Dict[str, object]],
        team_rows_by_code: Dict[str, Dict[str, object]],
        iterations: int,
    ) -> Dict[str, object]:
        biggest_upset = None
        best_score = -1.0
        for (winner_code, loser_code, stage_display), count in upset_signature_counts.items():
            power_gap = abs(
                self.team_lookup[winner_code].power - self.team_lookup[loser_code].power
            )
            score = count * power_gap
            if score > best_score:
                best_score = score
                biggest_upset = {
                    "winnerCode": winner_code,
                    "winner": self.team_lookup[winner_code].name,
                    "loserCode": loser_code,
                    "loser": self.team_lookup[loser_code].name,
                    "stage": stage_display,
                    "probability": round(count / iterations, 4),
                    "powerGap": round(power_gap, 2),
                }

        power_sorted = sorted(self.teams, key=lambda item: item.power, reverse=True)[:10]
        fragile = min(
            power_sorted,
            key=lambda team: (
                team_rows_by_code[team.code]["advanceProbability"],
                team_rows_by_code[team.code]["quarterfinalProbability"],
            ),
        )
        volatile_group = max(group_outlook, key=lambda item: item["volatilityIndex"])
        return {
            "biggestUpsetCandidate": biggest_upset,
            "mostVolatileGroup": {
                "group": volatile_group["group"],
                "volatilityIndex": volatile_group["volatilityIndex"],
                "mostLikelyTableProbability": volatile_group["mostLikelyTableProbability"],
            },
            "fragileFavorite": {
                "code": fragile.code,
                "name": fragile.name,
                "advanceProbability": team_rows_by_code[fragile.code]["advanceProbability"],
                "quarterfinalProbability": team_rows_by_code[fragile.code]["quarterfinalProbability"],
                "championProbability": team_rows_by_code[fragile.code]["championProbability"],
                "power": fragile.power,
            },
        }

    def _build_venue_lens(
        self,
        sample_run: Dict[str, object],
        team_profiles: Dict[str, Dict[str, object]],
    ) -> Dict[str, object]:
        hottest_group_venue = max(
            GROUP_VENUES.items(),
            key=lambda item: item[1]["altitudeM"] if item[1]["climate"] == "high-altitude" else item[1]["altitudeM"] / 2,
        )
        toughest_traveler = max(
            team_profiles.values(),
            key=lambda item: item["avgTravelLoad"],
        )
        best_venue_fit = max(
            team_profiles.values(),
            key=lambda item: item["avgVenueEdge"],
        )
        final_match = sample_run["rounds"][-1]["matches"][0]
        return {
            "headline": f"The sample final lands in {final_match['venue']['city']}.",
            "cards": [
                {
                    "label": "Highest-altitude group",
                    "value": f"Group {hottest_group_venue[0]}",
                    "detail": f"{hottest_group_venue[1]['city']} at {hottest_group_venue[1]['altitudeM']}m",
                },
                {
                    "label": "Heaviest travel drag",
                    "value": toughest_traveler["name"],
                    "detail": f"{toughest_traveler['avgTravelLoad']:.3f} xG drag per match",
                },
                {
                    "label": "Best venue fit",
                    "value": best_venue_fit["name"],
                    "detail": f"{best_venue_fit['avgVenueEdge']:+.3f} average venue edge",
                },
            ],
            "notes": [
                "Travel drag is smallest for North American teams and largest for long-haul visitors.",
                "High-altitude and climate tags nudge expected goals rather than overriding team quality.",
                "Knockout rounds rotate through the three host countries before the sample final in New York / New Jersey.",
            ],
        }

    def _build_scenario_compare_rows(
        self,
        featured_code: str,
        host_advantage: bool,
        iterations: int,
        seed_value: int,
        active_scenario: str,
    ) -> List[Dict[str, object]]:
        rows = []
        for index, scenario_key in enumerate(SCENARIO_PRESETS.keys(), start=1):
            rows.append(
                self._simulate_compare_entry(
                    featured_code=featured_code,
                    host_advantage=host_advantage,
                    iterations=iterations,
                    scenario_key=scenario_key,
                    seed_value=seed_value + (index * 113),
                    active=scenario_key == active_scenario,
                )
            )
        return rows

    def _simulate_compare_entry(
        self,
        featured_code: str,
        host_advantage: bool,
        iterations: int,
        scenario_key: str,
        seed_value: int,
        active: bool,
    ) -> Dict[str, object]:
        rng = random.Random(seed_value)
        champion_counts: Counter[str] = Counter()
        advance_counts: Counter[str] = Counter()
        semifinal_counts: Counter[str] = Counter()
        total_goals = 0
        total_matches = 0
        upset_count = 0
        for _ in range(iterations):
            run = self._simulate_single_tournament(
                rng=rng,
                scenario_config=SCENARIO_PRESETS[scenario_key],
                host_advantage=host_advantage,
            )
            champion_counts[run["champion"]] += 1
            for code in run["qualified_codes"]:
                advance_counts[code] += 1
            for code, stage_labels in run["stage_reached"].items():
                if "semifinal" in stage_labels:
                    semifinal_counts[code] += 1
            total_goals += int(run["stats"]["goals"])
            total_matches += int(run["stats"]["matches"])
            upset_count += int(run["stats"]["upsets"])
        favorite_code, favorite_count = champion_counts.most_common(1)[0]
        featured_champion_probability = champion_counts[featured_code] / iterations
        return {
            "id": scenario_key,
            "label": str(SCENARIO_PRESETS[scenario_key]["label"]),
            "active": active,
            "iterationsUsed": iterations,
            "featuredTeam": self.team_lookup[featured_code].name,
            "fieldFavorite": self.team_lookup[favorite_code].name,
            "favoriteProbability": round(favorite_count / iterations, 4),
            "titleProbability": round(featured_champion_probability, 4),
            "advanceProbability": round(advance_counts[featured_code] / iterations, 4),
            "semifinalProbability": round(semifinal_counts[featured_code] / iterations, 4),
            "averageGoalsPerMatch": round(total_goals / max(total_matches, 1), 2),
            "upsetRate": round(upset_count / max(total_matches, 1), 4),
        }

    def _build_sample_paths(
        self,
        sample_run: Dict[str, object],
    ) -> Dict[str, List[Dict[str, object]]]:
        paths: Dict[str, List[Dict[str, object]]] = defaultdict(list)
        for group_payload in sample_run["groups"]:
            stage_label = f"Group {group_payload['group']}"
            for match in group_payload["matches"]:
                home_code = str(match["homeCode"])
                away_code = str(match["awayCode"])
                paths[home_code].append(
                    self._path_entry_for_match(home_code, away_code, match, stage_label)
                )
                paths[away_code].append(
                    self._path_entry_for_match(away_code, home_code, match, stage_label)
                )
        for round_payload in sample_run["rounds"]:
            stage_label = str(round_payload["round"])
            for match in round_payload["matches"]:
                home_code = str(match["homeCode"])
                away_code = str(match["awayCode"])
                paths[home_code].append(
                    self._path_entry_for_match(home_code, away_code, match, stage_label)
                )
                paths[away_code].append(
                    self._path_entry_for_match(away_code, home_code, match, stage_label)
                )
        return paths

    def _path_entry_for_match(
        self,
        code: str,
        opponent_code: str,
        match: Dict[str, object],
        stage_label: str,
    ) -> Dict[str, object]:
        team_is_home = code == str(match["homeCode"])
        goals_for = int(match["homeGoals"] if team_is_home else match["awayGoals"])
        goals_against = int(match["awayGoals"] if team_is_home else match["homeGoals"])
        if goals_for > goals_against:
            result = "W"
        elif goals_against > goals_for:
            result = "L"
        else:
            result = "D"
            if match.get("winner"):
                result = "W" if str(match["winner"]) == code else "L"
        return {
            "stage": stage_label,
            "opponentCode": opponent_code,
            "opponent": self.team_lookup[opponent_code].name,
            "result": result,
            "scoreline": str(match["scoreline"]),
            "venueLabel": f"{match['venue']['city']}, {match['venue']['country']}",
        }

    def _common_opponent_rows(
        self,
        code: str,
        stage_opponent_counts: Dict[str, Dict[str, Counter[str]]],
        stage_counts: Dict[str, Counter[str]],
        advance_counts: Counter[str],
    ) -> List[Dict[str, object]]:
        denominators = {
            "round_of_32": advance_counts[code],
            "round_of_16": stage_counts[code]["round_of_16"],
            "quarterfinal": stage_counts[code]["quarterfinal"],
            "semifinal": stage_counts[code]["semifinal"],
            "final": stage_counts[code]["final"],
        }
        rows = []
        for stage_key in ("round_of_32", "round_of_16", "quarterfinal", "semifinal", "final"):
            denominator = denominators[stage_key]
            if denominator <= 0:
                continue
            counter = stage_opponent_counts[code][stage_key]
            if not counter:
                continue
            opponent_code, count = counter.most_common(1)[0]
            rows.append(
                {
                    "stageKey": stage_key,
                    "stage": STAGE_DISPLAY[stage_key],
                    "opponentCode": opponent_code,
                    "opponent": self.team_lookup[opponent_code].name,
                    "probability": round(count / denominator, 4),
                }
            )
        return rows

    def _build_team_profiles(
        self,
        team_rows_by_code: Dict[str, Dict[str, object]],
        sample_run: Dict[str, object],
        stage_opponent_counts: Dict[str, Dict[str, Counter[str]]],
        stage_counts: Dict[str, Counter[str]],
        advance_counts: Counter[str],
        iterations: int,
    ) -> Dict[str, Dict[str, object]]:
        sample_paths = self._build_sample_paths(sample_run)
        profiles: Dict[str, Dict[str, object]] = {}
        for code, row in team_rows_by_code.items():
            team = self.team_lookup[code]
            group_rivals = [
                rival for rival in self.groups[team.group] if rival.code != code
            ]
            toughest_rival = max(group_rivals, key=lambda item: item.power)
            power_breakdown = team.power_components()
            primary_edges = ", ".join(item["label"] for item in power_breakdown[:2])
            profile = {
                **row,
                "powerBreakdown": power_breakdown,
                "strengths": team.strengths(),
                "risks": team.risks(),
                "samplePath": sample_paths.get(code, []),
                "commonOpponents": self._common_opponent_rows(
                    code=code,
                    stage_opponent_counts=stage_opponent_counts,
                    stage_counts=stage_counts,
                    advance_counts=advance_counts,
                ),
                "notes": [
                    f"{team.name} project to finish {row['expectedFinish']:.2f} in Group {team.group} with {row['avgGoalsFor']:.2f} goals for and {row['avgGoalsAgainst']:.2f} against per run.",
                    f"The strongest power inputs are {primary_edges.lower()}, while {toughest_rival.name} remain the main same-group stress test.",
                    f"The travel layer averages {row['avgTravelLoad']:.3f} xG drag per match and a {row['avgVenueEdge']:+.3f} total venue edge.",
                ],
                "toughestGroupRival": toughest_rival.name,
                "travelNote": f"{row['avgTravelLoad']:.3f} average travel drag",
            }
            profiles[code] = profile
        return profiles

    def _simulate_single_tournament(
        self,
        rng: random.Random,
        scenario_config: Dict[str, object],
        host_advantage: bool,
    ) -> Dict[str, object]:
        group_results = []
        all_matches = []
        group_positions: Dict[str, Dict[str, int]] = {}
        group_points: Dict[str, int] = {}
        qualified_codes = set()
        stage_reached: Dict[str, set] = defaultdict(set)
        total_goals = 0
        total_matches = 0
        upset_count = 0

        for group_name, teams in self.groups.items():
            result = self._simulate_group(
                group_name=group_name,
                teams=teams,
                rng=rng,
                scenario_config=scenario_config,
                host_advantage=host_advantage,
            )
            group_results.append(result)
            all_matches.extend(result["matches"])
            positions_for_group = {}
            for index, row in enumerate(result["standings"], start=1):
                positions_for_group[row["code"]] = index
                group_points[row["code"]] = row["points"]
            group_positions[group_name] = positions_for_group
            total_goals += result["stats"]["goals"]
            total_matches += result["stats"]["matches"]
            upset_count += result["stats"]["upsets"]

        winners = {group["group"]: group["standings"][0]["code"] for group in group_results}
        runners_up = {group["group"]: group["standings"][1]["code"] for group in group_results}
        third_place_rows = [
            {
                **group["standings"][2],
                "group": group["group"],
            }
            for group in group_results
        ]
        best_thirds = sorted(
            third_place_rows,
            key=lambda row: (
                -row["points"],
                -row["gd"],
                -row["gf"],
                -self.team_lookup[row["code"]].power,
                row["name"],
            ),
        )[:8]

        for group in group_results:
            qualified_codes.add(group["standings"][0]["code"])
            qualified_codes.add(group["standings"][1]["code"])
            stage_reached[group["standings"][0]["code"]].add("round_of_32")
            stage_reached[group["standings"][1]["code"]].add("round_of_32")
        for row in best_thirds:
            qualified_codes.add(row["code"])
            stage_reached[row["code"]].add("round_of_32")

        third_assignment = self._assign_third_place_slots(
            third_rows=best_thirds,
            slot_rules=THIRD_SLOT_RULES,
        )

        round_of_32_inputs = []
        for fixture in ROUND_OF_32_BLUEPRINT:
            home = self._resolve_slot(fixture["home"], winners, runners_up, third_assignment)
            away = self._resolve_slot(fixture["away"], winners, runners_up, third_assignment)
            round_of_32_inputs.append((fixture["id"], home, away))

        rounds = []
        current_round_results = self._play_round(
            round_label="Round of 32",
            round_id_prefix="R16",
            fixtures=round_of_32_inputs,
            rng=rng,
            scenario_config=scenario_config,
            host_advantage=host_advantage,
        )
        rounds.append(
            {
                "round": "Round of 32",
                "stageKey": ROUND_STAGE_KEYS["Round of 32"],
                "matches": current_round_results["matches"],
            }
        )
        all_matches.extend(current_round_results["matches"])
        total_goals += current_round_results["stats"]["goals"]
        total_matches += current_round_results["stats"]["matches"]
        upset_count += current_round_results["stats"]["upsets"]
        for code in current_round_results["winners"]:
            stage_reached[code].add("round_of_16")

        current_round_results = self._play_round(
            round_label="Round of 16",
            round_id_prefix="QF",
            fixtures=self._next_round_fixtures("Round of 16", current_round_results["winners"]),
            rng=rng,
            scenario_config=scenario_config,
            host_advantage=host_advantage,
        )
        rounds.append(
            {
                "round": "Round of 16",
                "stageKey": ROUND_STAGE_KEYS["Round of 16"],
                "matches": current_round_results["matches"],
            }
        )
        all_matches.extend(current_round_results["matches"])
        total_goals += current_round_results["stats"]["goals"]
        total_matches += current_round_results["stats"]["matches"]
        upset_count += current_round_results["stats"]["upsets"]
        for code in current_round_results["winners"]:
            stage_reached[code].add("quarterfinal")

        current_round_results = self._play_round(
            round_label="Quarterfinals",
            round_id_prefix="SF",
            fixtures=self._next_round_fixtures("Quarterfinals", current_round_results["winners"]),
            rng=rng,
            scenario_config=scenario_config,
            host_advantage=host_advantage,
        )
        rounds.append(
            {
                "round": "Quarterfinals",
                "stageKey": ROUND_STAGE_KEYS["Quarterfinals"],
                "matches": current_round_results["matches"],
            }
        )
        all_matches.extend(current_round_results["matches"])
        total_goals += current_round_results["stats"]["goals"]
        total_matches += current_round_results["stats"]["matches"]
        upset_count += current_round_results["stats"]["upsets"]
        for code in current_round_results["winners"]:
            stage_reached[code].add("semifinal")

        semifinal_results = self._play_round(
            round_label="Semifinals",
            round_id_prefix="F",
            fixtures=self._next_round_fixtures("Semifinals", current_round_results["winners"]),
            rng=rng,
            scenario_config=scenario_config,
            host_advantage=host_advantage,
        )
        rounds.append(
            {
                "round": "Semifinals",
                "stageKey": ROUND_STAGE_KEYS["Semifinals"],
                "matches": semifinal_results["matches"],
            }
        )
        all_matches.extend(semifinal_results["matches"])
        total_goals += semifinal_results["stats"]["goals"]
        total_matches += semifinal_results["stats"]["matches"]
        upset_count += semifinal_results["stats"]["upsets"]
        for code in semifinal_results["winners"]:
            stage_reached[code].add("final")

        final_results = self._play_round(
            round_label="Final",
            round_id_prefix="C",
            fixtures=self._next_round_fixtures("Final", semifinal_results["winners"]),
            rng=rng,
            scenario_config=scenario_config,
            host_advantage=host_advantage,
        )
        rounds.append(
            {
                "round": "Final",
                "stageKey": ROUND_STAGE_KEYS["Final"],
                "matches": final_results["matches"],
            }
        )
        all_matches.extend(final_results["matches"])
        total_goals += final_results["stats"]["goals"]
        total_matches += final_results["stats"]["matches"]
        upset_count += final_results["stats"]["upsets"]

        champion = final_results["winners"][0]
        runner_up = final_results["losers"][0]
        stage_reached[champion].add("champion")

        third_place_table = []
        for rank, row in enumerate(
            sorted(
                third_place_rows,
                key=lambda entry: (
                    -entry["points"],
                    -entry["gd"],
                    -entry["gf"],
                    -self.team_lookup[entry["code"]].power,
                    entry["name"],
                ),
            ),
            start=1,
        ):
            third_place_table.append(
                {
                    "rank": rank,
                    "group": row["group"],
                    "code": row["code"],
                    "name": row["name"],
                    "points": row["points"],
                    "gd": row["gd"],
                    "gf": row["gf"],
                    "qualified": row["code"] in {entry["code"] for entry in best_thirds},
                }
            )

        return {
            "groups": group_results,
            "thirdPlaceTable": third_place_table,
            "rounds": rounds,
            "allMatches": all_matches,
            "champion": champion,
            "runner_up": runner_up,
            "group_positions": group_positions,
            "group_points": group_points,
            "qualified_codes": qualified_codes,
            "stage_reached": stage_reached,
            "stats": {
                "goals": total_goals,
                "matches": total_matches,
                "upsets": upset_count,
            },
        }

    def _simulate_group(
        self,
        group_name: str,
        teams: Sequence[Team],
        rng: random.Random,
        scenario_config: Dict[str, object],
        host_advantage: bool,
    ) -> Dict[str, object]:
        standings = {
            team.code: {
                "code": team.code,
                "name": team.name,
                "points": 0,
                "gf": 0,
                "ga": 0,
                "gd": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
            }
            for team in teams
        }
        venue = self._group_venue(group_name)
        matches = []
        total_goals = 0
        upset_count = 0

        for matchday, (home_index, away_index) in enumerate(GROUP_FIXTURES, start=1):
            home = teams[home_index]
            away = teams[away_index]
            result = self._simulate_match(
                home=home,
                away=away,
                rng=rng,
                scenario_config=scenario_config,
                host_advantage=host_advantage,
                knockout=False,
                venue=venue,
                stage_key="group",
                stage_display=f"Group {group_name}",
            )
            result["matchday"] = matchday
            total_goals += result["homeGoals"] + result["awayGoals"]
            upset_count += result["upset"]
            standings[home.code]["gf"] += result["homeGoals"]
            standings[home.code]["ga"] += result["awayGoals"]
            standings[away.code]["gf"] += result["awayGoals"]
            standings[away.code]["ga"] += result["homeGoals"]
            standings[home.code]["gd"] = standings[home.code]["gf"] - standings[home.code]["ga"]
            standings[away.code]["gd"] = standings[away.code]["gf"] - standings[away.code]["ga"]

            if result["homeGoals"] > result["awayGoals"]:
                standings[home.code]["points"] += 3
                standings[home.code]["wins"] += 1
                standings[away.code]["losses"] += 1
            elif result["awayGoals"] > result["homeGoals"]:
                standings[away.code]["points"] += 3
                standings[away.code]["wins"] += 1
                standings[home.code]["losses"] += 1
            else:
                standings[home.code]["points"] += 1
                standings[away.code]["points"] += 1
                standings[home.code]["draws"] += 1
                standings[away.code]["draws"] += 1

            matches.append(result)

        ordered_codes = self._rank_group(teams, standings, matches)
        ordered_standings = []
        for code in ordered_codes:
            row = standings[code].copy()
            row["power"] = self.team_lookup[code].power
            ordered_standings.append(row)

        return {
            "group": group_name,
            "venue": venue,
            "standings": ordered_standings,
            "matches": matches,
            "stats": {
                "goals": total_goals,
                "matches": len(matches),
                "upsets": upset_count,
            },
        }

    def _rank_group(
        self,
        teams: Sequence[Team],
        standings: Dict[str, Dict[str, int]],
        matches: Sequence[Dict[str, object]],
    ) -> List[str]:
        by_points: Dict[int, List[str]] = defaultdict(list)
        for team in teams:
            by_points[standings[team.code]["points"]].append(team.code)

        ordered_codes: List[str] = []
        for points in sorted(by_points.keys(), reverse=True):
            bucket = by_points[points]
            if len(bucket) == 1:
                ordered_codes.extend(bucket)
                continue

            mini = {
                code: {"points": 0, "gd": 0, "gf": 0}
                for code in bucket
            }
            for match in matches:
                home = match["homeCode"]
                away = match["awayCode"]
                if home not in mini or away not in mini:
                    continue
                home_goals = int(match["homeGoals"])
                away_goals = int(match["awayGoals"])
                mini[home]["gf"] += home_goals
                mini[home]["gd"] += home_goals - away_goals
                mini[away]["gf"] += away_goals
                mini[away]["gd"] += away_goals - home_goals
                if home_goals > away_goals:
                    mini[home]["points"] += 3
                elif away_goals > home_goals:
                    mini[away]["points"] += 3
                else:
                    mini[home]["points"] += 1
                    mini[away]["points"] += 1

            ranked_bucket = sorted(
                bucket,
                key=lambda code: (
                    mini[code]["points"],
                    mini[code]["gd"],
                    mini[code]["gf"],
                    standings[code]["gd"],
                    standings[code]["gf"],
                    self.team_lookup[code].power,
                    self.team_lookup[code].attack,
                ),
                reverse=True,
            )
            ordered_codes.extend(ranked_bucket)
        return ordered_codes

    def _simulate_match(
        self,
        home: Team,
        away: Team,
        rng: random.Random,
        scenario_config: Dict[str, object],
        host_advantage: bool,
        knockout: bool,
        venue: Dict[str, object],
        stage_key: str,
        stage_display: str,
    ) -> Dict[str, object]:
        volatility = float(scenario_config["volatility"])
        finishing = float(scenario_config["finishing"])
        strength_edge = (home.power - away.power) / 10.0
        attack_edge = (home.attack - away.defense) / 15.0
        midfield_edge = (home.midfield - away.midfield) / 22.0
        form_edge = (home.form - away.form) / 3.6
        home_adjustment = self._venue_adjustment(home, venue, host_advantage)
        away_adjustment = self._venue_adjustment(away, venue, host_advantage)

        home_expected = (
            1.22
            + (0.16 * strength_edge)
            + (0.18 * attack_edge)
            + (0.08 * midfield_edge)
            + (0.05 * form_edge)
            + home_adjustment["total"]
        )
        away_expected = (
            1.08
            - (0.12 * strength_edge)
            + (0.16 * ((away.attack - home.defense) / 15.0))
            - (0.06 * midfield_edge)
            - (0.04 * form_edge)
            + away_adjustment["total"]
        )

        shock = (rng.random() - 0.5) * volatility
        home_expected = clamp(0.25, (home_expected + shock) * finishing, 3.4)
        away_expected = clamp(0.20, (away_expected - (shock * 0.65)) * finishing, 3.2)

        home_goals = poisson_sample(home_expected, rng)
        away_goals = poisson_sample(away_expected, rng)
        et_home = 0
        et_away = 0
        pens_home = None
        pens_away = None
        winner = None

        if knockout and home_goals == away_goals:
            extra_multiplier = float(scenario_config["extra_time"])
            et_home = poisson_sample(max(home_expected * extra_multiplier, 0.08), rng)
            et_away = poisson_sample(max(away_expected * extra_multiplier, 0.08), rng)
            home_goals += et_home
            away_goals += et_away
            if home_goals == away_goals:
                pens_home, pens_away = self._simulate_penalties(home, away, rng)
                winner = home.code if pens_home > pens_away else away.code
            else:
                winner = home.code if home_goals > away_goals else away.code

        if winner is None and knockout:
            winner = home.code if home_goals > away_goals else away.code

        underdog_won = 0
        if home_goals != away_goals:
            expected_winner = home if home.power >= away.power else away
            actual_winner = home if home_goals > away_goals else away
            if expected_winner.code != actual_winner.code and abs(home.power - away.power) >= 3:
                underdog_won = 1
        elif winner is not None:
            expected_winner = home if home.power >= away.power else away
            actual_winner = self.team_lookup[winner]
            if expected_winner.code != actual_winner.code and abs(home.power - away.power) >= 3:
                underdog_won = 1

        scoreline = f"{home_goals}-{away_goals}"
        if pens_home is not None and pens_away is not None:
            scoreline = f"{home_goals}-{away_goals} ({pens_home}-{pens_away} pens)"

        return {
            "homeCode": home.code,
            "homeName": home.name,
            "awayCode": away.code,
            "awayName": away.name,
            "homeGoals": home_goals,
            "awayGoals": away_goals,
            "homeExpectedGoals": round(home_expected, 2),
            "awayExpectedGoals": round(away_expected, 2),
            "winner": winner,
            "winnerName": self.team_lookup[winner].name if winner else None,
            "scoreline": scoreline,
            "extraTimeGoals": {"home": et_home, "away": et_away},
            "penalties": None
            if pens_home is None
            else {"home": pens_home, "away": pens_away},
            "upset": underdog_won,
            "venue": venue,
            "stageKey": stage_key,
            "stageDisplay": stage_display,
            "venueAdjustments": {
                "home": home_adjustment,
                "away": away_adjustment,
            },
        }

    def _group_venue(self, group_name: str) -> Dict[str, object]:
        venue = GROUP_VENUES[group_name]
        return {
            **venue,
            "label": f"{venue['city']}, {venue['country']}",
        }

    def _round_venue(self, round_label: str, fixture_index: int) -> Dict[str, object]:
        venues = KNOCKOUT_VENUES[round_label]
        venue = venues[(fixture_index - 1) % len(venues)]
        return {
            **venue,
            "label": f"{venue['city']}, {venue['country']}",
        }

    def _venue_adjustment(
        self,
        team: Team,
        venue: Dict[str, object],
        host_advantage: bool,
    ) -> Dict[str, float]:
        venue_country_code = str(venue["countryCode"]).upper()
        climate = str(venue["climate"])
        altitude = int(venue["altitudeM"])
        host_boost = 0.0
        if host_advantage and team.host and team.code == venue_country_code:
            host_boost = 0.18

        travel_load = TRAVEL_LOAD_BY_CONFED.get(team.confederation, 0.05)
        if team.code == venue_country_code:
            travel_load *= 0.08
        elif team.confederation == "Concacaf":
            travel_load *= 0.55
        elif team.confederation == "CONMEBOL":
            travel_load *= 0.82

        climate_fit = 0.0
        warm_weather_confeds = {"Concacaf", "CONMEBOL", "CAF"}
        if climate in {"cool", "mild", "temperate"}:
            climate_fit = 0.03 if team.code in COOL_WEATHER_CODES else -0.015
        elif climate in {"hot", "humid", "warm"}:
            if team.confederation in warm_weather_confeds or team.code in {"MEX", "USA", "CAN"}:
                climate_fit = 0.024
            elif team.code in COOL_WEATHER_CODES:
                climate_fit = -0.032
        elif climate == "continental":
            climate_fit = 0.012 if team.confederation in {"UEFA", "Concacaf"} else -0.006
        elif climate == "high-altitude":
            climate_fit = 0.016 if team.code in ALTITUDE_READY_CODES else -0.024

        altitude_fit = 0.0
        if altitude >= 1800:
            altitude_fit = 0.05 if team.code in ALTITUDE_READY_CODES else -0.05
        elif altitude >= 500:
            altitude_fit = 0.02 if team.code in ALTITUDE_READY_CODES else -0.015

        total = host_boost + climate_fit + altitude_fit - travel_load
        return {
            "hostBoost": round(host_boost, 3),
            "travelLoad": round(travel_load, 3),
            "climateFit": round(climate_fit, 3),
            "altitudeFit": round(altitude_fit, 3),
            "total": round(total, 3),
        }

    def _simulate_penalties(
        self,
        home: Team,
        away: Team,
        rng: random.Random,
    ) -> Tuple[int, int]:
        home_skill = (
            (home.keeper * 0.40)
            + (home.rating * 0.16)
            + (home.midfield * 0.12)
            + (home.form * 4.0)
        )
        away_skill = (
            (away.keeper * 0.40)
            + (away.rating * 0.16)
            + (away.midfield * 0.12)
            + (away.form * 4.0)
        )
        home_make_prob = clamp(0.58, 0.73 + ((home_skill - away_skill) / 160.0), 0.88)
        away_make_prob = clamp(0.58, 0.73 + ((away_skill - home_skill) / 160.0), 0.88)
        home_score = sum(1 for _ in range(5) if rng.random() < home_make_prob)
        away_score = sum(1 for _ in range(5) if rng.random() < away_make_prob)
        while home_score == away_score:
            home_score += 1 if rng.random() < home_make_prob else 0
            away_score += 1 if rng.random() < away_make_prob else 0
        return home_score, away_score

    def _assign_third_place_slots(
        self,
        third_rows: Sequence[Dict[str, object]],
        slot_rules: Sequence[Tuple[str, str]],
    ) -> Dict[str, Team]:
        third_teams = [self.team_lookup[row["code"]] for row in third_rows]

        def backtrack(
            remaining_teams: List[Team],
            remaining_slots: List[Tuple[str, str]],
            assignments: Dict[str, Team],
        ) -> Optional[Dict[str, Team]]:
            if not remaining_teams:
                return assignments.copy()

            team = min(
                remaining_teams,
                key=lambda current: sum(
                    1 for _, owner_group in remaining_slots if current.group != owner_group
                ),
            )
            compatible_slots = [
                item for item in remaining_slots if item[1] != team.group
            ]
            compatible_slots.sort(key=lambda item: item[0])

            if not compatible_slots:
                return None

            next_teams = [candidate for candidate in remaining_teams if candidate.code != team.code]
            for slot_name, owner_group in compatible_slots:
                assignments[slot_name] = team
                next_slots = [
                    item for item in remaining_slots if item[0] != slot_name
                ]
                solved = backtrack(next_teams, next_slots, assignments)
                if solved is not None:
                    return solved
                assignments.pop(slot_name, None)
            return None

        solved = backtrack(third_teams, list(slot_rules), {})
        if solved is None:
            raise RuntimeError("Unable to assign third-place teams to knockout slots.")
        return solved

    def _resolve_slot(
        self,
        token: Tuple[str, str],
        winners: Dict[str, str],
        runners_up: Dict[str, str],
        third_assignment: Dict[str, Team],
    ) -> Team:
        kind, key = token
        if kind == "winner":
            return self.team_lookup[winners[key]]
        if kind == "runner_up":
            return self.team_lookup[runners_up[key]]
        return third_assignment[key]

    def _play_round(
        self,
        round_label: str,
        round_id_prefix: str,
        fixtures: Sequence[Tuple[str, Team, Team]],
        rng: random.Random,
        scenario_config: Dict[str, object],
        host_advantage: bool,
    ) -> Dict[str, object]:
        matches = []
        winners = []
        losers = []
        total_goals = 0
        upset_count = 0

        for index, (fixture_id, home, away) in enumerate(fixtures, start=1):
            venue = self._round_venue(round_label, index)
            result = self._simulate_match(
                home=home,
                away=away,
                rng=rng,
                scenario_config=scenario_config,
                host_advantage=host_advantage,
                knockout=True,
                venue=venue,
                stage_key=ROUND_STAGE_KEYS[round_label],
                stage_display=round_label,
            )
            winner_code = result["winner"]
            loser_code = away.code if winner_code == home.code else home.code
            winners.append(winner_code)
            losers.append(loser_code)
            total_goals += result["homeGoals"] + result["awayGoals"]
            upset_count += result["upset"]
            matches.append(
                {
                    "id": fixture_id,
                    "round": round_label,
                    **result,
                }
            )

        return {
            "matches": matches,
            "winners": winners,
            "losers": losers,
            "stats": {
                "goals": total_goals,
                "matches": len(matches),
                "upsets": upset_count,
            },
        }

    def _next_round_fixtures(
        self,
        round_label: str,
        winners: Sequence[str],
    ) -> List[Tuple[str, Team, Team]]:
        pairs = []
        team_pairs = list(zip(winners[::2], winners[1::2]))
        for index, (home_code, away_code) in enumerate(team_pairs, start=1):
            pairs.append(
                (
                    f"{round_label}-{index}",
                    self.team_lookup[home_code],
                    self.team_lookup[away_code],
                )
            )
        return pairs
