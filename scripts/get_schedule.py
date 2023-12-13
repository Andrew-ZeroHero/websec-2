#                                             #
#       Returns schedule for this week        #
#                                             #
from json import dump, dumps
import re
import requests
import os
from time import sleep


def get_from(link: str, count=10) -> str:
    link_status = -1
    for i in range(count):
        reply = requests.get(link)
        link_status = reply.status_code
        if reply.status_code in range(200, 300):
            return reply.text
        sleep(1)
    print(f"Status {link_status}:", link)


def parser(url):
    data = {}
    page_raw = get_from(url)
    page_raw = re.sub("\n", " ", page_raw)

    # Title
    title = re.search('<h2 class="h2-text info-block__title">(.*?)</h2>', page_raw)
    data["title"] = title.group(1).strip()

    # School weeks
    weeks = re.findall("(\d{1,2}) неделя", page_raw)
    weeks = list(map(lambda x: int(x), weeks))
    data["weeks"] = weeks

    # Dates
    head_dates = re.findall("schedule__head-date.*?(\d{2}\.\d{2}\.\d{4})", page_raw)
    data["dates"] = head_dates

    # Navigation through weekdays
    weekdays = re.findall(
        'class="weekday-nav__item (weekday-nav__item_active|) " ><div class="caption-text weekday-nav__item-weekday"> ([а-я]+)</div><div class="subtitle-text weekday-nav__item-date"> ([\d]+)',
        page_raw,
    )
    print(weekdays)
    for i in range(len(weekdays)):
        weekdays[i] = list(weekdays[i])
        if weekdays[i][0] == "weekday-nav__item_active":
            weekdays[i][0] = "weekday-active"
    data["weekdays"] = weekdays

    data["rows"] = []

    # Lessons timespans
    time_spans = re.findall('"schedule__time".*?(\d\d:\d\d).*?(\d\d:\d\d)', page_raw)
    for t in time_spans:
        data["rows"].append({"timespan": t})

    # Schedule cells
    lesson_group = '(lesson-color-type-(\d)">([а-яА-Я ё-]+)</div><div class="caption-text schedule__place">([а-яА-ЯA-Z ё\d-]*)</div>(?:<div class="schedule__teacher"> *(?:<a class="caption-text" href=".*?(\?staffId=\d+)" >|)([\.а-яА-ЯA-Z ё\d-]*)|))'
    items = re.findall(
        '<div class="schedule__item (schedule__item_show|)">(.*?)</div>(?=<div class="schedule__item|</div></div></div></div><div class="footer">)',
        page_raw,
    )

    cells = []
    for i in items:
        is_showing = "s_item_show" if i[0] == "schedule__item_show" else ""
        print(i[0], is_showing)
        lessons = re.findall(lesson_group, i[1])
        cells.append(
            {
                "is_showing": is_showing,
                "lessons": [
                    {
                        "type": j[1],
                        "title": j[2],
                        "place": j[3],
                        "staffid": j[4],
                        "staff": j[5],
                    }
                    for j in lessons
                ],
            }
        )

    for i in range(len(time_spans)):
        data["rows"][i]["items"] = []
        for j in range(len(head_dates)):
            data["rows"][i]["items"].append(cells[i * len(head_dates) + j])

    with open("data\\schedule.json", "w", encoding="utf-8") as f:
        dump(data, f, indent=4, ensure_ascii=False)
