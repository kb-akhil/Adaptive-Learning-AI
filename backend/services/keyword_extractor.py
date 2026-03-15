# ============================================================
# services/keyword_extractor.py — Generic syllabus extractor
# Handles: UNIT headings, flat comma lists, mixed formats
# ============================================================
import re, json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

BLOCKED = {
    "unit", "chapter", "module", "section", "part", "general",
    "introduction", "overview", "summary", "conclusion", "review",
    "basic", "advanced", "concept", "theory", "study", "notes",
    "syllabus", "course", "subject", "exam", "test", "question",
    "answer", "mark", "total", "hour", "period", "lecture", "lab",
    "practical", "tutorial", "assignment", "semester", "year",
    "degree", "department", "college", "edition", "pearson",
    "education", "publication", "press", "tmh", "mcgraw", "hill",
    "wiley", "prentice", "hall", "reference", "text", "book",
    "author", "publisher", "volume", "page", "appendix", "index",
    "the", "and", "for", "with", "from", "this", "that", "are",
    "was", "has", "have", "been", "will", "its", "also", "such",
    "type", "mode", "method", "process", "level", "form", "base",
    "case", "time", "rate", "size", "node", "line", "host", "site",
    "name", "byte", "bit", "value", "number", "point", "state",
    "set", "list", "item", "example", "objectives", "to", "of",
    "in", "a", "an", "is", "be", "use", "uses", "types",
}

SKIP_PATTERNS = [
    r'text\s*books?', r'reference\s*books?', r'references?',
    r'bibliography', r'pearson|forouzan|tanenbaum|stallings|kurose|mcgraw',
    r'^r\d{5,}', r'^l\s+t', r'^\d+\s+\d+\s+\d+',
    r'co\s*\d+\s*:', r'course\s+objective', r'course\s+outcome',
    r'learning\s+outcome', r'\d+(st|nd|rd|th)\s+edition',
    r'objectives?:', r'^\s*to\s+(introduce|demonstrate|know|understand)',
]

ROMAN = re.compile(r'^(i{1,4}|iv|vi{0,3}|ix|xi{0,3}|xiv|xv)$', re.IGNORECASE)

UNIT_HEADING = re.compile(
    r'^(unit|module|chapter)\s*[-–]?\s*([ivxlcdm]+|\d+)\s*[-–:\.]\s*(.*)',
    re.IGNORECASE
)

ACRONYM_FIX = [
    (r'\bCsma/Cd\b', 'CSMA/CD'), (r'\bCsma/Ca\b', 'CSMA/CA'),
    (r'\bCsma\b', 'CSMA'), (r'\bTcp\b', 'TCP'), (r'\bUdp\b', 'UDP'),
    (r'\bIp\b', 'IP'), (r'\bOsi\b', 'OSI'), (r'\bDns\b', 'DNS'),
    (r'\bHttp\b', 'HTTP'), (r'\bFtp\b', 'FTP'), (r'\bRsa\b', 'RSA'),
    (r'\bWww\b', 'WWW'), (r'\bAloha\b', 'ALOHA'), (r'\bMac\b', 'MAC'),
    (r'\bLan\b', 'LAN'), (r'\bWan\b', 'WAN'), (r'\bVpn\b', 'VPN'),
    (r'\bSsl\b', 'SSL'), (r'\bTls\b', 'TLS'), (r'\bArp\b', 'ARP'),
    (r'\bIcmp\b', 'ICMP'), (r'\bDhcp\b', 'DHCP'), (r'\bOspf\b', 'OSPF'),
    (r'\bBgp\b', 'BGP'), (r'\bRip\b', 'RIP'), (r'\bQos\b', 'QoS'),
]


def _fix_acronyms(text: str) -> str:
    for pattern, replacement in ACRONYM_FIX:
        text = re.sub(pattern, replacement, text)
    return text


def extract_keywords(text: str, top_n: int = 15) -> list:
    hierarchy = extract_hierarchy(text, top_n)
    topics = []
    seen   = set()
    for unit in hierarchy:
        title = unit["title"]
        if title.lower() not in seen:
            seen.add(title.lower())
            topics.append(title)
        for child in unit["subtopics"]:
            if child.lower() not in seen and len(topics) < top_n:
                seen.add(child.lower())
                topics.append(child)
    return topics[:top_n]


def extract_hierarchy(text: str, top_n: int = 15) -> list:
    if not text or len(text.strip()) < 30:
        return []

    cleaned = _clean_text(text)

    # Check if UNIT headings exist
    has_units = bool(UNIT_HEADING.search(cleaned))

    if has_units:
        units = _parse_units(cleaned)
    else:
        # No unit structure — treat whole text as flat topic list
        units = _parse_flat(cleaned)

    result = []
    for unit in units:
        title = unit["title"]
        if _is_noise(title):
            continue
        clean_subs = [
            _fix_acronyms(s) for s in unit["subtopics"]
            if not _is_noise(s) and s.lower() != title.lower()
        ]
        if title:
            result.append({
                "title":     _fix_acronyms(title),
                "subtopics": clean_subs[:10]
            })

    return result[:top_n]


