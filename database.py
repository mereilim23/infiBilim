import sqlite3
import os
import random
import string
import hashlib
import time


class Database:
    def __init__(self, db_file: str):
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        print("✅ Database connected")

    def create_tables(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student'
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                teacher_id INTEGER NOT NULL,
                invite_code TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users(id)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS class_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id),
                FOREIGN KEY (student_id) REFERENCES users(id),
                UNIQUE(class_id, student_id)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes (id)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                class_level INTEGER NOT NULL,
                section_id INTEGER NOT NULL,
                topic_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage INTEGER NOT NULL,
                passed BOOLEAN DEFAULT 0,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, class_level, section_id, topic_id)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS section_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                class_level INTEGER NOT NULL,
                section_id INTEGER NOT NULL,
                avg_percentage INTEGER DEFAULT 0,
                is_completed BOOLEAN DEFAULT 0,
                certificate_issued BOOLEAN DEFAULT 0,
                certificate_issued_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, class_level, section_id)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                class_level INTEGER NOT NULL,
                section_id INTEGER NOT NULL,
                section_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                certificate_code TEXT UNIQUE NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS teacher_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                is_public BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users(id)
            )
        """)

        self.conn.commit()
        print("✅ Tables created/updated")

    def insert_user(self, name: str, username: str, password: str, role: str = 'student') -> bool:
        try:
            self.cur.execute(
                "INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)",
                (name, username, password, role)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_username(self, username: str):
        self.cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        return self.cur.fetchone()

    def get_user_by_id(self, user_id: int):
        self.cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return self.cur.fetchone()

    def generate_invite_code(self) -> str:
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.cur.execute("SELECT id FROM classes WHERE invite_code = ?", (code,))
            if not self.cur.fetchone():
                return code

    def create_class(self, name: str, teacher_id: int) -> dict:
        code = self.generate_invite_code()
        self.cur.execute(
            "INSERT INTO classes (name, teacher_id, invite_code) VALUES (?, ?, ?)",
            (name, teacher_id, code)
        )
        self.conn.commit()
        class_id = self.cur.lastrowid
        return {"id": class_id, "invite_code": code}

    def get_teacher_classes(self, teacher_id: int):
        self.cur.execute("""
            SELECT c.*, COUNT(cs.student_id) as student_count
            FROM classes c
            LEFT JOIN class_students cs ON c.id = cs.class_id
            WHERE c.teacher_id = ?
            GROUP BY c.id
        """, (teacher_id,))
        return self.cur.fetchall()

    def get_class_by_code(self, code: str):
        self.cur.execute("SELECT * FROM classes WHERE invite_code = ?", (code.upper(),))
        return self.cur.fetchone()

    def join_class(self, student_id: int, invite_code: str) -> str:
        class_ = self.get_class_by_code(invite_code)
        if not class_:
            return "not_found"
        try:
            self.cur.execute(
                "INSERT INTO class_students (class_id, student_id) VALUES (?, ?)",
                (class_["id"], student_id)
            )
            self.conn.commit()
            return "ok"
        except sqlite3.IntegrityError:
            return "already_joined"

    def get_class_by_id(self, class_id: int):
        self.cur.execute("SELECT * FROM classes WHERE id = ?", (class_id,))
        return self.cur.fetchone()

    def get_class_students(self, class_id: int):
        self.cur.execute("""
            SELECT u.id, u.name, u.username AS email, cs.joined_at
            FROM class_students cs
            JOIN users u ON cs.student_id = u.id
            WHERE cs.class_id = ?
        """, (class_id,))
        return self.cur.fetchall()

    def create_assignment(self, class_id: int, title: str, description: str, due_date: str = None):
        self.cur.execute("""
            INSERT INTO assignments (class_id, title, description, due_date)
            VALUES (?, ?, ?, ?)
        """, (class_id, title, description, due_date))
        self.conn.commit()
        return True

    def get_class_assignments(self, class_id: int):
        self.cur.execute("""
            SELECT * FROM assignments 
            WHERE class_id = ? 
            ORDER BY created_at DESC
        """, (class_id,))
        return self.cur.fetchall()

    def save_test_result(self, user_id: int, class_level: int, section_id: int,
                         topic_id: int, score: int, total: int) -> dict:
        percentage = int((score / total) * 100) if total > 0 else 0
        passed = percentage >= 70

        try:
            self.cur.execute("""
                INSERT INTO test_results (user_id, class_level, section_id, topic_id, 
                                          score, total_questions, percentage, passed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, class_level, section_id, topic_id) 
                DO UPDATE SET score = excluded.score, 
                              total_questions = excluded.total_questions,
                              percentage = excluded.percentage,
                              passed = excluded.passed,
                              completed_at = CURRENT_TIMESTAMP
            """, (user_id, class_level, section_id, topic_id, score, total, percentage, passed))
            self.conn.commit()

            return self.update_section_progress(user_id, class_level, section_id)
        except Exception as e:
            print(f"Error saving test result: {e}")
            return {"error": str(e)}

    def update_section_progress(self, user_id: int, class_level: int, section_id: int) -> dict:
        self.cur.execute("""
            SELECT topic_id, percentage, passed 
            FROM test_results 
            WHERE user_id = ? AND class_level = ? AND section_id = ?
        """, (user_id, class_level, section_id))

        results = self.cur.fetchall()

        if not results:
            return {
                "avg_percentage": 0,
                "is_completed": False,
                "total_topics": 0,
                "completed_topics": 0
            }

        # Получаем общее кол-во тем в разделе
        section_info = self.get_section_info(class_level, section_id)
        total_topics_in_section = section_info["topics"] if section_info else 5

        total_percentage = sum(r["percentage"] for r in results)
        avg_percentage = round(total_percentage / total_topics_in_section)

        # ✅ ИСПРАВЛЕНО: completed_topics — только те темы, которые реально прошли тест
        completed_topics = len(results)

        # ✅ ИСПРАВЛЕНО: раздел завершён только когда пройдены ВСЕ темы
        all_topics_done = completed_topics >= total_topics_in_section
        is_completed = all_topics_done and avg_percentage >= 70

        self.cur.execute("""
            INSERT INTO section_progress (user_id, class_level, section_id, 
                                          avg_percentage, is_completed)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, class_level, section_id) 
            DO UPDATE SET avg_percentage = excluded.avg_percentage,
                          is_completed = excluded.is_completed
        """, (user_id, class_level, section_id, avg_percentage, is_completed))
        self.conn.commit()

        # ✅ ИСПРАВЛЕНО: сертификат выдаётся только когда ВСЕ темы пройдены И avg >= 70
        certificate = None
        if all_topics_done and avg_percentage >= 70:
            certificate = self.check_and_issue_certificate(user_id, class_level, section_id)

        return {
            "avg_percentage": avg_percentage,
            "is_completed": is_completed,
            "total_topics": total_topics_in_section,
            "completed_topics": completed_topics,
            "certificate_code": certificate.get("certificate_code") if certificate else None
        }

    def check_and_issue_certificate(self, user_id: int, class_level: int, section_id: int):
        self.cur.execute("""
            SELECT id FROM certificates 
            WHERE user_id = ? AND class_level = ? AND section_id = ?
        """, (user_id, class_level, section_id))

        if self.cur.fetchone():
            return None

        section_info = self.get_section_info(class_level, section_id)
        if not section_info:
            return None

        self.cur.execute("""
            SELECT avg_percentage FROM section_progress 
            WHERE user_id = ? AND class_level = ? AND section_id = ?
        """, (user_id, class_level, section_id))

        progress = self.cur.fetchone()

        if not progress:
            self.cur.execute("""
                SELECT AVG(percentage) as avg_percentage
                FROM test_results 
                WHERE user_id = ? AND class_level = ? AND section_id = ?
            """, (user_id, class_level, section_id))
            avg_result = self.cur.fetchone()
            avg_percentage = int(avg_result["avg_percentage"]) if avg_result["avg_percentage"] else 0
        else:
            avg_percentage = progress["avg_percentage"]

        if avg_percentage < 70:
            return None

        cert_string = f"{user_id}{class_level}{section_id}{time.time()}"
        cert_code = hashlib.md5(cert_string.encode()).hexdigest()[:12].upper()

        self.cur.execute("""
            INSERT INTO certificates (user_id, class_level, section_id, section_name, 
                                      score, certificate_code)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, class_level, section_id, section_info["name"],
              avg_percentage, cert_code))
        self.conn.commit()

        return {
            "certificate_code": cert_code,
            "section_name": section_info["name"],
            "score": avg_percentage
        }

    def get_section_info(self, class_level: int, section_id: int) -> dict:
        sections = {
            7: {
                1: {"name": "Компьютерлік жад және оның өлшем бірліктері", "topics": 4},
                2: {"name": "Желі және қауіпсіздік", "topics": 3},
                3: {"name": "Электрондық кесте арқылы есептер шығару", "topics": 7},
                4: {"name": "Python тіліндегі алгоритмдерді программалау", "topics": 4},
                5: {"name": "Практикалық программалау", "topics": 4},
            }
        }
        return sections.get(class_level, {}).get(section_id)

    def get_user_progress(self, user_id: int, class_level: int):
        self.cur.execute("""
            SELECT section_id, topic_id, percentage, passed 
            FROM test_results 
            WHERE user_id = ? AND class_level = ?
            ORDER BY section_id, topic_id
        """, (user_id, class_level))

        results = self.cur.fetchall()

        sections_progress = {}
        for r in results:
            if r["section_id"] not in sections_progress:
                sections_progress[r["section_id"]] = {
                    "topics": [],
                    "total_percentage": 0
                }
            sections_progress[r["section_id"]]["topics"].append({
                "topic_id": r["topic_id"],
                "percentage": r["percentage"],
                "passed": r["passed"]
            })
            sections_progress[r["section_id"]]["total_percentage"] += r["percentage"]

        for section_id, data in sections_progress.items():
            section_info = self.get_section_info(class_level, section_id)
            total_topics_in_section = section_info["topics"] if section_info else 5

            if data["topics"]:
                topic_count = len(data["topics"])
                data["avg_percentage"] = round(data["total_percentage"] / total_topics_in_section)
                # ✅ ИСПРАВЛЕНО: раздел завершён только если пройдены ВСЕ темы
                data["is_completed"] = (topic_count >= total_topics_in_section) and (data["avg_percentage"] >= 70)
                # ✅ ИСПРАВЛЕНО: completed_topics — сколько тем реально прошёл тест
                data["completed_topics"] = topic_count
                data["total_topics"] = total_topics_in_section
            else:
                data["avg_percentage"] = 0
                data["is_completed"] = False
                data["completed_topics"] = 0
                data["total_topics"] = total_topics_in_section

        return sections_progress

    def get_user_certificates(self, user_id: int):
        self.cur.execute("""
            SELECT c.*, u.name as student_name
            FROM certificates c
            JOIN users u ON c.user_id = u.id
            WHERE c.user_id = ? 
            ORDER BY c.issued_at DESC
        """, (user_id,))
        return self.cur.fetchall()

    def get_class_with_details(self, class_id: int):
        self.cur.execute("""
            SELECT c.*, 
                   COUNT(DISTINCT cs.student_id) as total_students,
                   COUNT(DISTINCT a.id) as total_assignments
            FROM classes c
            LEFT JOIN class_students cs ON c.id = cs.class_id
            LEFT JOIN assignments a ON c.id = a.class_id
            WHERE c.id = ?
            GROUP BY c.id
        """, (class_id,))
        return self.cur.fetchone()

    def get_students_rating(self, class_id: int, section_id: int = None):
        self.cur.execute("""
            SELECT u.id, u.name, u.username AS email
            FROM class_students cs
            JOIN users u ON cs.student_id = u.id
            WHERE cs.class_id = ?
        """, (class_id,))

        students = self.cur.fetchall()
        rating_data = []

        for student in students:
            if section_id:
                self.cur.execute("""
                    SELECT section_id, topic_id, percentage, passed
                    FROM test_results
                    WHERE user_id = ? AND class_level = ?
                    ORDER BY section_id, topic_id
                """, (student["id"], self.get_class_level(class_id)))
            else:
                self.cur.execute("""
                    SELECT section_id, topic_id, percentage, passed
                    FROM test_results
                    WHERE user_id = ?
                    ORDER BY section_id, topic_id
                """, (student["id"],))

            results = self.cur.fetchall()

            if results:
                sections = {}
                for r in results:
                    if r["section_id"] not in sections:
                        sections[r["section_id"]] = []
                    sections[r["section_id"]].append(r["percentage"])

                section_averages = {}
                for sec_id, percentages in sections.items():
                    # ✅ ИСПРАВЛЕНО: делим на общее кол-во тем раздела (5), а не на пройденные
                    sec_info = self.get_section_info(self.get_class_level(class_id), sec_id)
                    section_averages[sec_id] = round(sum(percentages) / total_in_section)

                total_avg = round(sum(section_averages.values()) / len(section_averages)) if section_averages else 0
                # ✅ ИСПРАВЛЕНО: раздел завершён только если пройдены ВСЕ темы И avg >= 70
                completed_sections = sum(
                    1 for sec_id, avg in section_averages.items()
                    if avg >= 70 and len(sections[sec_id]) >= (
                        self.get_section_info(self.get_class_level(class_id), sec_id) or {"topics": 5}
                    )["topics"]
                )
                total_sections = len(section_averages)
            else:
                section_averages = {}
                total_avg = 0
                completed_sections = 0
                total_sections = 0

            rating_data.append({
                "id": student["id"],
                "name": student["name"],
                "email": student["email"],
                "total_avg": total_avg,
                "completed_sections": completed_sections,
                "total_sections": total_sections,
                "section_averages": section_averages
            })

        rating_data.sort(key=lambda x: x["total_avg"], reverse=True)
        for idx, student in enumerate(rating_data, 1):
            student["rating_position"] = idx

        return rating_data

    def get_class_level(self, class_id: int) -> int:
        return 7

    def get_class_average_stats(self, class_id: int, section_id: int = None):
        students = self.get_students_rating(class_id, section_id)

        if not students:
            return {
                "total_students": 0,
                "class_average": 0,
                "completed_percentage": 0,
                "top_student": None,
                "section_stats": {}
            }

        total_avg = round(sum(s["total_avg"] for s in students) / len(students))
        completed_count = sum(1 for s in students if s["total_avg"] >= 70)
        completed_percentage = (completed_count / len(students)) * 100

        section_stats = {}
        for student in students:
            for sec_id, avg in student["section_averages"].items():
                if sec_id not in section_stats:
                    section_stats[sec_id] = {"total": 0, "count": 0, "completed": 0}
                section_stats[sec_id]["total"] += avg
                section_stats[sec_id]["count"] += 1
                if avg >= 70:
                    section_stats[sec_id]["completed"] += 1

        for sec_id in section_stats:
            section_stats[sec_id]["average"] = round(section_stats[sec_id]["total"] / section_stats[sec_id]["count"])
            section_stats[sec_id]["completed_percentage"] = (section_stats[sec_id]["completed"] / section_stats[sec_id]["count"]) * 100

        return {
            "total_students": len(students),
            "class_average": total_avg,
            "completed_percentage": completed_percentage,
            "top_student": students[0] if students else None,
            "section_stats": section_stats
        }

    def get_teacher_videos(self, teacher_id: int):
        self.cur.execute("""
            SELECT * FROM teacher_videos 
            WHERE teacher_id = ? OR is_public = 1
            ORDER BY created_at DESC
        """, (teacher_id,))
        return self.cur.fetchall()

    def add_teacher_video(self, teacher_id: int, title: str, url: str, description: str = None, is_public: bool = False):
        self.cur.execute("""
            INSERT INTO teacher_videos (teacher_id, title, url, description, is_public)
            VALUES (?, ?, ?, ?, ?)
        """, (teacher_id, title, url, description, is_public))
        self.conn.commit()
        return self.cur.lastrowid

    def get_student_detailed_progress(self, student_id: int, class_id: int):
        class_level = self.get_class_level(class_id)

        self.cur.execute("""
            SELECT section_id, topic_id, score, total_questions, percentage, passed, completed_at
            FROM test_results
            WHERE user_id = ? AND class_level = ?
            ORDER BY section_id, topic_id
        """, (student_id, class_level))

        results = self.cur.fetchall()

        sections = {}
        for r in results:
            if r["section_id"] not in sections:
                sections[r["section_id"]] = {
                    "topics": [],
                    "total_percentage": 0,
                    "completed_at": None
                }
            sections[r["section_id"]]["topics"].append({
                "topic_id": r["topic_id"],
                "score": r["score"],
                "total": r["total_questions"],
                "percentage": r["percentage"],
                "passed": r["passed"],
                "completed_at": r["completed_at"]
            })
            sections[r["section_id"]]["total_percentage"] += r["percentage"]
            if r["completed_at"] and (not sections[r["section_id"]]["completed_at"] or r["completed_at"] > sections[r["section_id"]]["completed_at"]):
                sections[r["section_id"]]["completed_at"] = r["completed_at"]

        for sec_id in sections:
            if sections[sec_id]["topics"]:
                sec_info = self.get_section_info(class_level, sec_id)
                total_topics_in_section = sec_info["topics"] if sec_info else 5
                topic_count = len(sections[sec_id]["topics"])
                sections[sec_id]["avg_percentage"] = round(sections[sec_id]["total_percentage"] / total_topics_in_section)
                # ✅ ИСПРАВЛЕНО: завершён только если ВСЕ темы пройдены
                sections[sec_id]["is_completed"] = (
                    topic_count >= total_topics_in_section and
                    sections[sec_id]["avg_percentage"] >= 70
                )

        return sections

    def get_section_rating(self, class_id: int, section_id: int) -> list:
        """
        Бір бөлім бойынша барлық оқушылардың тақырыптар нәтижесін қайтарады.
        Нәтиже: [{ id, name, email, topics: {1: pct, 2: pct, ...}, avg, all_topics_done }]
        Орташа пайыз бойынша кемуші ретпен сұрыпталады.
        """
        class_level = self.get_class_level(class_id)
        sec_info = self.get_section_info(class_level, section_id)
        total_topics = sec_info["topics"] if sec_info else 5

        # topic_id -> local index (1,2,3...) mapping
        # Кейбір бөлімдерде topic_id глобальды болады (мыс. 5-бөлім: 19,20,21,22)
        # Шаблон 1,2,3,4 күтеді — сондықтан түрлендіреміз
        TOPIC_ID_MAP = {
            7: {
                1: {1: 1, 2: 2, 3: 3, 4: 4},
                2: {5: 1, 6: 2, 7: 3},
                3: {8: 1, 9: 2, 10: 3, 11: 4, 12: 5, 13: 6, 14: 7},
                4: {15: 1, 16: 2, 17: 3, 18: 4},
                5: {19: 1, 20: 2, 21: 3, 22: 4},
            }
        }
        topic_map = TOPIC_ID_MAP.get(class_level, {}).get(section_id, {})

        # Барлық оқушыларды аламыз
        self.cur.execute("""
            SELECT u.id, u.name, u.username AS email
            FROM class_students cs
            JOIN users u ON cs.student_id = u.id
            WHERE cs.class_id = ?
            ORDER BY u.name
        """, (class_id,))
        students = self.cur.fetchall()

        result = []
        for student in students:
            # Осы бөлім бойынша тест нәтижелерін аламыз
            self.cur.execute("""
                SELECT topic_id, percentage
                FROM test_results
                WHERE user_id = ? AND class_level = ? AND section_id = ?
                ORDER BY topic_id
            """, (student["id"], class_level, section_id))
            rows = self.cur.fetchall()

            topics_map = {}
            total_pct = 0
            for r in rows:
                raw_id = r["topic_id"]
                # Локальды индекске түрлендіру: маппинг бар болса қолдан, жоқ болса as-is
                local_idx = topic_map.get(raw_id, raw_id)
                topics_map[local_idx] = r["percentage"]
                total_pct += r["percentage"]

            avg = round(total_pct / total_topics)
            all_topics_done = len(topics_map) >= total_topics

            result.append({
                "id": student["id"],
                "name": student["name"],
                "email": student["email"],
                "topics": topics_map,
                "avg": avg,
                "all_topics_done": all_topics_done,
                "done_count": len(topics_map),
                "total_topics": total_topics
            })

        # Орташа бойынша кемуші ретпен сұрыптаймыз
        result.sort(key=lambda x: x["avg"], reverse=True)
        return result

    def close(self):
        self.cur.close()
        self.conn.close()