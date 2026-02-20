import pdfplumber
import re

# ── Identify the real "Topics of the course" table ────────────────────────────
# We require BOTH a topic column AND a sessions/hours column header.
# This is the strongest signal that differentiates it from CO/PO tables,
# evaluation tables, reference tables, etc.

TOPIC_COL_KEYWORDS   = ["topic", "topics", "unit", "module", "content", "syllabus content"]
SESSION_COL_KEYWORDS = ["session", "sessions", "hour", "hours", "lecture", "lectures",
                        "number of", "periods", "l-t-p", "ltp", "weeks"]

# Patterns that immediately disqualify a table (admin/metadata/evaluation)
DISQUALIFY_PATTERNS = [
    r"co\s*/\s*po",          # CO/PO mapping table
    r"po\d+",                # PO columns
    r"pso\d*",               # PSO columns
    r"weightage",            # evaluation/grading table
    r"evaluation\s*component",
    r"quiz|end\s*sem|lab\s*evaluation",
    r"rubric",
    r"textbook|reference\s*book",
    r"nptel|coursera|edx|mooc",
    r"email|@\w+\.\w+",
    r"cabin\s+\d+",
    r"attendance|plagiarism",
    # Course metadata / info tables (the ones causing junk topics)
    r"credit",               # Credits: 3 (2-0-2) style header rows
    r"l\s*-\s*t\s*-\s*p",   # L-T-P credit breakdown column
    r"batch\s*:",            # Batch: 2024 ...
    r"academic\s*year",      # Academic Year: 2025-26
    r"faculty\s*name",       # Faculty name rows
    r"course\s*code",        # Course code rows
    r"in.class\s*tool",      # In-class tool info rows
    r"hands.on\s*practical", # Practical session info rows
    r"group\s*problem",      # Group problem-solving info rows
]

# Patterns that disqualify a single cell from being a topic
ADMIN_CELL_PATTERNS = [
    r"(faculty|coordinator|professor|dr\.?|mr\.?|ms\.?)\s+\w+",
    r"@\w+\.\w+",                        # email
    r"cabin\s+\d+",                      # office location
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*\d{4}",  # dates
    r"^\s*co\s*\d+\s*$",                 # bare CO1 CO2 etc
    r"^\s*po\s*\d+\s*$",
    r"\d+\s*marks?\b",
    r"(prerequisite|attendance|plagiarism|rubric|weightage)",
    r"(textbook|reference|bibliography|nptel|coursera|edx)",
    r"(aim of|overview|objective|introduction to the course)",
    r"(project\s*file|repository|problem\s*statement)",
    r"(th\s*edition|pearson|mcgraw|springer)",
    # Metadata row labels that look like topics but aren't
    r"^\s*credits?\s*[:\(]",             # Credits: 3 or Credits (2-0-2)
    r"\(\d+-\d+-\d+\)",                  # (2-0-2) credit format
    r"^\s*batch\s*:",                    # Batch: 2024...
    r"academic\s*year",                  # Academic Year: 2025-26
    r"^\s*topics?\s*of\s*the\s*course",  # "Topics of the course" label cell
    r"in.class\s*tool",                  # In-class tool Information
    r"hands.on\s*practical",             # Hands-on practical sessions
    r"group\s*problem.solving",          # Group problem-solving sessions
    r"^\s*\d+\s*\(\d+-\d+-\d+\)",       # bare "3 (2-0-2)" credit value
    r"semester|academic\s*year|batch",   # General metadata terms
]

