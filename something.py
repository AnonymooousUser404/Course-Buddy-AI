import json
from langchain_community.document_loaders import JSONLoader
loader = JSONLoader(
    file_path='courses.json',
    jq_schema='.[]',
    text_content=False
)
docs = loader.load()
department_names = {}
for doc in docs:
    temp = json.loads(doc.page_content)
    for key,value in temp.items():
        if(key == "department" and value not in department_names):
            department_names[value] = []

print(department_names)