from src.normalize import normalize_course

def get_equivalents(data, from_inst, to_inst, course):
    key = (from_inst, normalize_course(course), to_inst)
    return data["equiv_map"].get(key, [])

def build_report(data, from_inst, to_inst, completed_courses, completed_units, completed_golden_four):
    elig = data["eligibility"]
    g4_required = elig["golden_four"]

    completed_courses = [normalize_course(x) for x in completed_courses]
    completed_g4 = set(completed_golden_four)

    missing_units = max(0, int(elig["min_units"]) - int(completed_units))
    missing_g4 = [x for x in g4_required if x not in completed_g4]
    eligible_general = (missing_units == 0 and len(missing_g4) == 0)

    eq_rows = []
    completed_target = set()
    for c in completed_courses:
        eq = get_equivalents(data, from_inst, to_inst, c)
        if eq:
            completed_target.update(eq)
        eq_rows.append({"from": c, "to": eq})

   
    program = data["programs"][0] 
    req_cc = set(program["required_from_cc"]["cs"] + program["required_from_cc"]["math"])
    req_cc = {normalize_course(x) for x in req_cc}
    missing_cc = sorted(req_cc - set(completed_courses))

    return {
        "eligible_general": eligible_general,
        "missing_units": missing_units,
        "missing_g4": missing_g4,
        "equivalencies": eq_rows,
        "missing_cc_prep": missing_cc,
        "completed_target": sorted(completed_target),
    }
