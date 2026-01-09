import json

with open("transfer-data.json", "r") as f:
    data = json.load(f)

elig = data["eligibility"]

def to_set(s):
    # user types: CSCI 123 F, CSCI 133 F
    return {x.strip().upper() for x in s.split(",") if x.strip()}

print("Enter CS class codes you have completed at FC (comma separated):")
completed_cs = to_set(input("> "))

print("Enter math class codes you have completed at FC (comma separated):")
completed_math = to_set(input("> "))

print("Enter Golden Four you have completed (comma separated):")
completed_g4 = to_set(input("> "))

print("Enter completed units:")
completed_units = int(input("> "))

min_units_ok = completed_units >= elig["min_units"]

required_cs = {x.upper() for x in elig["required_cs_courses"]}
required_math = {x.upper() for x in elig["required_math_courses"]}
required_g4 = {x.upper() for x in elig["golden_four"]}

missing_cs = sorted(required_cs - completed_cs)
missing_math = sorted(required_math - completed_math)
missing_g4 = sorted(required_g4 - completed_g4)

if min_units_ok and not missing_cs and not missing_math and not missing_g4:
    print("\n You are eligible to transfer to", data["csu"]["name"])
else:
    print("\n You are not eligible to transfer yet.")
    if not min_units_ok:
        need = elig["min_units"] - completed_units
        print(f"- Units needed: {need}")
    if missing_cs:
        print("- Missing CS courses:", ", ".join(missing_cs))
    if missing_math:
        print("- Missing Math courses:", ", ".join(missing_math))
    if missing_g4:
        print("- Missing Golden Four:", ", ".join(missing_g4))
