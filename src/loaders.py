import json
import os
from src.normalize import normalize_course

def _read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def load_data(data_dir: str):
    institutions = _read_json(os.path.join(data_dir, "institutions.json"))
    courses = _read_json(os.path.join(data_dir, "courses.json"))
    equivalencies = _read_json(os.path.join(data_dir, "equivalencies.json"))
    eligibility = _read_json(os.path.join(data_dir, "eligibility_rules.json"))
    programs = _read_json(os.path.join(data_dir, "program_requirements.json"))

    courses_by_inst = {}
    for c in courses:
        inst = c["institution_id"]
        code = normalize_course(c["code"])
        courses_by_inst.setdefault(inst, []).append(code)
    for inst in courses_by_inst:
        courses_by_inst[inst] = sorted(set(courses_by_inst[inst]))

    equiv_map = {}
    for e in equivalencies:
        key = (
            e["from_institution"],
            normalize_course(e["from_course"]),
            e["to_institution"],
        )
        equiv_map[key] = [normalize_course(x) for x in e["to_courses"]]

    return {
        "institutions": institutions,
        "courses_by_inst": courses_by_inst,
        "equiv_map": equiv_map,
        "eligibility": eligibility,
        "programs": programs,
    }
