# Transfer-Safe-Academic-Planner

Helps community college students build reliable, data-driven transfer plans for 4-year universities.

## Features
- Select a current school and a target school  
  `Example: Fullerton College → California State University, Fullerton`
- Enter completed and required courses along with total credits.
- The system determines transfer eligibility by matching coursework with the selected school's requirements.

## Tech Stack 
- Python
- Flask
- HTML, CSS

## Tools Used
- AI tools (Codex) were used to assist with frontend design and for testing.

## How It Works

- The user selects a current school and a target university, then inputs completed courses and total units.
- Input is normalized to ensure consistent formatting for comparison.
- The system loads academic data from JSON files, including course equivalencies, program requirements, and eligibility rules.
- A decision engine compares the user's coursework against transfer requirements.
- The system outputs whether the student meets transfer eligibility criteria.

## Notes
- Only a limited number of schools are currently supported.
- Only selected majors and their corresponding courses are available.
