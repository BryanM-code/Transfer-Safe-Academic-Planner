import json
import unittest
from pathlib import Path
from uuid import uuid4

from app import app
from src.engine import build_report
from src.loaders import load_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TransferPlannerRegressionTests(unittest.TestCase):
    def test_build_report_counts_selected_course_units(self):
        result = build_report(
            data=load_data(str(PROJECT_ROOT / "data")),
            from_inst="FC",
            program_id="CSUF:CS:2026",
            completed_courses=["CSCI 123", "MATH 151"],
            additional_units=5,
            completed_golden_four=[],
        )

        self.assertEqual(result["selected_units"], 8)
        self.assertEqual(result["total_units"], 13)
        self.assertEqual(result["missing_units"], 47)

    def test_report_handles_invalid_extra_units_without_500(self):
        client = app.test_client()

        response = client.post(
            "/report",
            data={
                "from_inst": "FC",
                "to_inst": "CSUF",
                "program_id": "CSUF:CS:2026",
                "completed_courses": ["CSCI 123"],
                "extra_units": "not-a-number",
                "golden_four": ["Oral Communication"],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Units counted: 4 total", response.data)

    def test_load_data_merges_duplicate_equivalencies(self):
        tmp_path = PROJECT_ROOT / "tests" / f".tmp_loader_data_{uuid4().hex}"
        tmp_path.mkdir(parents=True)
        (tmp_path / "institutions.json").write_text(
            json.dumps([{"id": "FC", "name": "Fullerton College", "segment": "CCC"}]),
            encoding="utf-8",
        )
        (tmp_path / "courses.json").write_text(
            json.dumps([{"institution_id": "FC", "code": "CSCI 123", "units": 4}]),
            encoding="utf-8",
        )
        (tmp_path / "equivalencies.json").write_text(
            json.dumps(
                [
                    {
                        "from_institution": "FC",
                        "from_course": "CSCI 123",
                        "to_institution": "CSUF",
                        "to_courses": ["CPSC 121A"],
                    },
                    {
                        "from_institution": "FC",
                        "from_course": "CSCI 123",
                        "to_institution": "CSUF",
                        "to_courses": ["CPSC 121L"],
                    },
                ]
            ),
            encoding="utf-8",
        )
        (tmp_path / "eligibility_rules.json").write_text(
            json.dumps([{"id": "CSU_TRANSFER", "min_units": 60, "golden_four": []}]),
            encoding="utf-8",
        )
        (tmp_path / "program_requirements.json").write_text(
            json.dumps(
                [
                    {
                        "program_id": "CSUF:TEST:2026",
                        "to_institution": "CSUF",
                        "eligibility_rule_id": "CSU_TRANSFER",
                        "program_name": "Test Program",
                        "year": "2025-2026",
                        "source_requirements": {"FC": {"groups": {"Core": []}}},
                    }
                ]
            ),
            encoding="utf-8",
        )

        data = load_data(str(tmp_path))

        self.assertEqual(
            data["equiv_map"][("FC", "CSCI 123", "CSUF")],
            ["CPSC 121A", "CPSC 121L"],
        )

    def test_index_exposes_multiple_program_paths(self):
        client = app.test_client()
        response = client.get("/?from_inst=IVC&to_inst=CSUF&program_id=CSUF:BUS:2026")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Irvine Valley College", response.data)
        self.assertIn(b"Business Administration", response.data)


if __name__ == "__main__":
    unittest.main()
