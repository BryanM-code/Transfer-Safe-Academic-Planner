import json
import os
from src.normalize import normalize_course

def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_data(data_dir: str):
    institutions = _read_json(os.path.join(data_dir, "institutions.json"))
    courses = _read_json(os.path.join(data_dir, "courses.json"))
    equivalencies = _read_json(os.path.join(data_dir, "equivalencies.json"))
    eligibility_rules = _read_json(os.path.join(data_dir, "eligibility_rules.json"))
    programs = _read_json(os.path.join(data_dir, "program_requirements.json"))

    if isinstance(eligibility_rules, dict):
        eligibility_rules = [dict(eligibility_rules, id="DEFAULT_RULE")]

    institutions = sorted(institutions, key=lambda inst: inst["name"])
    institutions_by_id = {inst["id"]: inst for inst in institutions}
    eligibility_by_id = {rule["id"]: rule for rule in eligibility_rules}

    courses_by_inst = {}
    course_units = {}
    for c in courses:
        inst = c["institution_id"]
        code = normalize_course(c["code"])
        courses_by_inst.setdefault(inst, []).append(code)
        course_units[(inst, code)] = c["units"]
    for inst in courses_by_inst:
        courses_by_inst[inst] = sorted(set(courses_by_inst[inst]))

    equiv_map = {}
    for e in equivalencies:
        key = (
            e["from_institution"],
            normalize_course(e["from_course"]),
            e["to_institution"],
        )
        existing = equiv_map.setdefault(key, [])
        for course in e["to_courses"]:
            normalized = normalize_course(course)
            if normalized not in existing:
                existing.append(normalized)

    normalized_programs = []
    for program in programs:
        source_requirements = {}
        for source_inst, requirement in program.get("source_requirements", {}).items():
            groups = {
                group_name: [normalize_course(course) for course in courses]
                for group_name, courses in requirement.get("groups", {}).items()
            }
            source_requirements[source_inst] = {
                "label": requirement.get("label") or f"{source_inst} preparation",
                "groups": groups,
            }

        normalized_programs.append(
            {
                **program,
                "eligibility_rule_id": program.get("eligibility_rule_id") or "DEFAULT_RULE",
                "source_requirements": source_requirements,
            }
        )

    normalized_programs = sorted(
        normalized_programs,
        key=lambda program: (
            institutions_by_id.get(program["to_institution"], {}).get("name", program["to_institution"]),
            program["program_name"],
            program["year"],
        ),
    )
    programs_by_id = {program["program_id"]: program for program in normalized_programs}

    return {
        "institutions": institutions,
        "institutions_by_id": institutions_by_id,
        "courses_by_inst": courses_by_inst,
        "course_units": course_units,
        "equiv_map": equiv_map,
        "eligibility_rules": eligibility_by_id,
        "programs": normalized_programs,
        "programs_by_id": programs_by_id,
    }
