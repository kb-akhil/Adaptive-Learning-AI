# ============================================================
# agents/question_agent.py — Fast: 1 call per question
# ============================================================
import os, re, torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR  = os.path.join(BASE_DIR, "trained_models", "flan_t5_cn")

PROMPT_TEMPLATE = "Generate a multiple choice question about {topic} with options A B C D"

_model     = None
_tokenizer = None


def _load_model():
    global _model, _tokenizer
    if _model is None:
        print(f"[QuestionAgent] Loading model from {MODEL_DIR}")
        _tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)
        _model     = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model.to(device)
        _model.eval()
        print(f"[QuestionAgent] Model loaded on {device}")
    return _model, _tokenizer


def _parse_mcq(text):
    text = text.strip()
    text = re.sub(r'\s+([ABCD]\))', r'\n\1', text)
    text = re.sub(r'\s+(Answer:)', r'\nAnswer:', text)

    q_match = re.search(r"Question:\s*(.+?)(?=\nA\))", text, re.DOTALL)
    if not q_match:
        q_match = re.search(r"^(.+?)(?=\nA\))", text, re.DOTALL)
    if not q_match:
        return None
    question = q_match.group(1).strip()

    raw_options = []
    for letter in ["A", "B", "C", "D"]:
        pattern = rf"\n{letter}\)\s*(.+?)(?=\n[ABCD]\)|\nAnswer:|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            raw_options.append(match.group(1).strip())

    if len(raw_options) < 3:
        return None

    seen_vals, unique_vals = set(), []
    for val in raw_options:
        norm = val.strip().lower()
        if norm not in seen_vals:
            seen_vals.add(norm)
            unique_vals.append(val)

    while len(unique_vals) < 4:
        unique_vals.append("I'm not sure")

    if len(unique_vals) < 3:
        return None

    options = [
        {"key": ["A", "B", "C", "D"][i], "value": unique_vals[i]}
        for i in range(min(4, len(unique_vals)))
    ]

    return {"question": question, "options": options, "answer": "C"}


def _normalize(text: str) -> str:
    return re.sub(r'[^a-z0-9 ]', '', text.lower().strip())


def _generate_one(prompt, model, tokenizer):
    device = next(model.parameters()).device
    inputs = tokenizer(
        prompt, return_tensors="pt", max_length=80, truncation=True
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=180,
            num_beams=2,        # ← reduced from 4 to 2 for speed
            early_stopping=True,
            no_repeat_ngram_size=3,
        )

    raw = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return _parse_mcq(raw)


def generate_questions(topics: list, questions_per_topic: int = 2) -> list:
    model, tokenizer = _load_model()
    all_questions    = []
    global_seen      = set()

    for topic in topics:
        print(f"\n[QuestionAgent] Topic: {topic}")
        count = 0

        for slot in range(questions_per_topic):
            # Slot 0: plain topic, Slot 1: slightly varied
            if slot == 0:
                prompt = PROMPT_TEMPLATE.format(topic=topic)
            else:
                prompt = PROMPT_TEMPLATE.format(topic=f"{topic} mechanism")

            parsed = _generate_one(prompt, model, tokenizer)

            if parsed is None:
                print(f"[QuestionAgent] Parse failed slot {slot} for '{topic}'")
                continue

            norm = _normalize(parsed["question"])
            if norm in global_seen:
                print(f"[QuestionAgent] Duplicate skipped")
                continue

            global_seen.add(norm)
            parsed["topic"] = topic
            all_questions.append(parsed)
            count += 1
            print(f"[QuestionAgent] OK: {parsed['question'][:70]}")

        if count == 0:
            print(f"[QuestionAgent] WARNING: No questions for '{topic}'")

    for i, q in enumerate(all_questions):
        q["id"] = i + 1

    print(f"\n[QuestionAgent] Total: {len(all_questions)} questions")
    return all_questions


generate_questions_for_topics = generate_questions