# Subject name label patterns
SUBJECT_LABEL_RE = [
    r"course\s*name\s*[:\-–]\s*(.+)",
    r"subject\s*(?:name|title)?\s*[:\-–]\s*(.+)",
    r"paper\s*(?:name|title)\s*[:\-–]\s*(.+)",
    r"name\s*of\s*(?:the\s*)?(?:course|subject)\s*[:\-–]\s*(.+)",
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def is_disqualified_table(table: list) -> bool:
    """Return True if this table is NOT a syllabus/topics table."""
    header_text = " ".join(
        str(c).lower() for row in table[:2] if row for c in row if c
    )
    return any(re.search(p, header_text) for p in DISQUALIFY_PATTERNS)


def is_topics_table(table: list) -> bool:
    """Return True only if header has BOTH a topic column AND a sessions column."""
    if not table or len(table) < 2:
        return False
    if is_disqualified_table(table):
        return False

    header_text = " ".join(
        str(c).lower() for row in table[:2] if row for c in row if c
    )
    has_topic   = any(kw in header_text for kw in TOPIC_COL_KEYWORDS)
    has_session = any(kw in header_text for kw in SESSION_COL_KEYWORDS)

    if not (has_topic and has_session):
        return False

    # Extra guard: if first column of data rows contains metadata labels
    # (Credits, Batch, Topics of the course...) it's an info table, not a syllabus
    METADATA_LABEL_RE = re.compile(
        r"credits?|batch\s*:|academic\s*year|topics?\s*of\s*the\s*course|"
        r"in.class\s*tool|hands.on\s*practical|group\s*problem|semester|"
        r"l\s*-\s*t\s*-\s*p|\(\d+-\d+-\d+\)",
        re.IGNORECASE
    )
    metadata_hits = 0
    for row in table[1:6]:  # check first 5 data rows
        if row and row[0]:
            if METADATA_LABEL_RE.search(str(row[0])):
                metadata_hits += 1
    if metadata_hits >= 2:
        return False  # looks like an info/metadata table

    return True


def get_topic_col(header_row: list) -> int:
    """Return index of the column whose header matches a topic keyword."""
    for ci, cell in enumerate(header_row or []):
        ct = str(cell).lower() if cell else ""
        if any(kw in ct for kw in TOPIC_COL_KEYWORDS):
            return ci
    return 0   # fallback: first column


def is_admin_cell(text: str) -> bool:
    t = text.lower().strip()
    return any(re.search(p, t) for p in ADMIN_CELL_PATTERNS)


def condense_topic(raw: str) -> str | None:
    """
    Given a long topic cell like:
      "Introduction and applications of DBMS, Purpose of data base, Data
       Independence, Database System architecture- 2-tier and 3-tier."

    Return a concise title like:
      "Introduction and applications of DBMS"

    Strategy:
    1. Collapse newlines → single space
    2. Strip leading bullets / numbering
    3. Take text before the first comma that comes after ≥4 words
       (many cells list sub-topics separated by commas)
    4. Validate length and content
    """
    if not raw:
        return None

    t = str(raw).strip()
    t = re.sub(r"\n+", " ", t)          # newlines → space
    t = re.sub(r"\s+", " ", t).strip()

    # Strip bullets / numbering
    t = re.sub(r"^[•→\-–\*\s]+", "", t)
    t = re.sub(r"^\(?[ivxIVX\d]+[.)]\)?\s*", "", t)
    t = re.sub(r"^(unit|module|chapter|topic)\s*\d*\s*[:\-–]?\s*", "", t, flags=re.IGNORECASE)
    t = t.strip().rstrip(".,;:")

    if not t or len(t) < 5:
        return None

    if is_admin_cell(t):
        return None

    # ── Condense: keep only the first meaningful phrase ───────────────────────
    # Split on commas, semicolons, " - ", or newlines and take parts
    # until we have 3–10 words
    parts = re.split(r",\s*|;\s*|\s+[–\-]\s+", t)
    condensed = parts[0].strip().rstrip(".")

    # If first part is too short (< 3 words), include the second part too
    if len(condensed.split()) < 3 and len(parts) > 1:
        condensed = (condensed + ", " + parts[1].strip()).rstrip(".")

    # If still too long (>12 words) take only first 10 words
    words = condensed.split()
    if len(words) > 12:
        condensed = " ".join(words[:10])

    # Must be ≥ 2 words, ≥ 5 chars, contain real letters
    if len(condensed.split()) < 2 or len(condensed) < 5:
        return None
    if not re.search(r"[a-zA-Z]{3,}", condensed):
        return None

    # Reject if it still looks like admin text after condensing
    if is_admin_cell(condensed):
        return None

    return condensed


# ── Subject extraction ─────────────────────────────────────────────────────────

def extract_subject_name(pdf) -> str:
    first = pdf.pages[0]

    # 1. Scan table cells on page 1 for "Course Name: ..."
    for table in first.extract_tables():
        for row in table:
            if not row:
                continue
            for i, cell in enumerate(row):
                if not cell:
                    continue
                cs = str(cell).strip()
                if re.search(r"course\s*name|subject\s*(?:name|title)?|paper\s*(?:name|title)",
                             cs, re.IGNORECASE):
                    # Value after colon in same cell
                    m = re.search(r"[:\-\u2013]\s*(.+)", cs, re.DOTALL)
                    if m:
                        cand = re.sub(r"\s*\n\s*", " ", m.group(1)).strip().rstrip(".,")
                        # Reject if it contains admin noise
                        if 3 < len(cand) < 80 and not re.search(r"@|cabin|\d{4}-\d{2}", cand, re.IGNORECASE):
                            return cand
                    # Value in adjacent cell
                    if i + 1 < len(row) and row[i + 1]:
                        cand = re.sub(r"\s*\n\s*", " ", str(row[i + 1])).strip()
                        if 3 < len(cand) < 80 and not re.search(r"@|\d{4}", cand):
                            return cand

    # 2. Plain text fallback
    text = (first.extract_text() or "").replace("\n", " ")
    for pat in SUBJECT_LABEL_RE:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            name = re.split(r"\s{3,}|\t", name)[0].strip().rstrip(".,")
            if 3 < len(name) < 80:
                return name

    return "Unknown Subject"


# ── Table topic extraction ─────────────────────────────────────────────────────

def extract_from_tables(pdf) -> list:
    topics = []

    for page in pdf.pages:
        for table in page.extract_tables():
            if not is_topics_table(table):
                continue

            topic_col = get_topic_col(table[0] or [])

            for row in table[1:]:   # skip header row
                if not row or topic_col >= len(row):
                    continue
                cell = row[topic_col]
                topic = condense_topic(cell)
                if topic:
                    topics.append(topic)

    return topics


# ── Bullet-point plain text fallback ──────────────────────────────────────────
# Used ONLY when the PDF has no recognisable table structure at all

BULLET_RE = re.compile(r"^(?:[•→*]|[-–]\s{1,3}(?=[A-Z])|\d+[.)]\s)")

def extract_from_text(pdf) -> list:
    topics = []
    for page in pdf.pages:
        text = page.extract_text() or ""
        for line in text.splitlines():
            line = line.strip()
            if not BULLET_RE.match(line):
                continue
            topic = condense_topic(line)
            if topic:
                topics.append(topic)
    return topics


# ── Entry point ────────────────────────────────────────────────────────────────

def extract_topics_from_pdf(file) -> dict:
    """
    Returns:
        { "subject": "Database Management System", "topics": [...] }
    """
    with pdfplumber.open(file) as pdf:
        subject      = extract_subject_name(pdf)
        table_topics = extract_from_tables(pdf)

        # Only fall back to bullet-point text if tables gave nothing
        if not table_topics:
            text_topics = extract_from_text(pdf)
        else:
            text_topics = []

        all_topics = table_topics + [t for t in text_topics if t not in table_topics]

    # Deduplicate case-insensitively, preserve order
    seen, unique = set(), []
    for t in all_topics:
        key = t.lower()
        if key not in seen:
            seen.add(key)
            unique.append(t)

    return {
        "subject": subject,
        "topics":  unique[:40],
    }