"""Проверка файлов с заданиями из папки examples.

Запуск: python3 check_examples.py
Скрипт простой, без сторонних библиотек. Он проверяет те правила,
которые описаны в README.md и в question.schema.json.
"""
import json
from pathlib import Path

TYPES = ["NUMERIC", "SINGLE_CHOICE", "MULTIPLE_CHOICE"]
FIELDS = ["topic", "exam_number", "text", "question_type", "options", "correct_answer", "points"]


def check_question(number, q):
    """Возвращает список ошибок одного задания."""
    errors = []
    for field in FIELDS:
        if field not in q:
            errors.append(f"нет поля {field}")
    if errors:
        return errors

    kind = q["question_type"]
    if kind not in TYPES:
        return [f"неизвестный тип {kind}"]
    if not isinstance(q["points"], int) or q["points"] < 1:
        errors.append("points должно быть целым числом от 1")
    if q["exam_number"] is not None and not isinstance(q["exam_number"], int):
        errors.append("exam_number должно быть числом или null")

    if kind == "NUMERIC":
        if q["options"] is not None:
            errors.append("у NUMERIC options должно быть null")
        if isinstance(q["correct_answer"], bool) or not isinstance(q["correct_answer"], (int, float)):
            errors.append("у NUMERIC correct_answer должно быть числом")
        return errors

    # дальше только задания с выбором
    options = q["options"]
    if not isinstance(options, list) or len(options) < 2:
        return errors + ["нужно минимум два варианта в options"]
    ids = [o["id"] for o in options]
    if len(ids) != len(set(ids)):
        errors.append("id вариантов повторяются")

    answer = q["correct_answer"]
    if kind == "SINGLE_CHOICE":
        if answer not in ids:
            errors.append("correct_answer должен быть id одного из вариантов")
    else:
        if not isinstance(answer, list) or len(answer) < 1:
            errors.append("у MULTIPLE_CHOICE correct_answer должен быть списком id")
        else:
            for item in answer:
                if item not in ids:
                    errors.append(f"в correct_answer есть неизвестный id {item}")
    return errors


def check_file(path):
    """Проверяет один файл, печатает ошибки и возвращает их число."""
    data = json.loads(path.read_text(encoding="utf-8"))
    problems = 0

    for key in ["subject", "variant_structure", "questions"]:
        if key not in data:
            print(f"{path.name}: нет поля {key}")
            return 1

    # для каждого номера из структуры варианта нужно задание с этим номером
    numbers_in_bank = [q["exam_number"] for q in data["questions"]]
    for item in data["variant_structure"]:
        if item["exam_number"] not in numbers_in_bank:
            print(f"{path.name}: в банке нет заданий с номером {item['exam_number']}")
            problems += 1

    for i, q in enumerate(data["questions"], start=1):
        for error in check_question(i, q):
            print(f"{path.name}, задание {i}: {error}")
            problems += 1
    return problems


def main():
    folder = Path(__file__).parent / "examples"
    total = 0
    for path in sorted(folder.glob("*.json")):
        total += check_file(path)
    if total == 0:
        print("Всё в порядке")
    else:
        print(f"Найдено ошибок: {total}")


main()
