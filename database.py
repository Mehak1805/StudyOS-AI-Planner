import sqlite3
import os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study_plans.db")

def conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    c = conn()
    c.execute("""
    CREATE TABLE IF NOT EXISTS topics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        topic TEXT,
        known INTEGER DEFAULT 0
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS saved_plans(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        plan_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS saved_plans(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        plan_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS knowledge(
        subject TEXT,
        keyword TEXT,
        difficulty TEXT,
        score INTEGER,
        exam_prob INTEGER DEFAULT 50
    )
    """)
    cols = [r[1] for r in c.execute("PRAGMA table_info(knowledge)").fetchall()]
    if "exam_prob" not in cols:
        c.execute("ALTER TABLE knowledge ADD COLUMN exam_prob INTEGER DEFAULT 50")
    tcols = [r[1] for r in c.execute("PRAGMA table_info(topics)").fetchall()]
    if "known" not in tcols:
        c.execute("ALTER TABLE topics ADD COLUMN known INTEGER DEFAULT 0")
    seed_knowledge(c)
    c.commit()
    c.close()

def reset_knowledge():
    c = conn()
    c.execute("DELETE FROM knowledge")
    seed_knowledge(c)
    c.commit()
    c.close()

def seed_knowledge(c):
    if c.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0] >= 300:
        return
    rows = [
        ("dbms","normalization","Hard",3,95),
        ("dbms","normal form","Hard",3,95),
        ("dbms","1nf","Hard",3,90),
        ("dbms","2nf","Hard",3,90),
        ("dbms","3nf","Hard",3,95),
        ("dbms","bcnf","Hard",3,92),
        ("dbms","4nf","Hard",3,75),
        ("dbms","5nf","Hard",3,60),
        ("dbms","functional dependency","Hard",3,95),
        ("dbms","fd","Hard",3,90),
        ("dbms","decomposition","Hard",3,85),
        ("dbms","lossless","Hard",3,80),
        ("dbms","dependency preservation","Hard",3,78),
        ("dbms","transaction","Hard",3,95),
        ("dbms","acid","Hard",3,92),
        ("dbms","atomicity","Medium",2,85),
        ("dbms","consistency","Medium",2,85),
        ("dbms","isolation","Hard",3,88),
        ("dbms","durability","Medium",2,80),
        ("dbms","concurrency","Hard",3,90),
        ("dbms","concurrency control","Hard",3,90),
        ("dbms","serializability","Hard",3,88),
        ("dbms","serializable","Hard",3,85),
        ("dbms","conflict","Hard",3,82),
        ("dbms","locking","Hard",3,85),
        ("dbms","two phase locking","Hard",3,85),
        ("dbms","2pl","Hard",3,82),
        ("dbms","deadlock","Hard",3,88),
        ("dbms","timestamp","Hard",3,80),
        ("dbms","recovery","Hard",3,85),
        ("dbms","log","Medium",2,80),
        ("dbms","checkpoint","Medium",2,75),
        ("dbms","sql","Medium",2,95),
        ("dbms","query","Medium",2,90),
        ("dbms","join","Medium",2,92),
        ("dbms","inner join","Medium",2,88),
        ("dbms","outer join","Medium",2,85),
        ("dbms","full join","Medium",2,80),
        ("dbms","natural join","Medium",2,82),
        ("dbms","left join","Medium",2,85),
        ("dbms","aggregate","Medium",2,85),
        ("dbms","group by","Medium",2,82),
        ("dbms","having","Medium",2,80),
        ("dbms","subquery","Hard",3,85),
        ("dbms","nested query","Hard",3,82),
        ("dbms","view","Medium",2,80),
        ("dbms","stored procedure","Hard",3,70),
        ("dbms","trigger","Medium",2,75),
        ("dbms","cursor","Medium",2,65),
        ("dbms","indexing","Hard",3,88),
        ("dbms","index","Hard",3,85),
        ("dbms","b tree","Hard",3,85),
        ("dbms","b+ tree","Hard",3,88),
        ("dbms","hashing","Hard",3,80),
        ("dbms","file organization","Hard",3,80),
        ("dbms","er diagram","Medium",2,92),
        ("dbms","er model","Medium",2,90),
        ("dbms","entity","Easy",1,85),
        ("dbms","attribute","Easy",1,82),
        ("dbms","relationship","Medium",2,88),
        ("dbms","er","Medium",2,88),
        ("dbms","relational model","Medium",2,88),
        ("dbms","relational algebra","Hard",3,85),
        ("dbms","tuple calculus","Hard",3,75),
        ("dbms","domain calculus","Hard",3,70),
        ("dbms","keys","Medium",2,90),
        ("dbms","primary key","Easy",1,90),
        ("dbms","foreign key","Medium",2,88),
        ("dbms","candidate key","Medium",2,85),
        ("dbms","super key","Medium",2,82),
        ("dbms","integrity","Medium",2,80),
        ("dbms","constraint","Medium",2,80),
        ("dbms","ddl","Easy",1,80),
        ("dbms","dml","Easy",1,80),
        ("dbms","dcl","Easy",1,70),
        ("dbms","schema","Easy",1,85),
        ("dbms","instance","Easy",1,80),
        ("dbms","data independence","Medium",2,82),
        ("dbms","abstraction","Easy",1,80),
        ("dbms","three tier","Medium",2,78),
        ("dbms","data model","Easy",1,82),
        ("dbms","nosql","Medium",2,70),
        ("dbms","distributed","Hard",3,72),
        ("dbms","data warehouse","Medium",2,65),
        ("dbms","olap","Medium",2,60),
        ("dbms","application","Easy",1,70),
        ("dbms","introduction","Easy",1,70),
        ("dbms","basics","Easy",1,65),
        ("dbms","design","Medium",2,80),
        ("dbms","database design","Medium",2,80),
        ("dbms","process","Medium",2,75),
        ("operating system","process","Medium",2,88),
        ("operating system","thread","Medium",2,82),
        ("operating system","scheduling","Hard",3,90),
        ("operating system","memory management","Hard",3,88),
        ("operating system","deadlock","Hard",3,90),
        ("operating system","synchronization","Hard",3,88),
        ("operating system","file system","Medium",2,80),
        ("operating system","virtual memory","Hard",3,85),
        ("operating system","paging","Medium",2,82),
        ("operating system","segmentation","Medium",2,78),
        ("operating system","semaphore","Medium",2,80),
        ("operating system","cpu scheduling","Hard",3,88),
        ("operating system","page replacement","Hard",3,85),
        ("operating system","disk scheduling","Hard",3,82),
        ("operating system","banker","Hard",3,80),
        ("computer networks","osi","Medium",2,90),
        ("computer networks","tcp","Medium",2,85),
        ("computer networks","ip","Medium",2,85),
        ("computer networks","routing","Hard",3,88),
        ("computer networks","dns","Easy",1,80),
        ("computer networks","http","Easy",1,78),
        ("computer networks","congestion","Hard",3,82),
        ("computer networks","subnetting","Hard",3,85),
        ("computer networks","sliding window","Hard",3,80),
        ("computer networks","error detection","Medium",2,80),
        ("computer networks","mac","Medium",2,78),
        ("dsa","array","Easy",1,85),
        ("dsa","linked list","Easy",1,82),
        ("dsa","stack","Easy",1,80),
        ("dsa","queue","Easy",1,78),
        ("dsa","tree","Medium",2,88),
        ("dsa","binary tree","Medium",2,85),
        ("dsa","bst","Medium",2,85),
        ("dsa","avl","Hard",3,80),
        ("dsa","graph","Hard",3,88),
        ("dsa","dynamic programming","Hard",3,90),
        ("dsa","dp","Hard",3,88),
        ("dsa","sorting","Medium",2,85),
        ("dsa","searching","Easy",1,80),
        ("dsa","recursion","Medium",2,82),
        ("dsa","backtracking","Hard",3,80),
        ("dsa","greedy","Medium",2,82),
        ("dsa","hashing","Medium",2,80),
        ("dsa","heap","Medium",2,78),
        ("dsa","complexity","Medium",2,85),
        ("dsa","dijkstra","Hard",3,80),
        ("dsa","bfs","Medium",2,82),
        ("dsa","dfs","Medium",2,82),
        ("maths","calculus","Hard",3,75),
        ("maths","matrix","Hard",3,72),
        ("maths","trigonometry","Hard",3,70),
        ("maths","integration","Hard",3,72),
        ("maths","derivative","Hard",3,70),
        ("maths","algebra","Medium",2,68),
        ("maths","statistics","Medium",2,65),
        ("maths","probability","Medium",2,68),
        ("physics","thermodynamics","Hard",3,72),
        ("physics","electrostatics","Hard",3,70),
        ("physics","optics","Hard",3,68),
        ("physics","magnetism","Hard",3,70),
        ("chemistry","organic chemistry","Hard",3,72),
        ("chemistry","electrochemistry","Hard",3,70),
        ("machine learning","neural network","Hard",3,75),
        ("machine learning","deep learning","Hard",3,72),
        ("machine learning","regression","Medium",2,70),
        ("machine learning","classification","Medium",2,68),
        ("software engineering","sdlc","Easy",1,65),
        ("software engineering","testing","Medium",2,68),
        ("software engineering","design pattern","Hard",3,70),
        ("general","introduction","Easy",1,55),
        ("general","overview","Easy",1,55),
        ("general","advanced","Hard",3,70),
        ("general","fundamentals","Easy",1,60),
        ("general","analysis","Hard",3,70),
        ("general","design","Medium",2,65),
        ("general","implementation","Medium",2,65),
        ("general","optimization","Hard",3,72),
        ("general","algorithm","Hard",3,75),
        ("general","theory","Medium",2,62),
        ("general","application","Medium",2,65),
        ("general","concept","Easy",1,58),
        ("general","method","Medium",2,62),
        ("general","technique","Medium",2,65),
        ("general","model","Medium",2,65),
        ("general","system","Medium",2,65),
        ("general","process","Medium",2,65),
        ("general","definition","Easy",1,55),
        ("general","basics","Easy",1,55),
        ("general","control","Hard",3,70),
        ("general","recovery","Hard",3,72),
        ("general","management","Medium",2,65),
        ("general","scheduling","Hard",3,75),
        ("general","protocol","Hard",3,70),
    ]
    c.executemany("INSERT INTO knowledge VALUES(?,?,?,?,?)", rows)

