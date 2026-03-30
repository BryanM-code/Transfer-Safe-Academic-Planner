from pathlib import Path

from flask import Flask, render_template, request
from src.engine import build_report
from src.loaders import load_data

app = Flask(__name__)

DATA = load_data(str(Path(__file__).resolve().parent / "data"))

def parse_non_negative_int(value, default=0):
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return default

def institution_name(inst_id):
    return DATA["institutions_by_id"].get(inst_id, {}).get("name", inst_id)

def available_source_ids():
    source_ids = []
    for institution in DATA["institutions"]:
        inst_id = institution["id"]
        if institution["segment"] != "CCC":
            continue
        if inst_id not in DATA["courses_by_inst"]:
            continue
        if any(inst_id in program["source_requirements"] for program in DATA["programs"]):
            source_ids.append(inst_id)
    return source_ids

def available_destinations_for_source(source_id):
    destination_ids = []
    for institution in DATA["institutions"]:
        inst_id = institution["id"]
        if any(
            program["to_institution"] == inst_id and source_id in program["source_requirements"]
            for program in DATA["programs"]
        ):
            destination_ids.append(inst_id)
    return destination_ids

def available_programs(source_id, destination_id):
    return [
        program
        for program in DATA["programs"]
        if program["to_institution"] == destination_id and source_id in program["source_requirements"]
    ]

def resolve_selection(values):
    source_ids = available_source_ids()
    selected_source = values.get("from_inst")
    if selected_source not in source_ids:
        selected_source = source_ids[0] if source_ids else None

    destination_ids = available_destinations_for_source(selected_source) if selected_source else []
    selected_destination = values.get("to_inst")
    if selected_destination not in destination_ids:
        selected_destination = destination_ids[0] if destination_ids else None

    program_options = available_programs(selected_source, selected_destination) if selected_source and selected_destination else []
    selected_program_id = values.get("program_id")
    if selected_program_id not in {program["program_id"] for program in program_options}:
        selected_program_id = program_options[0]["program_id"] if program_options else None

    selected_program = DATA["programs_by_id"].get(selected_program_id) if selected_program_id else None
    eligibility_rule = DATA["eligibility_rules"].get(selected_program["eligibility_rule_id"]) if selected_program else None

    return {
        "source_options": [
            {"id": inst_id, "name": institution_name(inst_id)}
            for inst_id in source_ids
        ],
        "destination_options": [
            {"id": inst_id, "name": institution_name(inst_id)}
            for inst_id in destination_ids
        ],
        "program_options": program_options,
        "selected_source": selected_source,
        "selected_source_name": institution_name(selected_source) if selected_source else None,
        "selected_destination": selected_destination,
        "selected_destination_name": institution_name(selected_destination) if selected_destination else None,
        "selected_program_id": selected_program_id,
        "selected_program": selected_program,
        "golden_four": eligibility_rule["golden_four"] if eligibility_rule else [],
        "fc_courses": DATA["courses_by_inst"].get(selected_source, []),
    }

@app.get("/")
def index():
    selection = resolve_selection(request.args)
    return render_template("index.html", **selection)

@app.post("/report")
def report():
    selection = resolve_selection(request.form)
    completed = request.form.getlist("completed_courses")
    extra_units = parse_non_negative_int(request.form.get("extra_units", "0"))
    completed_g4 = request.form.getlist("golden_four")

    result = build_report(
        data=DATA,
        from_inst=selection["selected_source"],
        program_id=selection["selected_program_id"],
        completed_courses=completed,
        additional_units=extra_units,
        completed_golden_four=completed_g4
    )
    result["source_institution_name"] = institution_name(selection["selected_source"])
    result["destination_institution_name"] = institution_name(result["destination_institution_id"])
    return render_template("report.html", r=result)

if __name__ == "__main__":
    app.run(debug=True)
