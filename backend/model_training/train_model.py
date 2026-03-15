# ============================================================
# model_training/train_model.py — NaN fix
# ============================================================
import os, sys, torch, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformers import (
    T5ForConditionalGeneration, T5Tokenizer,
    Seq2SeqTrainer, Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq,
)
from dataset_loader import load_cn_dataset

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_MODEL  = "google/flan-t5-base"
OUTPUT_DIR  = os.path.join(BASE_DIR, "trained_models", "flan_t5_cn")
LOGGING_DIR = os.path.join(BASE_DIR, "trained_models", "logs")

EPOCHS        = 10
BATCH_SIZE    = 4
GRAD_ACCUM    = 2           # effective batch = 8
LEARNING_RATE = 3e-4
MAX_INPUT     = 80
MAX_TARGET    = 180
WARMUP        = 50


def tokenize(batch, tokenizer):
    model_inputs = tokenizer(
        batch["input"],
        max_length=MAX_INPUT,
        truncation=True,
        padding="max_length",   # ← pad to fixed length (fixes NaN from empty labels)
    )
    labels = tokenizer(
        batch["output"],
        max_length=MAX_TARGET,
        truncation=True,
        padding="max_length",   # ← same fix
    )
    # Replace padding token id with -100 so loss ignores padding
    label_ids = labels["input_ids"]
    label_ids = [
        [(l if l != tokenizer.pad_token_id else -100) for l in lbl]
        for lbl in label_ids
    ]
    model_inputs["labels"] = label_ids
    return model_inputs


def main():
    print("=" * 60)
    print("AgenticLearn — FLAN-T5 Retrain (NaN fix)")
    print("=" * 60)

    # Delete old model
    if os.path.exists(OUTPUT_DIR):
        print(f"\n[Train] Removing old model...")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\n[Train] Loading base model: {BASE_MODEL}")
    tokenizer = T5Tokenizer.from_pretrained(BASE_MODEL)
    model     = T5ForConditionalGeneration.from_pretrained(BASE_MODEL)
    # NO gradient checkpointing — it conflicts with use_cache and causes issues
    torch.cuda.empty_cache()

    print("\n[Train] Loading dataset...")
    dataset = load_cn_dataset()
    print(f"[Train] {len(dataset)} examples loaded")

    print("\n[Train] Tokenizing...")
    tokenized = dataset.map(
        lambda b: tokenize(b, tokenizer),
        batched=True,
        remove_columns=dataset.column_names,
    )

    split      = tokenized.train_test_split(test_size=0.1, seed=42)
    train_data = split["train"]
    eval_data  = split["test"]
    print(f"[Train] Train: {len(train_data)} | Eval: {len(eval_data)}")

    args = Seq2SeqTrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LEARNING_RATE,
        warmup_steps=WARMUP,
        weight_decay=0.01,
        optim="adafactor",
        fp16=False,             # ← DISABLED — was causing NaN loss
        predict_with_generate=True,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        logging_dir=LOGGING_DIR,
        logging_steps=10,
        save_total_limit=1,
        report_to="none",
        generation_max_length=MAX_TARGET,
    )

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)
    trainer  = Seq2SeqTrainer(
        model=model, args=args,
        train_dataset=train_data,
        eval_dataset=eval_data,
        tokenizer=tokenizer,
        data_collator=collator,
    )

    print("\n[Train] Training started...")
    print("[Train] You should see loss DECREASING from ~3.0 down to <0.5")
    print("[Train] If loss stays 0.0 or NaN — stop and report back\n")
    trainer.train()

    print(f"\n[Train] Saving model to: {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("[Train] Saved!")

    # Quick test
    print("\n[Train] Testing model output...")
    model.eval()
    test_prompts = [
        "Generate a multiple choice question about Ethernet with options A B C D",
        "Generate a multiple choice question about TCP with options A B C D",
        "Generate a multiple choice question about DNS with options A B C D",
    ]
    success = 0
    for prompt in test_prompts:
        inp = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(
                **inp,
                max_new_tokens=180,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )
        result = tokenizer.decode(out[0], skip_special_tokens=True)
        has_options = all(f"{x})" in result for x in ["A", "B", "C", "D"])
        has_answer  = "Answer:" in result
        if has_options and has_answer:
            success += 1
        print(f"\nPROMPT: {prompt}")
        print(f"OUTPUT: {result}")
        print(f"STATUS: {'PASS' if (has_options and has_answer) else 'FAIL'}")

    print(f"\n{'='*60}")
    print(f"[Train] {success}/{len(test_prompts)} prompts generated full MCQ")
    if success >= 2:
        print("[Train] SUCCESS!")
    else:
        print("[Train] Still failing — share the loss values from training above")
    print("="*60)


if __name__ == "__main__":
    main()