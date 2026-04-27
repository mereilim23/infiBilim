from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from database import Database
from urllib.parse import quote, unquote
import json

app = FastAPI()

# ─── Database ───────────────────────────────────────────────
db = Database("data/users.db")
db.create_tables()

# ─── Templates & Static ────────────────────────────────────
env = Environment(loader=FileSystemLoader("templates"), cache_size=0)
env.globals.update({"url_for": app.url_path_for})
app.mount("/static", StaticFiles(directory="static"), name="static")


# ─── Helper Functions ──────────────────────────────────────
def get_username(cookie: str) -> str:
    try:
        return unquote(cookie)
    except:
        return "Пайдаланушы"


def make_cookie_response(content: str, name: str, role: str, user_id: int, redirect_url: str):
    response = HTMLResponse(
        content=f'<html><head><meta http-equiv="refresh" content="0;url={redirect_url}"></head><body></body></html>')
    response.set_cookie(key="user_name", value=quote(name), max_age=86400 * 7, path="/")
    response.set_cookie(key="user_role", value=role, max_age=86400 * 7, path="/")
    response.set_cookie(key="user_id", value=str(user_id), max_age=86400 * 7, path="/")
    return response


def render_template(request: Request, template: str, context: dict = None):
    if context is None:
        context = {}
    user_name = request.cookies.get("user_name", "")
    user_role = request.cookies.get("user_role", "")

    join_message = request.cookies.get("join_message", "")
    if join_message:
        try:
            join_message = unquote(join_message)
        except:
            pass

    context.update({
        "request": request,
        "user_name": get_username(user_name) if user_name else "Пайдаланушы",
        "user_role": user_role,
        "join_message": join_message
    })
    template_obj = env.get_template(template)
    content = template_obj.render(**context)

    if join_message:
        response = HTMLResponse(content)
        response.delete_cookie("join_message", path="/")
        return response

    return HTMLResponse(content)


# ─── Auth ─────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return render_template(request, "perv.html")


@app.get("/login", response_class=HTMLResponse)
def read_login(request: Request):
    return render_template(request, "autenti.html")


@app.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    if not username or not password:
        return render_template(request, "autenti.html", {"error": "Барлық өрістерді толтырыңыз!"})

    user = db.get_user_by_username(username)
    if user and user["password"] == password:
        redirect = "/teacher" if user["role"] == "teacher" else "/glav"
        return make_cookie_response("", user["name"], user["role"], user["id"], redirect)
    else:
        return render_template(request, "autenti.html", {"error": "Логин немесе құпия сөз қате!"})


@app.get("/register", response_class=HTMLResponse)
def read_register(request: Request):
    return render_template(request, "register.html")


@app.post("/register", response_class=HTMLResponse)
async def register_user(
        request: Request,
        name: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        role: str = Form(default="student")
):
    if not name or not username or not password:
        return render_template(request, "register.html", {"error": "Барлық өрістерді толтырыңыз!"})

    success = db.insert_user(name, username, password, role)
    if success:
        user = db.get_user_by_username(username)
        redirect = "/teacher" if role == "teacher" else "/glav"
        return make_cookie_response("", name, role, user["id"], redirect)
    else:
        return render_template(request, "register.html", {"error": "Бұл логин тіркелген!"})


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_name")
    response.delete_cookie("user_role")
    response.delete_cookie("user_id")
    response.delete_cookie("join_message")
    return response


# ─── Student Pages ─────────────────────────────────────────
@app.get("/glav", response_class=HTMLResponse)
def read_glav(request: Request):
    return render_template(request, "glav.html")


@app.get("/profile", response_class=HTMLResponse)
def read_profile(request: Request):
    return render_template(request, "profile.html")


@app.get("/certificates", response_class=HTMLResponse)
def read_certificates(request: Request):
    return render_template(request, "certificates.html")


@app.get("/topic", response_class=HTMLResponse)
def read_topic(request: Request):
    return render_template(request, "topic.html")


@app.get("/test", response_class=HTMLResponse)
def read_test(request: Request):
    return render_template(request, "test.html")