def _parse_flat(text: str) -> list:
    """
    For syllabi without UNIT headings — just a flat list of topics.
    Splits the entire text by commas/semicolons to get individual topics.
    Returns ONE module with all topics as subtopics, OR multiple small modules
    if the text has clear section breaks (lines ending with colon).
    """
    lines   = text.strip().split('\n')
    modules = []
    current_title   = None
    current_subs    = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Line ending with colon = section header
        if re.match(r'^[A-Z][^,;]{3,50}:\s*$', line) or \
           re.match(r'^[A-Z][^,;]{3,50}:\s*$', line.rstrip('.')):
            if current_title and current_subs:
                modules.append({"title": current_title, "subtopics": current_subs})
            current_title = _clean_topic(line.rstrip(':').strip())
            current_subs  = []
        else:
            # Split line by comma/semicolon
            parts = re.split(r'[,;]', line)
            for part in parts:
                part = part.strip()
                part = re.sub(r'^The\s+', '', part)
                cleaned = _clean_topic(part)
                if cleaned and not _is_noise(cleaned) and len(cleaned.split()) <= 6:
                    if current_title:
                        current_subs.append(cleaned)
                    else:
                        # No header yet — collect all as flat list
                        if not modules:
                            modules.append({"title": "Topics", "subtopics": []})
                        modules[-1]["subtopics"].append(cleaned)

    if current_title and current_subs:
        modules.append({"title": current_title, "subtopics": current_subs})

    # If only one "Topics" module, use first subtopic as title
    if len(modules) == 1 and modules[0]["title"] == "Topics":
        subs = modules[0]["subtopics"]
        if subs:
            title = subs[0]
            modules[0]["title"]     = title
            modules[0]["subtopics"] = subs[1:]

    return modules


def _parse_units(text: str) -> list:
    lines   = text.split('\n')
    units   = []
    current_title   = None
    current_content = []
    pending_title   = False

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue

        m = UNIT_HEADING.match(line)
        if m:
            if current_title:
                subtopics = _extract_subtopics_from_content(current_title, current_content)
                units.append({"title": current_title, "subtopics": subtopics})

            inline_title = m.group(3).strip()
            if inline_title:
                first_part    = re.split(r'[,;]', inline_title)[0].strip()
                current_title = _clean_topic(first_part) or f"Unit {m.group(2)}"
                current_content = [inline_title]
                pending_title = False
            else:
                pending_title   = True
                current_title   = None
                current_content = []
        elif pending_title and line:
            first_part    = re.split(r'[,;:]', line)[0].strip()
            current_title = _clean_topic(first_part) or line[:40]
            current_content = [line]
            pending_title = False
        else:
            if current_title:
                current_content.append(line)

    if current_title:
        subtopics = _extract_subtopics_from_content(current_title, current_content)
        units.append({"title": current_title, "subtopics": subtopics})

    return units


def _extract_subtopics_from_content(title: str, content_lines: list) -> list:
    subtopics = []
    seen      = set()
    title_low = title.lower()

    full_content = ' '.join(content_lines)
    parts = re.split(r'[,;]', full_content)

    for part in parts:
        part = part.strip()
        part = re.sub(r'^[•\-\*►→✓\d\.\)]\s*', '', part).strip()
        part = re.sub(r'^The\s+', '', part).strip()
        cleaned = _clean_topic(part)
        if not cleaned:
            continue
        cleaned = _fix_acronyms(cleaned)
        if cleaned.lower() in seen:
            continue
        if cleaned.lower() == title_low:
            continue
        if _is_noise(cleaned):
            continue
        if len(cleaned.split()) == 1 and len(cleaned) < 5:
            continue
        if len(cleaned.split()) > 8:
            continue
        seen.add(cleaned.lower())
        subtopics.append(cleaned)

    return subtopics


def _clean_text(text: str) -> str:
    lines        = text.split('\n')
    clean_lines  = []
    skip_section = False

    for line in lines:
        line_lower = line.strip().lower()
        if any(re.search(p, line_lower) for p in SKIP_PATTERNS[:6]):
            skip_section = True
        if UNIT_HEADING.match(line.strip()):
            skip_section = False
        if not skip_section:
            if not any(re.search(p, line_lower) for p in SKIP_PATTERNS):
                clean_lines.append(line)

    return '\n'.join(clean_lines)


def _clean_topic(raw: str) -> str:
    if not raw:
        return ""
    raw = re.sub(r'^[ivxlcdmIVXLCDM]+\s*[-:.]\s*', '', raw).strip()
    raw = re.sub(r'^\(?\d+[.)]\s*', '', raw).strip()
    raw = re.sub(r'\(.*?\)', '', raw).strip()
    raw = re.sub(r'\s+\d+$', '', raw).strip()
    raw = re.sub(r'[^\w\s\-/&:.,()]', '', raw).strip()
    raw = re.sub(r'\s+', ' ', raw).strip()
    raw = raw.title().strip()
    if len(raw) < 4:
        return ""
    # Trim overly long topics (more than 7 words) at colon or comma only
    if len(raw.split()) > 7:
        for sep in [":", ","]:
            if sep in raw:
                part = raw.split(sep)[0].strip()
                if len(part) > 4:
                    raw = part
                    break
    return raw


def _is_noise(topic: str) -> bool:
    t = topic.lower().strip()
    if len(t) < 3:
        return True
    if ROMAN.match(t):
        return True
    if re.match(r'^[\d\s\-:\.\/]+$', t):
        return True
    if re.match(r'^[A-Z]\d{4,}', topic):
        return True
    words = t.split()
    if all(w in BLOCKED or ROMAN.match(w) or w.isdigit() for w in words):
        return True
    if any(re.search(p, t) for p in SKIP_PATTERNS):
        return True
    return False


def keywords_to_json(kws: list) -> str:
    return json.dumps(kws)

def json_to_keywords(kws_json: str) -> list:
    try:
        return json.loads(kws_json)
    except Exception:
        return []

def hierarchy_to_json(hierarchy: list) -> str:
    return json.dumps(hierarchy)

def json_to_hierarchy(h_json: str) -> list:
    try:
        return json.loads(h_json)
    except Exception:
        return []