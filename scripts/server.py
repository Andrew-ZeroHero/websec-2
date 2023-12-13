#                                       #
#       Main script for lab work        #
#                                       #
from flask import Flask, request, render_template, redirect
from json import load, dumps
import ast
import get_schedule

app = Flask(__name__, static_folder="static")


@app.route("/")
@app.route("/faculties")
def post_faculties():
    with open("data\\groups.json", encoding="utf-8") as f:
        data = load(f)

    faculties = {}
    for faculty, groups in data.items():
        faculties[faculty] = groups["id"]
    return render_template("faculties.html", faculties=faculties)


@app.route("/search")
def post_search():
    searchText = request.args.get("searchText", type=str)

    with open("data\\groups_tmp.json", encoding="utf-8") as f:
        data1 = load(f)
    with open("data\\staff.json", encoding="utf-8") as f:
        data2 = load(f)

    searchGroups = {}
    for group, id in data1.items():
        if searchText in group:
            searchGroups[group] = id

    staff = {}
    for teacher, id in data2.items():
        if searchText in teacher:
            staff[teacher] = id
    return render_template(
        "search.html", staff=staff, groups=searchGroups, searchText=searchText
    )


@app.route("/staff")
def post_staff():
    with open("data\\staff.json", encoding="utf-8") as f:
        data = load(f)

    staff = {}
    for teacher, id in data.items():
        staff[teacher] = id
    return render_template("staff.html", staff=staff)


@app.route("/faculties/<int:facultyId>/groups")
def post_groups(facultyId):
    with open("data\\groups.json", encoding="utf-8") as f:
        data = load(f)

    for faculty, grouplist in data.items():
        if int(grouplist["id"]) == facultyId:
            return render_template("groups.html", groups=grouplist["groups"])

    return redirect(f"/faculties/{facultyId}", 404)


@app.route("/schedule/groups")
def post_schedule():
    groupId = request.args.get("groupId", type=str)
    week = request.args.get("week", type=int)
    if week is None:
        url = f"https://ssau.ru/rasp?groupId={groupId}"
    else:
        url = f"https://ssau.ru/rasp?groupId={groupId}&selectedWeek={str(week)}&selectedWeekday=1"
    get_schedule.parser(url)
    with open("data\\schedule.json", encoding="utf-8") as f:
        schedule = load(f)

    return render_template(
        "schedule.html",
        groupId=groupId,
        title=schedule["title"],
        weeks=schedule["weeks"],
        dates=schedule["dates"],
        rows=schedule["rows"],
    )


@app.route("/schedule/staff")
def post_staff_schedule():
    print(123)
    staffId = request.args.get("staffId", type=str)
    week = request.args.get("week", type=int)

    if week is None:
        url = f"https://ssau.ru/rasp?staffId={staffId}"
    else:
        url = f"https://ssau.ru/rasp?staffId={staffId}&selectedWeek={str(week)}&selectedWeekday=1"

    get_schedule.parser(url)
    with open("data\\schedule.json", encoding="utf-8") as f:
        schedule = load(f)

    return render_template(
        "staff_schedule.html",
        staffId=staffId,
        title=schedule["title"],
        weeks=schedule["weeks"],
        dates=schedule["dates"],
        rows=schedule["rows"],
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