@app.post("/update-profile", response_class=HTMLResponse)
async def update_profile(request: Request, full_name: str = Form(...)):
    content = '<html><head><meta http-equiv="refresh" content="0;url=/profile"></head><body></body></html>'
    response = HTMLResponse(content=content)
    response.set_cookie(key="user_name", value=quote(full_name), max_age=86400 * 7, path="/")
    return response


# ─── Teacher Pages ─────────────────────────────────────────
@app.get("/teacher", response_class=HTMLResponse)
def teacher_dashboard(request: Request):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")
    if user_role != "teacher":
        return RedirectResponse(url="/glav", status_code=303)

    classes = db.get_teacher_classes(int(user_id)) if user_id else []
    return render_template(request, "teacher.html", {
        "classes": [dict(c) for c in classes]
    })


@app.post("/teacher/create-class", response_class=HTMLResponse)
async def create_class(request: Request, class_name: str = Form(...), class_level: int = Form(default=7)):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")
    if user_role != "teacher" or not user_id:
        return RedirectResponse(url="/login", status_code=303)

    db.create_class(class_name, int(user_id), class_level)
    return RedirectResponse(url="/teacher", status_code=303)


@app.get("/teacher/class/{class_id}", response_class=HTMLResponse)
def class_detail(class_id: int, request: Request):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")
    if user_role != "teacher":
        return RedirectResponse(url="/glav", status_code=303)

    class_ = db.get_class_by_id(class_id)
    if not class_ or class_["teacher_id"] != int(user_id):
        return RedirectResponse(url="/teacher", status_code=303)

    students = db.get_class_students(class_id)
    return render_template(request, "teacher_class.html", {
        "class": dict(class_),
        "students": [dict(s) for s in students]
    })


