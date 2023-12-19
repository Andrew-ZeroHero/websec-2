#                                                                                       #
#       Returns two lists: list of groups with faculties and just list of groups        #
#                                                                                       #
import re
import json
from tqdm import tqdm
import requests
import sys
import os
from time import sleep


def get_from(link: str, count=10) -> str:
    link_status: int
    for i in range(count):
        reply = requests.get(link)
        link_status = reply.status_code
        if reply.status_code in range(200, 300):
            return reply.text
        sleep(1)
    print(f"Status {link_status}:", link)
    sys.exit(os.EX_UNAVAILABLE)


raw = re.sub("\n", " ", get_from("https://ssau.ru/rasp"))
lines = re.findall('<a href="/rasp/faculty/\d+\?course=1" class="h3-text">.*?</a>', raw)
faculty = {}
groups = {}
for i in lines:
    new_name = re.findall(r"(?<=>).*?(?=<)", i)[0].strip()
    new_id = re.findall(r"\d+(?=\?)", i)[0]
    faculty[new_name] = {"id": new_id}

for name, fac in tqdm(faculty.items(), desc="Processing groups"):
    fac_id = fac["id"]
    faculty[name]["groups"] = {}
    raw = get_from(f"https://ssau.ru/rasp/faculty/{fac_id}?course=1")
    courses = list(map(lambda x: int(x), re.findall(r"(?<=course=)\d+", raw)))
    if len(courses) == 0:
        continue
    for course_id in courses:
        raw = get_from(f"https://ssau.ru/rasp/faculty/{fac_id}?course={course_id}")
        for i in re.findall(r"(?<=groupId=).*?\d{4}-\d{6}D", raw):
            t = re.sub('".*(?=\d{4}-\d{6}D)', " ", i).split()
            faculty[name]["groups"][t[1]] = t[0]
            groups[t[1]] = t[0]

    file1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/groups.json")
    file2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/groups_tmp.json")
    with open(file1, "w") as f:
        json.dump(faculty, f, indent=4, ensure_ascii=False, sort_keys=True)
    with open(file2, "w") as f:
        json.dump(groups, f, indent=4, ensure_ascii=False, sort_keys=True)
