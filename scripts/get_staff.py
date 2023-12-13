#                                 #
#       Returns staff list        #
#                                 #
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


teachers = {}
template = "https://ssau.ru/staff?page={0}&letter=0"


raw = re.sub("\n", " ", get_from("https://ssau.ru/staff"))
page_max = max(list(map(lambda x: int(x), re.findall(r"(?<=page=)\d+", raw))))
for i in tqdm(range(page_max), desc="Processing staff"):
    tmp_raw = re.sub("\n", " ", get_from(template.format(i + 1)))
    tmp_info = re.findall(r"https://ssau.ru/staff/\d+.*?(?=</a>)", tmp_raw)
    for j in tmp_info:
        tmp = re.sub("-.+>", "", j)
        tmp = re.sub(r".*/", "", tmp).strip().split(" ", 1)
        teachers[tmp[1]] = tmp[0]


with open("data\\staff.json", "w") as f:
    json.dump(teachers, f, indent=4, ensure_ascii=False, sort_keys=True)
