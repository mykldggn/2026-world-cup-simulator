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
        rng = random.Random(seed if seed is not None else 20260611)

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
            for group_name, positions in run["group_positions"].items():
                for code, position in positions.items():
                    group_position_counts[group_name][code][position] += 1
            for code, points in run["group_points"].items():
                avg_points_tracker[code].append(points)

        assert sample_run is not None

        champion_odds = []
        team_stage_rows = []
        for team in sorted(self.teams, key=lambda item: (-champion_counts[item.code], -item.power, item.name)):
            champion_probability = champion_counts[team.code] / iterations
            final_probability = finalists[team.code] / iterations
            round_of_32_probability = stage_counts[team.code]["round_of_32"] / iterations
            round_of_16_probability = stage_counts[team.code]["round_of_16"] / iterations
            quarterfinal_probability = stage_counts[team.code]["quarterfinal"] / iterations
            semifinal_probability = stage_counts[team.code]["semifinal"] / iterations
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

        group_outlook = []
        for group_name, teams in self.groups.items():
            rows = []
            for team in teams:
                position_counts = group_position_counts[group_name][team.code]
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
                        "avgPoints": round(sum(avg_points_tracker[team.code]) / iterations, 2),
                        "championProbability": round(champion_counts[team.code] / iterations, 4),
                    }
                )
            rows.sort(
                key=lambda item: (
                    -item["advanceProbability"],
                    -item["groupWinProbability"],
                    -item["avgPoints"],
                    item["name"],
                )
            )
            group_outlook.append(
                {
                    "group": group_name,
                    "averagePower": round(
                        sum(self.team_lookup[row["code"]].power for row in rows) / len(rows), 2
                    ),
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
        most_common_final = final_pairings.most_common(1)[0]

        featured_summary = self._build_featured_team_summary(
            featured_code=featured_code or favorite["code"],
            stage_rows=team_stage_rows,
        )

        return {
            "metadata": {
                "iterations": iterations,
                "scenario": scenario_key,
                "hostAdvantage": host_advantage,
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
                    f"{dark_horse['name']} profiles as the liveliest dark horse outside the top tier.",
                ],
            },
            "featuredTeam": featured_summary,
            "championOdds": champion_odds,
            "teamTable": team_stage_rows,
            "groupOutlook": group_outlook,
            "sampleTournament": sample_run,
        }

    def _build_featured_team_summary(
        self,
        featured_code: str,
        stage_rows: Sequence[Dict[str, object]],
    ) -> Dict[str, object]:
        row = next(item for item in stage_rows if item["code"] == featured_code)
        team = self.team_lookup[featured_code]
        group_rivals = [
            rival for rival in self.groups[team.group] if rival.code != featured_code
        ]
        toughest_rival = max(group_rivals, key=lambda item: item.power)
        return {
            "code": featured_code,
            "name": team.name,
            "group": team.group,
            "confederation": team.confederation,
            "fifaRank": team.fifa_rank,
            "flagCode": team.flag_code,
            "power": team.power,
            "rankingAnchor": team.ranking_anchor,
            "style": team.style,
            "advanceProbability": row["advanceProbability"],
            "quarterfinalProbability": row["quarterfinalProbability"],
            "championProbability": row["championProbability"],
            "avgGroupPoints": row["avgGroupPoints"],
            "toughestGroupRival": toughest_rival.name,
            "notes": [
                f"{team.name} sit at FIFA rank {team.fifa_rank} in the 1 April 2026 snapshot and advance from Group {team.group} in {row['advanceProbability'] * 100:.1f}% of runs.",
                f"The toughest same-group matchup is {toughest_rival.name} on the current power model.",
                f"The engine blends a {team.ranking_anchor:.1f} ranking anchor with line-by-line ratings and tags {team.style} as {team.name}'s most repeatable strategic identity.",
            ],
        }

    def _simulate_single_tournament(
        self,
        rng: random.Random,
        scenario_config: Dict[str, object],
        host_advantage: bool,
    ) -> Dict[str, object]:
        group_results = []
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
            {"round": "Round of 32", "matches": current_round_results["matches"]}
        )
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
            {"round": "Round of 16", "matches": current_round_results["matches"]}
        )
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
            {"round": "Quarterfinals", "matches": current_round_results["matches"]}
        )
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
        rounds.append({"round": "Semifinals", "matches": semifinal_results["matches"]})
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
        rounds.append({"round": "Final", "matches": final_results["matches"]})
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
        matches = []
        total_goals = 0
        upset_count = 0

        for home_index, away_index in GROUP_FIXTURES:
            home = teams[home_index]
            away = teams[away_index]
            result = self._simulate_match(
                home=home,
                away=away,
                rng=rng,
                scenario_config=scenario_config,
                host_advantage=host_advantage,
                knockout=False,
            )
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
    ) -> Dict[str, object]:
        volatility = float(scenario_config["volatility"])
        finishing = float(scenario_config["finishing"])
        strength_edge = (home.power - away.power) / 10.0
        attack_edge = (home.attack - away.defense) / 15.0
        midfield_edge = (home.midfield - away.midfield) / 22.0
        form_edge = (home.form - away.form) / 3.6
        host_edge = 0.22 if host_advantage and home.host else 0.0
        away_host_edge = 0.22 if host_advantage and away.host else 0.0

        home_expected = (
            1.22
            + (0.16 * strength_edge)
            + (0.18 * attack_edge)
            + (0.08 * midfield_edge)
            + (0.05 * form_edge)
            + host_edge
        )
        away_expected = (
            1.08
            - (0.12 * strength_edge)
            + (0.16 * ((away.attack - home.defense) / 15.0))
            - (0.06 * midfield_edge)
            - (0.04 * form_edge)
            + away_host_edge
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
            "scoreline": scoreline,
            "extraTimeGoals": {"home": et_home, "away": et_away},
            "penalties": None
            if pens_home is None
            else {"home": pens_home, "away": pens_away},
            "upset": underdog_won,
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

        for fixture_id, home, away in fixtures:
            result = self._simulate_match(
                home=home,
                away=away,
                rng=rng,
                scenario_config=scenario_config,
                host_advantage=host_advantage,
                knockout=True,
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