def add_topic(subject, topic):
    c = conn()
    c.execute("INSERT INTO topics (subject, topic, known) VALUES(?,?,0)", (subject, topic))
    c.commit()
    c.close()

def get_topics():
    c = conn()
    rows = c.execute("SELECT id, subject, topic, known FROM topics").fetchall()
    c.close()
    return rows

def mark_topic_known(topic_id: int, known: int):
    c = conn()
    c.execute("UPDATE topics SET known=? WHERE id=?", (known, topic_id))
    c.commit()
    c.close()

def mark_all_known(subject: str, known: int):
    c = conn()
    c.execute("UPDATE topics SET known=? WHERE LOWER(subject)=LOWER(?)", (known, subject))
    c.commit()
    c.close()

def clear_topics():
    c = conn()
    c.execute("DELETE FROM topics")
    c.commit()
    c.close()

def get_knowledge():
    c = conn()
    rows = c.execute("SELECT subject, keyword, difficulty, score, exam_prob FROM knowledge").fetchall()
    c.close()
    return rows

def save_to_knowledge(subject, topic, difficulty, score, exam_prob=55):
    """Cache AI-classified topics so we don't re-call the API next time."""
    c = conn()
    # Avoid duplicates
    exists = c.execute(
        "SELECT COUNT(*) FROM knowledge WHERE subject=? AND keyword=?",
        (subject.lower(), topic.lower())
    ).fetchone()[0]
    if not exists:
        c.execute("INSERT INTO knowledge VALUES(?,?,?,?,?)",
                  (subject.lower(), topic.lower(), difficulty, score, exam_prob))
        c.commit()
    c.close()

def save_study_plan(name, plan_json):
    c = conn()
    c.execute("INSERT INTO saved_plans (name, plan_json) VALUES(?,?)", (name, plan_json))
    c.commit()
    c.close()

def get_saved_plans():
    c = conn()
    rows = c.execute("SELECT id, name, plan_json, created_at FROM saved_plans ORDER BY created_at DESC").fetchall()
    c.close()
    return rows

def delete_saved_plan(plan_id):
    c = conn()
    c.execute("DELETE FROM saved_plans WHERE id=?", (plan_id,))
    c.commit()
    c.close()

def save_study_plan(name, plan_json):
    c = conn()
    c.execute("INSERT INTO saved_plans (name, plan_json) VALUES(?,?)", (name, plan_json))
    c.commit()
    c.close()

def get_saved_plans():
    c = conn()
    rows = c.execute("SELECT id, name, plan_json, created_at FROM saved_plans ORDER BY created_at DESC").fetchall()
    c.close()
    return rows

def delete_saved_plan(plan_id):
    c = conn()
    c.execute("DELETE FROM saved_plans WHERE id=?", (plan_id,))
    c.commit()
    c.close()