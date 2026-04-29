import os
import random
import string
import hashlib
import time
import psycopg2
import psycopg2.extras


class Database:
    def __init__(self):
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise Exception("DATABASE_URL environment variable is not set!")

        self.conn = psycopg2.connect(db_url)
        self.conn.autocommit = False
        print("✅ Database connected (PostgreSQL)")

    def _cur(self):
        """Returns a new dict-cursor, reconnecting if needed."""
        try:
            self.conn.isolation_level  # ping
        except Exception:
            db_url = os.environ.get("DATABASE_URL")
            self.conn = psycopg2.connect(db_url)
        return self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def _exec(self, sql, params=None, fetch=None):
        """
        Execute SQL, commit, and optionally fetch results.
        fetch: None | 'one' | 'all'
        """
        # Replace SQLite placeholders ? with PostgreSQL %s
        if params:
            sql = sql.replace("?", "%s")
        cur = self._cur()
        try:
            cur.execute(sql, params)
            self.conn.commit()
            if fetch == 'one':
                return cur.fetchone()
            if fetch == 'all':
                return cur.fetchall()
            return cur
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def create_tables(self):
        cur = self._cur()
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'student'
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    invite_code TEXT NOT NULL UNIQUE,
                    class_level INTEGER NOT NULL DEFAULT 7,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES users(id)
                )
            """)

            # Add class_level column if it doesn't exist (for old DBs)
            try:
                cur.execute("ALTER TABLE classes ADD COLUMN IF NOT EXISTS class_level INTEGER NOT NULL DEFAULT 7")
            except Exception:
                pass

            cur.execute("""
                CREATE TABLE IF NOT EXISTS class_students (
                    id SERIAL PRIMARY KEY,
                    class_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (class_id) REFERENCES classes(id),
                    FOREIGN KEY (student_id) REFERENCES users(id),
                    UNIQUE(class_id, student_id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS assignments (
                    id SERIAL PRIMARY KEY,
                    class_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (class_id) REFERENCES classes(id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    class_level INTEGER NOT NULL,
                    section_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    percentage INTEGER NOT NULL,
                    passed BOOLEAN DEFAULT FALSE,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, class_level, section_id, topic_id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS section_progress (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    class_level INTEGER NOT NULL,
                    section_id INTEGER NOT NULL,
                    avg_percentage INTEGER DEFAULT 0,
                    is_completed BOOLEAN DEFAULT FALSE,
                    certificate_issued BOOLEAN DEFAULT FALSE,
                    certificate_issued_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, class_level, section_id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS certificates (
                    id SERIAL PRIMARY KEY,
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

            cur.execute("""
                CREATE TABLE IF NOT EXISTS teacher_videos (
                    id SERIAL PRIMARY KEY,
                    teacher_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES users(id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    user_id INTEGER PRIMARY KEY,
                    is_active BOOLEAN DEFAULT FALSE,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            self.conn.commit()
            print("✅ Tables created/updated")
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def insert_user(self, name: str, username: str, password: str, role: str = 'student') -> bool:
        try:
            self._exec(
                "INSERT INTO users (name, username, password, role) VALUES (%s, %s, %s, %s)",
                (name, username, password, role)
            )
            return True
        except Exception:
            return False

    def get_user_by_username(self, username: str):
        return self._exec("SELECT * FROM users WHERE username = %s", (username,), fetch='one')

    def get_user_by_id(self, user_id: int):
        return self._exec("SELECT * FROM users WHERE id = %s", (user_id,), fetch='one')

    def generate_invite_code(self) -> str:
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            result = self._exec("SELECT id FROM classes WHERE invite_code = %s", (code,), fetch='one')
            if not result:
                return code

    def create_class(self, name: str, teacher_id: int, class_level: int = 7) -> dict:
        code = self.generate_invite_code()
        cur = self._cur()
        try:
            cur.execute(
                "INSERT INTO classes (name, teacher_id, invite_code, class_level) VALUES (%s, %s, %s, %s) RETURNING id",
                (name, teacher_id, code, class_level)
            )
            row = cur.fetchone()
            self.conn.commit()
            return {"id": row["id"], "invite_code": code}
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def get_teacher_classes(self, teacher_id: int):
        return self._exec("""
            SELECT c.*, COUNT(cs.student_id) as student_count
            FROM classes c
            LEFT JOIN class_students cs ON c.id = cs.class_id
            WHERE c.teacher_id = %s
            GROUP BY c.id
        """, (teacher_id,), fetch='all')

    def get_class_by_code(self, code: str):
        return self._exec("SELECT * FROM classes WHERE invite_code = %s", (code.upper(),), fetch='one')

    def join_class(self, student_id: int, invite_code: str) -> str:
        class_ = self.get_class_by_code(invite_code)
        if not class_:
            return "not_found"
        try:
            self._exec(
                "INSERT INTO class_students (class_id, student_id) VALUES (%s, %s)",
                (class_["id"], student_id)
            )
            return "ok"
        except Exception:
            return "already_joined"

    def get_class_by_id(self, class_id: int):
        return self._exec("SELECT * FROM classes WHERE id = %s", (class_id,), fetch='one')

    def get_class_students(self, class_id: int):
        return self._exec("""
            SELECT u.id, u.name, u.username AS email, u.password,
                   cs.joined_at,
                   COALESCE(ua.is_active, FALSE) AS is_active,
                   ua.last_seen
            FROM class_students cs
            JOIN users u ON cs.student_id = u.id
            LEFT JOIN user_activity ua ON ua.user_id = u.id
            WHERE cs.class_id = %s
        """, (class_id,), fetch='all')

    def set_user_active(self, user_id: int, is_active: bool):
        self._exec("""
            INSERT INTO user_activity (user_id, is_active, last_seen)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                is_active = EXCLUDED.is_active,
                last_seen = CURRENT_TIMESTAMP
        """, (user_id, is_active))

    def get_active_students(self, class_id: int):
        return self._exec("""
            SELECT u.id, ua.is_active, ua.last_seen
            FROM class_students cs
            JOIN users u ON cs.student_id = u.id
            LEFT JOIN user_activity ua ON ua.user_id = u.id
            WHERE cs.class_id = %s
        """, (class_id,), fetch='all')

    def create_assignment(self, class_id: int, title: str, description: str, due_date: str = None):
        self._exec("""
            INSERT INTO assignments (class_id, title, description, due_date)
            VALUES (%s, %s, %s, %s)
        """, (class_id, title, description, due_date))
        return True

    def get_class_assignments(self, class_id: int):
        return self._exec("""
            SELECT * FROM assignments 
            WHERE class_id = %s 
            ORDER BY created_at DESC
        """, (class_id,), fetch='all')

    def save_test_result(self, user_id: int, class_level: int, section_id: int,
                         topic_id: int, score: int, total: int) -> dict:
        percentage = int((score / total) * 100) if total > 0 else 0
        passed = percentage >= 70

        try:
            self._exec("""
                INSERT INTO test_results (user_id, class_level, section_id, topic_id, 
                                          score, total_questions, percentage, passed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT(user_id, class_level, section_id, topic_id) 
                DO UPDATE SET score = EXCLUDED.score, 
                              total_questions = EXCLUDED.total_questions,
                              percentage = EXCLUDED.percentage,
                              passed = EXCLUDED.passed,
                              completed_at = CURRENT_TIMESTAMP
            """, (user_id, class_level, section_id, topic_id, score, total, percentage, passed))

            return self.update_section_progress(user_id, class_level, section_id)
        except Exception as e:
            print(f"Error saving test result: {e}")
            return {"error": str(e)}

    def update_section_progress(self, user_id: int, class_level: int, section_id: int) -> dict:
        results = self._exec("""
            SELECT topic_id, percentage, passed 
            FROM test_results 
            WHERE user_id = %s AND class_level = %s AND section_id = %s
        """, (user_id, class_level, section_id), fetch='all')

        if not results:
            return {"avg_percentage": 0, "is_completed": False, "total_topics": 0, "completed_topics": 0}

        section_info = self.get_section_info(class_level, section_id)
        total_topics_in_section = section_info["topics"] if section_info else 5
        total_percentage = sum(r["percentage"] for r in results)
        avg_percentage = round(total_percentage / total_topics_in_section)
        completed_topics = len(results)
        all_topics_done = completed_topics >= total_topics_in_section
        is_completed = all_topics_done and avg_percentage >= 70

        self._exec("""
            INSERT INTO section_progress (user_id, class_level, section_id, avg_percentage, is_completed)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT(user_id, class_level, section_id) 
            DO UPDATE SET avg_percentage = EXCLUDED.avg_percentage,
                          is_completed = EXCLUDED.is_completed
        """, (user_id, class_level, section_id, avg_percentage, is_completed))

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
        existing = self._exec("""
            SELECT id FROM certificates 
            WHERE user_id = %s AND class_level = %s AND section_id = %s
        """, (user_id, class_level, section_id), fetch='one')
        if existing:
            return None

        section_info = self.get_section_info(class_level, section_id)
        if not section_info:
            return None

        progress = self._exec("""
            SELECT avg_percentage FROM section_progress 
            WHERE user_id = %s AND class_level = %s AND section_id = %s
        """, (user_id, class_level, section_id), fetch='one')

        if not progress:
            avg_result = self._exec("""
                SELECT AVG(percentage) as avg_percentage
                FROM test_results 
                WHERE user_id = %s AND class_level = %s AND section_id = %s
            """, (user_id, class_level, section_id), fetch='one')
            avg_percentage = int(avg_result["avg_percentage"]) if avg_result and avg_result["avg_percentage"] else 0
        else:
            avg_percentage = progress["avg_percentage"]

        if avg_percentage < 70:
            return None

        cert_string = f"{user_id}{class_level}{section_id}{time.time()}"
        cert_code = hashlib.md5(cert_string.encode()).hexdigest()[:12].upper()

        self._exec("""
            INSERT INTO certificates (user_id, class_level, section_id, section_name, score, certificate_code)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, class_level, section_id, section_info["name"], avg_percentage, cert_code))

        return {"certificate_code": cert_code, "section_name": section_info["name"], "score": avg_percentage}

    def get_section_info(self, class_level: int, section_id: int) -> dict:
        sections = {
            7: {
                1: {"name": "Компьютерлік жад және оның өлшем бірліктері", "topics": 4},
                2: {"name": "Желі және қауіпсіздік", "topics": 3},
                3: {"name": "Электрондық кесте арқылы есептер шығару", "topics": 7},
                4: {"name": "Python тіліндегі алгоритмдерді программалау", "topics": 4},
                5: {"name": "Практикалық программалау", "topics": 4},
            },
            8: {
                1: {"name": "Компьютер мен желілердің техникалық сипаттамалары", "topics": 5},
                2: {"name": "Денсаулық және қауіпсіздік", "topics": 2},
                3: {"name": "Ақпаратты электронды кестелерде өңдеу", "topics": 5},
                4: {"name": "Python тіліндегі алгоритмдерді программалау", "topics": 7},
                5: {"name": "Практикалық программалау", "topics": 5},
            },
            9: {
                1: {"name": "Ақпаратпен жұмыс жасау", "topics": 4},
                2: {"name": "Компьютер таңдаймыз", "topics": 3},
                3: {"name": "Деректер базасы", "topics": 5},
                4: {"name": "Python тіліндегі алгоритмдерді программалау", "topics": 8},
            }
        }
        return sections.get(class_level, {}).get(section_id)

    def get_user_progress(self, user_id: int, class_level: int):
        results = self._exec("""
            SELECT section_id, topic_id, percentage, passed 
            FROM test_results 
            WHERE user_id = %s AND class_level = %s
            ORDER BY section_id, topic_id
        """, (user_id, class_level), fetch='all')

        sections_progress = {}
        for r in results:
            if r["section_id"] not in sections_progress:
                sections_progress[r["section_id"]] = {"topics": [], "total_percentage": 0}
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
                data["is_completed"] = (topic_count >= total_topics_in_section) and (data["avg_percentage"] >= 70)
                data["completed_topics"] = topic_count
                data["total_topics"] = total_topics_in_section
            else:
                data["avg_percentage"] = 0
                data["is_completed"] = False
                data["completed_topics"] = 0
                data["total_topics"] = total_topics_in_section

        return sections_progress

    def get_user_certificates(self, user_id: int):
        return self._exec("""
            SELECT c.*, u.name as student_name
            FROM certificates c
            JOIN users u ON c.user_id = u.id
            WHERE c.user_id = %s 
            ORDER BY c.issued_at DESC
        """, (user_id,), fetch='all')

    def get_class_with_details(self, class_id: int):
        return self._exec("""
            SELECT c.*, 
                   COUNT(DISTINCT cs.student_id) as total_students,
                   COUNT(DISTINCT a.id) as total_assignments
            FROM classes c
            LEFT JOIN class_students cs ON c.id = cs.class_id
            LEFT JOIN assignments a ON c.id = a.class_id
            WHERE c.id = %s
            GROUP BY c.id
        """, (class_id,), fetch='one')

    def get_students_rating(self, class_id: int, section_id: int = None):
        students = self._exec("""
            SELECT u.id, u.name, u.username AS email
            FROM class_students cs
            JOIN users u ON cs.student_id = u.id
            WHERE cs.class_id = %s
        """, (class_id,), fetch='all')

        rating_data = []
        for student in students:
            if section_id:
                results = self._exec("""
                    SELECT section_id, topic_id, percentage, passed
                    FROM test_results
                    WHERE user_id = %s AND class_level = %s
                    ORDER BY section_id, topic_id
                """, (student["id"], self.get_class_level(class_id)), fetch='all')
            else:
                results = self._exec("""
                    SELECT section_id, topic_id, percentage, passed
                    FROM test_results
                    WHERE user_id = %s
                    ORDER BY section_id, topic_id
                """, (student["id"],), fetch='all')

            if results:
                sections = {}
                for r in results:
                    if r["section_id"] not in sections:
                        sections[r["section_id"]] = []
                    sections[r["section_id"]].append(r["percentage"])

                section_averages = {}
                for sec_id, percentages in sections.items():
                    sec_info = self.get_section_info(self.get_class_level(class_id), sec_id)
                    total_in_section = sec_info["topics"] if sec_info else 5
                    section_averages[sec_id] = round(sum(percentages) / total_in_section)

                total_avg = round(sum(section_averages.values()) / len(section_averages)) if section_averages else 0
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
        row = self._exec("SELECT class_level FROM classes WHERE id = %s", (class_id,), fetch='one')
        if row and row["class_level"]:
            return int(row["class_level"])
        row2 = self._exec("SELECT name FROM classes WHERE id = %s", (class_id,), fetch='one')
        if row2:
            for level in [7, 8, 9]:
                if str(level) in row2["name"]:
                    return level
        return 7

    def get_class_average_stats(self, class_id: int, section_id: int = None):
        students = self.get_students_rating(class_id, section_id)
        if not students:
            return {"total_students": 0, "class_average": 0, "completed_percentage": 0,
                    "top_student": None, "section_stats": {}}

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
            section_stats[sec_id]["completed_percentage"] = (
                section_stats[sec_id]["completed"] / section_stats[sec_id]["count"]
            ) * 100

        return {
            "total_students": len(students),
            "class_average": total_avg,
            "completed_percentage": completed_percentage,
            "top_student": students[0] if students else None,
            "section_stats": section_stats
        }

    def get_teacher_videos(self, teacher_id: int):
        return self._exec("""
            SELECT * FROM teacher_videos 
            WHERE teacher_id = %s OR is_public = TRUE
            ORDER BY created_at DESC
        """, (teacher_id,), fetch='all')

    def add_teacher_video(self, teacher_id: int, title: str, url: str,
                          description: str = None, is_public: bool = False):
        cur = self._cur()
        try:
            cur.execute("""
                INSERT INTO teacher_videos (teacher_id, title, url, description, is_public)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (teacher_id, title, url, description, is_public))
            row = cur.fetchone()
            self.conn.commit()
            return row["id"]
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def get_student_detailed_progress(self, student_id: int, class_id: int):
        class_level = self.get_class_level(class_id)
        results = self._exec("""
            SELECT section_id, topic_id, score, total_questions, percentage, passed, completed_at
            FROM test_results
            WHERE user_id = %s AND class_level = %s
            ORDER BY section_id, topic_id
        """, (student_id, class_level), fetch='all')

        sections = {}
        for r in results:
            if r["section_id"] not in sections:
                sections[r["section_id"]] = {"topics": [], "total_percentage": 0, "completed_at": None}
            sections[r["section_id"]]["topics"].append({
                "topic_id": r["topic_id"],
                "score": r["score"],
                "total": r["total_questions"],
                "percentage": r["percentage"],
                "passed": r["passed"],
                "completed_at": r["completed_at"]
            })
            sections[r["section_id"]]["total_percentage"] += r["percentage"]
            if r["completed_at"] and (
                not sections[r["section_id"]]["completed_at"] or
                r["completed_at"] > sections[r["section_id"]]["completed_at"]
            ):
                sections[r["section_id"]]["completed_at"] = r["completed_at"]

        for sec_id in sections:
            if sections[sec_id]["topics"]:
                sec_info = self.get_section_info(class_level, sec_id)
                total_topics_in_section = sec_info["topics"] if sec_info else 5
                topic_count = len(sections[sec_id]["topics"])
                sections[sec_id]["avg_percentage"] = round(
                    sections[sec_id]["total_percentage"] / total_topics_in_section
                )
                sections[sec_id]["is_completed"] = (
                    topic_count >= total_topics_in_section and
                    sections[sec_id]["avg_percentage"] >= 70
                )

        return sections

    def get_section_rating(self, class_id: int, section_id: int) -> list:
        class_level = self.get_class_level(class_id)
        sec_info = self.get_section_info(class_level, section_id)
        total_topics = sec_info["topics"] if sec_info else 5

        TOPIC_ID_MAP = {
            7: {
                1: {1: 1, 2: 2, 3: 3, 4: 4},
                2: {5: 1, 6: 2, 7: 3},
                3: {8: 1, 9: 2, 10: 3, 11: 4, 12: 5, 13: 6, 14: 7},
                4: {15: 1, 16: 2, 17: 3, 18: 4},
                5: {19: 1, 20: 2, 21: 3, 22: 4},
            },
            8: {
                1: {23: 1, 24: 2, 25: 3, 26: 4, 27: 5},
                2: {28: 1, 29: 2},
                3: {30: 1, 31: 2, 32: 3, 33: 4, 34: 5},
                4: {35: 1, 36: 2, 37: 3, 38: 4, 39: 5, 40: 6, 41: 7},
                5: {42: 1, 43: 2, 44: 3, 45: 4, 46: 5},
            },
            9: {
                1: {47: 1, 48: 2, 49: 3, 50: 4},
                2: {51: 1, 52: 2, 53: 3},
                3: {54: 1, 55: 2, 56: 3, 57: 4, 58: 5},
                4: {59: 1, 60: 2, 61: 3, 62: 4, 63: 5, 64: 6, 65: 7, 66: 8},
            }
        }
        topic_map = TOPIC_ID_MAP.get(class_level, {}).get(section_id, {})

        students = self._exec("""
            SELECT u.id, u.name, u.username AS email
            FROM class_students cs
            JOIN users u ON cs.student_id = u.id
            WHERE cs.class_id = %s
            ORDER BY u.name
        """, (class_id,), fetch='all')

        result = []
        for student in students:
            rows = self._exec("""
                SELECT topic_id, percentage
                FROM test_results
                WHERE user_id = %s AND class_level = %s AND section_id = %s
                ORDER BY topic_id
            """, (student["id"], class_level, section_id), fetch='all')

            topics_map = {}
            total_pct = 0
            for r in rows:
                raw_id = r["topic_id"]
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

        result.sort(key=lambda x: x["avg"], reverse=True)
        return result

    def close(self):
        self.conn.close()