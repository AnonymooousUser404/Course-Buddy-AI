import json
import os

# Paths to the files
resobin_courses_path = os.path.join("insti_gpt_files", "resobin_courses_final.json")
courses_json_path = "courses.json"

# Load resobin_courses_final.json
with open(resobin_courses_path, "r", encoding="utf-8") as f:
    resobin_courses = json.load(f)

print(f"Loaded resobin_courses, type: {type(resobin_courses)}")
print(f"Length: {len(resobin_courses)}")
print(f"First item type: {type(resobin_courses[0]) if resobin_courses else 'None'}")
if resobin_courses:
    print(f"First item keys: {list(resobin_courses[0].keys()) if isinstance(resobin_courses[0], dict) else 'Not a dict'}")

# Build a mapping from course_code to tags (as comma-separated string)
course_tags_map = {}
for i, course in enumerate(resobin_courses):
    try:
        # Access the nested structure
        if isinstance(course, dict) and "doc" in course:
            doc = course["doc"]
            course_code = doc.get("code")
            tags = doc.get("tags", [])
            
            # Convert tags list to comma-separated string
            tags_str = ",".join(tags) if tags else ""
            
            if course_code:
                course_tags_map[course_code] = tags_str
        else:
            print(f"Warning: Course {i} is not in expected format: {type(course)}")
            if isinstance(course, dict):
                print(f"  Keys: {list(course.keys())}")
    except Exception as e:
        print(f"Error processing course {i}: {e}")
        print(f"  Course data: {course}")

print(f"\nFound {len(course_tags_map)} courses with tags")

# Load courses.json
with open(courses_json_path, "r", encoding="utf-8") as f:
    courses_data = json.load(f)

# Update tags in courses.json
updated_count = 0
for code, tags_str in course_tags_map.items():
    if code in courses_data:
        # Convert comma-separated string back to list for consistency
        tags_list = tags_str.split(",") if tags_str else []
        courses_data[code]["tags"] = tags_list
        updated_count += 1

# Write back the updated courses.json
with open(courses_json_path, "w", encoding="utf-8") as f:
    json.dump(courses_data, f, indent=4, ensure_ascii=False)

print(f"\nUpdated {updated_count} courses with tags")
print("Sample updates:")
for code, tags in list(course_tags_map.items())[:5]:
    print(f"  {code}: {tags}")
