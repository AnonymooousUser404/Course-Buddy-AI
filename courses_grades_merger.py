import json
import re
# Instead of storing grades as a list, concatenate their string representations with '|' as separator

def doc_to_grade_string(doc):
    # Convert a grade doc dict to a readable string
    # Example: "Year: 2023, Semester: 1, Instructor: I - A.M.Pradeep, Grades: BB:4, BC:1, CC:2, CD:1, FF:2, Total:10"
    year = doc.get('year', '')
    semester = doc.get('semester', '')
    instructor = doc.get('Instructor', '')
    # Collect all grade keys (skip known non-grade keys)
    skip_keys = {'course_name', 'year', 'semester', 'title', 'Instructor', 'Total'}
    grade_items = []
    for k, v in doc.items():
        if k not in skip_keys and isinstance(v, str) and v.isdigit():
            grade_items.append(f"{k}:{v}")
    grades_str = ', '.join(grade_items)
    total = doc.get('Total', '')
    if total:
        grades_str += f", Total:{total}"
    # Compose the string
    parts = []
    if year: parts.append(f"Year: {year}")
    if semester: parts.append(f"Semester: {semester}")
    if instructor: parts.append(f"Instructor: {instructor}")
    if grades_str: parts.append(f"Grades: {grades_str}")
    return ', '.join(parts)

# Load courses.json
with open('Courses.json', 'r', encoding='utf-8') as f:
    courses_data = json.load(f)

# Load grades.json
with open('insti_gpt_files/grades.json', 'r', encoding='utf-8') as f:
    grades_data = json.load(f)

# Helper: normalize course code (remove spaces, upper case)
def normalize_code(name):
    return re.sub(r'\s+', '', name).upper()

# Build a mapping from normalized course code to grades
grades_by_code = {}
for entry in grades_data:
    doc = entry.get('doc', {})
    course_name = doc.get('course_name', '')
    code = normalize_code(course_name)
    # Store all grade entries for this code
    if code not in grades_by_code:
        grades_by_code[code] = []
    grades_by_code[code].append(doc)

# Merge grades into courses
courses_with_grades = {}
for code, course in courses_data.items():
    norm_code = normalize_code(code)
    # Try to find grades for this course code
    grades_docs = grades_by_code.get(norm_code, [])
    # Convert each doc to a string and concatenate with '|'
    grades_strings = [doc_to_grade_string(doc) for doc in grades_docs]
    grades_concat = ' \n '.join(grades_strings) if grades_strings else ""
    # Attach grades info to the course dict
    course_with_grades = dict(course)  # shallow copy
    course_with_grades['grades'] = grades_concat
    courses_with_grades[code] = course_with_grades

# Write to course_with_grades.json
with open('course_with_grades.json', 'w', encoding='utf-8') as f:
    json.dump(courses_with_grades, f, indent=4, ensure_ascii=False)
