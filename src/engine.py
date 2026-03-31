from src.normalize import normalize_course

def get_equivalents(data, from_inst, to_inst, course):
    key = (from_inst, normalize_course(course), to_inst)
    return data["equiv_map"].get(key, [])

def get_program(data, program_id):
    program = data["programs_by_id"].get(program_id)
    if not program:
        raise ValueError(f"No program requirements found for {program_id}")
    return program

def build_report(data, from_inst, program_id, completed_courses, additional_units, completed_golden_four):
    program = get_program(data, program_id)
    eligibility_rule = data["eligibility_rules"][program["eligibility_rule_id"]]
    g4_required = eligibility_rule["golden_four"]
    to_inst = program["to_institution"]

    completed_courses = [normalize_course(x) for x in completed_courses]
    unique_completed_courses = set(completed_courses)
    completed_g4 = set(completed_golden_four)
    additional_units = max(0, int(additional_units))
    selected_units = sum(
        data["course_units"].get((from_inst, course), 0) for course in unique_completed_courses
    )
    total_units = selected_units + additional_units

    missing_units = max(0, int(eligibility_rule["min_units"]) - total_units)
    missing_g4 = [x for x in g4_required if x not in completed_g4]
    eligible_general = (missing_units == 0 and len(missing_g4) == 0)

    eq_rows = []
    completed_target = set()
    for c in completed_courses:
        eq = get_equivalents(data, from_inst, to_inst, c)
        if eq:
            completed_target.update(eq)
        eq_rows.append({"from": c, "to": eq})

   
    source_requirement = program["source_requirements"].get(from_inst)
    prep_groups = []
    if source_requirement:
        req_cc = set()
        for group_name, courses in source_requirement["groups"].items():
            course_set = {normalize_course(course) for course in courses}
            req_cc.update(course_set)
            prep_groups.append(
                {
                    "group": group_name,
                    "missing": sorted(course_set - unique_completed_courses),
                    "completed": sorted(course_set & unique_completed_courses),
                }
            )
        missing_cc = sorted(req_cc - unique_completed_courses)
        prep_available = True
        prep_note = None
    else:
        missing_cc = []
        prep_available = False
        prep_note = "No major-prep course list is stored yet for this source school and program."

    return {
        "program": program,
        "eligibility_rule": eligibility_rule,
        "source_institution_id": from_inst,
        "destination_institution_id": to_inst,
        "eligible_general": eligible_general,
        "selected_units": selected_units,
        "additional_units": additional_units,
        "total_units": total_units,
        "missing_units": missing_units,
        "missing_g4": missing_g4,
        "equivalencies": eq_rows,
        "prep_available": prep_available,
        "prep_note": prep_note,
        "prep_groups": prep_groups,
        "missing_cc_prep": missing_cc,
        "completed_target": sorted(completed_target),
    }
