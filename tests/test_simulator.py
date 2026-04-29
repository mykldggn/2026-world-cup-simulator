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
        self.assertIn(sample["champion"], {row["code"] for row in result["championOdds"]})


if __name__ == "__main__":
    unittest.main()