# ─── ASSIGNMENTS ──────────────────────────────────────────
@app.get("/assignments", response_class=HTMLResponse)
def student_assignments(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    return render_template(request, "student_assignments.html")


@app.post("/get-class-tasks", response_class=HTMLResponse)
async def get_class_tasks(request: Request, class_code: str = Form(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    class_ = db.get_class_by_code(class_code)
    if not class_:
        return render_template(request, "student_assignments.html", {
            "error": "Код табылмады ❌"
        })

    assignments = db.get_class_assignments(class_["id"])
    return render_template(request, "student_assignments.html", {
        "class": dict(class_),
        "assignments": [dict(a) for a in assignments]
    })


@app.get("/teacher/class/{class_id}/assignments", response_class=HTMLResponse)
def teacher_assignments(class_id: int, request: Request):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")

    if user_role != "teacher":
        return RedirectResponse(url="/glav", status_code=303)

    class_ = db.get_class_by_id(class_id)
    if not class_ or class_["teacher_id"] != int(user_id):
        return RedirectResponse(url="/teacher", status_code=303)

    assignments = db.get_class_assignments(class_id)
    return render_template(request, "teacher_assignments.html", {
        "class": dict(class_),
        "assignments": [dict(a) for a in assignments]
    })


@app.post("/teacher/class/{class_id}/create-assignment", response_class=HTMLResponse)
async def create_assignment(
        class_id: int,
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        due_date: str = Form(None)
):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")

    if user_role != "teacher":
        return RedirectResponse(url="/login", status_code=303)

    db.create_assignment(class_id, title, description, due_date)
    return RedirectResponse(url=f"/teacher/class/{class_id}/assignments", status_code=303)


# ─── Admin ────────────────────────────────────────────────
@app.get("/users")
def show_users():
    db.cur.execute("SELECT id, name, email, role FROM users")
    users = db.cur.fetchall()
    return {"users": [dict(u) for u in users]}


# ─── API Endpoints ─────────────────────────────────────────
@app.post("/api/save-test-result")
async def save_test_result_api(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return {"error": "Not authenticated"}

    try:
        data = await request.json()
        class_level = data.get("class_level")
        section_id = data.get("section_id")
        topic_id = data.get("topic_id")
        score = data.get("score")
        total = data.get("total")

        result = db.save_test_result(int(user_id), class_level, section_id,
                                     topic_id, score, total)
        return result
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/user-progress")
async def get_user_progress_api(request: Request):
    user_id = request.cookies.get("user_id")
    class_level = request.query_params.get("class_level")

    if not user_id or not class_level:
        return {"error": "Missing parameters"}

    progress = db.get_user_progress(int(user_id), int(class_level))
    certificates = db.get_user_certificates(int(user_id))

    return {
        "progress": progress,
        "certificates": [dict(c) for c in certificates]
    }


@app.get("/api/user-certificates")
async def get_user_certificates_api(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return {"error": "Not authenticated"}

    certificates = db.get_user_certificates(int(user_id))
    return {"certificates": [dict(c) for c in certificates]}


@app.get("/teacher/class/{class_id}/rating")
def class_rating(class_id: int, request: Request):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")

    if user_role != "teacher":
        return RedirectResponse(url="/glav", status_code=303)

    class_ = db.get_class_by_id(class_id)
    if not class_ or class_["teacher_id"] != int(user_id):
        return RedirectResponse(url="/teacher", status_code=303)

    students_rating = db.get_students_rating(class_id)
    class_stats = db.get_class_average_stats(class_id)

    return render_template(request, "teacher_rating.html", {
        "class": dict(class_),
        "students": students_rating,
        "stats": class_stats
    })


@app.get("/teacher/class/{class_id}/student/{student_id}")
def student_detail(class_id: int, student_id: int, request: Request):
    user_role = request.cookies.get("user_role", "")
    teacher_id = request.cookies.get("user_id", "")

    if user_role != "teacher":
        return RedirectResponse(url="/glav", status_code=303)

    class_ = db.get_class_by_id(class_id)
    if not class_ or class_["teacher_id"] != int(teacher_id):
        return RedirectResponse(url="/teacher", status_code=303)

    student = db.get_user_by_id(student_id)
    if not student:
        return RedirectResponse(url=f"/teacher/class/{class_id}/rating", status_code=303)

    progress = db.get_student_detailed_progress(student_id, class_id)

    return render_template(request, "teacher_student_detail.html", {
        "class": dict(class_),
        "student": dict(student),
        "progress": progress
    })


@app.get("/teacher/videos")
def teacher_videos(request: Request):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")

    if user_role != "teacher":
        return RedirectResponse(url="/glav", status_code=303)

    videos = db.get_teacher_videos(int(user_id))

    return render_template(request, "teacher_videos.html", {
        "videos": [dict(v) for v in videos]
    })


@app.post("/teacher/videos/add")
async def add_teacher_video(request: Request, title: str = Form(...),
                            url: str = Form(...), description: str = Form(None),
                            is_public: bool = Form(False)):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")

    if user_role != "teacher":
        return RedirectResponse(url="/login", status_code=303)

    db.add_teacher_video(int(user_id), title, url, description, is_public)
    return RedirectResponse(url="/teacher/videos", status_code=303)


@app.get("/api/class/{class_id}/rating")
def api_class_rating(class_id: int, request: Request):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")

    if user_role != "teacher":
        return {"error": "Unauthorized"}

    class_ = db.get_class_by_id(class_id)
    if not class_ or class_["teacher_id"] != int(user_id):
        return {"error": "Access denied"}

    section_id = request.query_params.get("section_id")
    if section_id:
        section_id = int(section_id)

    students_rating = db.get_students_rating(class_id, section_id)
    class_stats = db.get_class_average_stats(class_id, section_id)

    return {
        "students": students_rating,
        "stats": class_stats
    }


@app.get("/teacher/class/{class_id}/students-data")
def get_class_students_data(class_id: int, request: Request):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")

    if user_role != "teacher":
        return {"error": "Unauthorized"}

    class_ = db.get_class_by_id(class_id)
    if not class_ or class_["teacher_id"] != int(user_id):
        return {"error": "Access denied"}

    students = db.get_class_students(class_id)

    return {
        "students": [dict(s) for s in students],
        "count": len(students)
    }


@app.post("/join-class")
async def join_class(request: Request, invite_code: str = Form(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    result = db.join_class(int(user_id), invite_code)

    response = RedirectResponse(url="/glav", status_code=303)

    if result == "ok":
        response.set_cookie(key="join_message", value=quote("✅ Сыныпқа сәтті қосылдыңыз!"), max_age=5, path="/")
    elif result == "already_joined":
        response.set_cookie(key="join_message", value=quote("⚠️ Сіз бұл сыныпқа бұрын қосылғансыз!"), max_age=5, path="/")
    else:
        response.set_cookie(key="join_message", value=quote("❌ Код қате! Қайта тексеріңіз."), max_age=5, path="/")

    return response


@app.get("/teacher/class/{class_id}/section-rating/{section_id}", response_class=HTMLResponse)
def section_rating(class_id: int, section_id: int, request: Request):
    user_role = request.cookies.get("user_role", "")
    user_id = request.cookies.get("user_id", "")

    if user_role != "teacher":
        return RedirectResponse(url="/glav", status_code=303)

    class_ = db.get_class_by_id(class_id)
    if not class_ or class_["teacher_id"] != int(user_id):
        return RedirectResponse(url="/teacher", status_code=303)

    class_level = db.get_class_level(class_id)
    # Сынып деңгейіне сәйкес рұқсат етілген бөлімдер санын анықтаймыз
    max_sections = {7: 5, 8: 5, 9: 4}.get(class_level, 5)
    if section_id not in range(1, max_sections + 1):
        return RedirectResponse(url=f"/teacher/class/{class_id}/rating", status_code=303)

    section_data = db.get_section_rating(class_id, section_id)

    return render_template(request, "teacher_section_rating.html", {
        "class": dict(class_),
        "current_section": section_id,
        "section_data": section_data,
        "class_level": class_level
    })


# ─── Section Routes ─────────────────────────────────────────
@app.get("/topic_7_1bolim", response_class=HTMLResponse)
def read_topic_7_1bolim(request: Request):
    return render_template(request, "topic_7_1bolim.html")

@app.get("/topic_7_2bolim", response_class=HTMLResponse)
def read_topic_7_2bolim(request: Request):
    return render_template(request, "topic_7_2bolim.html")

@app.get("/topic_7_3bolim", response_class=HTMLResponse)
def read_topic_7_3bolim(request: Request):
    return render_template(request, "topic_7_3bolim.html")

@app.get("/topic_7_4bolim", response_class=HTMLResponse)
def read_topic_7_4bolim(request: Request):
    return render_template(request, "topic_7_4bolim.html")

@app.get("/topic_7_5bolim", response_class=HTMLResponse)
def read_topic_7_5bolim(request: Request):
    return render_template(request, "topic_7_5bolim.html")

# 8-сынып бөлімдерінің маршруттары
@app.get("/topic_8_1bolim", response_class=HTMLResponse)
def read_topic_8_1bolim(request: Request):
    return render_template(request, "topic_8_1bolim.html")

@app.get("/topic_8_2bolim", response_class=HTMLResponse)
def read_topic_8_2bolim(request: Request):
    return render_template(request, "topic_8_2bolim.html")

@app.get("/topic_8_3bolim", response_class=HTMLResponse)
def read_topic_8_3bolim(request: Request):
    return render_template(request, "topic_8_3bolim.html")

@app.get("/topic_8_4bolim", response_class=HTMLResponse)
def read_topic_8_4bolim(request: Request):
    return render_template(request, "topic_8_4bolim.html")

@app.get("/topic_8_5bolim", response_class=HTMLResponse)
def read_topic_8_5bolim(request: Request):
    return render_template(request, "topic_8_5bolim.html")

@app.get("/topic_9_1bolim", response_class=HTMLResponse)
def read_topic_8_1bolim(request: Request):
    return render_template(request, "topic_9_1bolim.html")

@app.get("/topic_9_2bolim", response_class=HTMLResponse)
def read_topic_8_2bolim(request: Request):
    return render_template(request, "topic_9_2bolim.html")

@app.get("/topic_9_3bolim", response_class=HTMLResponse)
def read_topic_8_3bolim(request: Request):
    return render_template(request, "topic_9_3bolim.html")

@app.get("/topic_9_4bolim", response_class=HTMLResponse)
def read_topic_8_4bolim(request: Request):
    return render_template(request, "topic_9_4bolim.html")

@app.get("/topic_9_5bolim", response_class=HTMLResponse)
def read_topic_8_5bolim(request: Request):
    return render_template(request, "topic_9_5bolim.html")