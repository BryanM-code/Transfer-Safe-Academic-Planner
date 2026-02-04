from flask import Flask, render_template, request
from src.engine import build_report
from src.loaders import load_data

app = Flask(__name__)

DATA = load_data("data")  

@app.get("/")
def index():
    fc_courses = DATA["courses_by_inst"].get("FC", [])
    g4 = DATA["eligibility"]["golden_four"]
    return render_template("index.html", fc_courses=fc_courses, golden_four=g4)

@app.post("/report")
def report():
    completed = request.form.getlist("completed_courses")
    units = int(request.form.get("units", "0"))
    completed_g4 = request.form.getlist("golden_four")

    result = build_report(
        data=DATA,
        from_inst="FC",
        to_inst="CSUF",
        completed_courses=completed,
        completed_units=units,
        completed_golden_four=completed_g4
    )
    return render_template("report.html", r=result)

if __name__ == "__main__":
    app.run(debug=True)
