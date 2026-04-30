import unittest

from app.simulator import WorldCupSimulator


class WorldCupSimulatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.simulator = WorldCupSimulator()

    def test_metadata_shape(self) -> None:
        result = self.simulator.simulate(
            iterations=80,
            scenario="balanced",
            featured_team="USA",
            seed=42,
        )
        self.assertEqual(result["metadata"]["iterations"], 80)
        self.assertEqual(len(result["groupOutlook"]), 12)
        self.assertGreaterEqual(len(result["championOdds"]), 48)
        self.assertIn("favorite", result["summary"])

    def test_sample_tournament_structure(self) -> None:
        result = self.simulator.simulate(
            iterations=60,
            scenario="chaos",
            featured_team="BRA",
            seed=7,
        )
        sample = result["sampleTournament"]
        self.assertEqual(len(sample["groups"]), 12)
        self.assertEqual(len(sample["thirdPlaceTable"]), 12)
        self.assertEqual(len(sample["rounds"]), 5)
        self.assertEqual(len(sample["allMatches"]), 103)
        self.assertIn(sample["champion"], {row["code"] for row in result["championOdds"]})

    def test_extended_outputs_present(self) -> None:
        result = self.simulator.simulate(
            iterations=80,
            scenario="chalk",
            featured_team="USA",
            seed=21,
        )
        self.assertEqual(len(result["scenarioCompare"]), 3)
        self.assertIn("downloadName", result["shareCard"])
        self.assertIn("cards", result["venueLens"])
        self.assertIn("headline", result["modelInfo"])
        self.assertIn("USA", result["teamProfiles"])
        self.assertIn("powerBreakdown", result["teamProfiles"]["USA"])
        self.assertIn("commonOpponents", result["teamProfiles"]["USA"])
        self.assertIn("featuredPath", result["sampleTournament"])


if __name__ == "__main__":
    unittest.main()
