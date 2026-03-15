# ============================================================
# agents/path_agent.py — Fixed priority grouping
# ============================================================
import re

NOISE_PATTERNS = [
    r'^unit\s*[-–]', r'^unit\s*[ivxlcdm\d]',
    r'unit\s*[-–]\s*[ivxlcdm\d]', r'^[lvt]\s+[t/p]',
    r'^l\s+t', r'^r\d{4,}', r'\d+(st|nd|rd|th)\s+edition',
    r'tanenbaum|forouzan|stallings|kurose|pearson|tmh',
    r'^general$', r'^\d+[\s\-]+\d+', r'^[-–&]+$', r'^\s*$',
    r'text\s*book', r'reference', r'bibliography',
]

def _is_noise(t: str) -> bool:
    s = t.lower().strip()
    return len(s) < 3 or any(re.search(p, s) for p in NOISE_PATTERNS)

def _norm(t: str) -> str:
    return re.sub(r'[^a-z0-9]', '', t.lower().strip())

def _match(a: str, b: str) -> bool:
    if _norm(a) == _norm(b): return True
    stop = {"of","and","the","in","a","an","to","for","with","on","layer"}
    wa = set(a.lower().split()) - stop
    wb = set(b.lower().split()) - stop
    return bool(wa and wb and wa & wb)

def _get_priority(t: str, weak: list, strong: list) -> int:
    """Check if topic t is in weak or strong list."""
    for w in weak:
        if _match(t, w): return 1
    for s in strong:
        if _match(t, s): return 3
    return 2


def generate_learning_path(
    weak_topics:   list,
    strong_topics: list,
    all_topics:    list,
    accuracy:      float,
    hierarchy:     list = None,
) -> dict:

    hierarchy     = [u for u in (hierarchy or []) if not _is_noise(u.get("title",""))]
    weak_topics   = [t for t in weak_topics   if not _is_noise(t)]
    strong_topics = [t for t in strong_topics if not _is_noise(t)]
    all_topics    = [t for t in all_topics    if not _is_noise(t)]

    # ── FULL SYLLABUS (3+ units) ──────────────────────────────
    if len(hierarchy) >= 3:
        modules = []
        for unit in hierarchy:
            title = unit.get("title","")
            subs  = [s for s in unit.get("subtopics",[]) if not _is_noise(s)]
            p     = _get_priority(title, weak_topics, strong_topics)
            modules.append({
                "title": title, "subtopics": subs,
                "priority": p,
                "priority_label": {1:"Needs Focus",2:"Review",3:"Strong"}[p],
                "is_weak": p==1, "is_strong": p==3,
            })
        modules.sort(key=lambda m: m["priority"])
        modules = _ensure_three(modules)
        for i,m in enumerate(modules): m["module_number"] = i+1
        return _wrap(modules, accuracy)

    # ── SINGLE UNIT ───────────────────────────────────────────
    # Get all subtopics from hierarchy
    pool = []
    if hierarchy:
        for unit in hierarchy:
            for s in unit.get("subtopics",[]):
                if not _is_noise(s) and s not in pool:
                    pool.append(s)
    if not pool:
        pool = [t for t in all_topics if not _is_noise(t)]

    if not pool:
        return _wrap([], accuracy)

    # Classify each pool topic by performance
    weak_p   = [t for t in pool if _get_priority(t, weak_topics, strong_topics) == 1]
    strong_p = [t for t in pool if _get_priority(t, weak_topics, strong_topics) == 3]
    medium_p = [t for t in pool if _get_priority(t, weak_topics, strong_topics) == 2]

    print(f"[PathAgent] Pool={len(pool)} Weak={weak_p} Strong={strong_p} Medium={medium_p}")

    # Build 3 modules — one per priority group
    # Each module: title = first topic, subtopics = rest
    raw = []
    if weak_p:
        raw.append((1, "Needs Focus", weak_p, True, False))
    if medium_p:
        raw.append((2, "Review", medium_p, False, False))
    if strong_p:
        raw.append((3, "Strong", strong_p, False, True))

    # If only 1 or 2 groups — split largest group to ensure 3 modules
    if len(raw) == 1:
        topics = raw[0][2]
        n = len(topics)
        t1 = max(1, n//3)
        t2 = max(2, 2*n//3)
        raw = [
            (1, "Needs Focus", topics[:t1],  True,  False),
            (2, "Review",      topics[t1:t2], False, False),
            (3, "Strong",      topics[t2:],   False, True),
        ]
    elif len(raw) == 2:
        # Split the larger group
        idx = 0 if len(raw[0][2]) >= len(raw[1][2]) else 1
        topics = raw[idx][2]
        mid = max(1, len(topics)//2)
        new_raw = list(raw)
        new_raw[idx] = (raw[idx][0], raw[idx][1], topics[:mid], raw[idx][3], raw[idx][4])
        new_raw.insert(idx+1, (2, "Review", topics[mid:], False, False))
        raw = new_raw

    # Collect all topics for cross-referencing
    all_pool_topics = [t for (_,_,tl,_,_) in raw for t in tl]

    # Build final modules
    modules = []
    for (p, label, topics, iw, istr) in raw:
        if not topics:
            continue
        title     = topics[0]
        subtopics = topics[1:]
        # If only 1 topic in group, add related topics from other groups as subtopics
        if not subtopics:
            subtopics = [t for t in all_pool_topics if t != title][:4]
        modules.append({
            "module_number":  0,
            "title":          title,
            "subtopics":      subtopics,
            "priority":       p,
            "priority_label": label,
            "is_weak":        iw,
            "is_strong":      istr,
            "status":         "not_started"
        })

    for i,m in enumerate(modules): m["module_number"] = i+1

    w = sum(1 for m in modules if m["priority"]==1)
    r = sum(1 for m in modules if m["priority"]==2)
    s = sum(1 for m in modules if m["priority"]==3)
    print(f"[PathAgent] Final: {len(modules)} modules W:{w} R:{r} S:{s} | Acc:{accuracy}%")
    return _wrap(modules, accuracy)


def _ensure_three(modules):
    if len(modules) < 3: return modules
    if len({m["priority"] for m in modules}) >= 3: return modules
    n = len(modules)
    for i,m in enumerate(modules):
        if i >= n - max(1, n//4):
            m.update({"priority":3,"priority_label":"Strong","is_weak":False,"is_strong":True})
        elif i >= max(1, n - max(2, n//3)):
            m.update({"priority":2,"priority_label":"Review","is_weak":False,"is_strong":False})
        else:
            m.update({"priority":1,"priority_label":"Needs Focus","is_weak":True,"is_strong":False})
    return modules


def _wrap(modules, accuracy):
    return {
        "total_modules":    len(modules),
        "overall_accuracy": accuracy,
        "recommendation":   _recommendation(accuracy),
        "modules":          modules
    }

def _recommendation(accuracy: float) -> str:
    if accuracy >= 80:
        return "Great performance! Focus on review modules to reinforce edge cases."
    elif accuracy >= 60:
        return "Good effort! Revisit the high-priority modules and practice with examples."
    else:
        return "Start from Module 1 and work through each topic carefully before moving forward."