#!/usr/bin/env python3
"""
Воспроизведение подсчетов Андреева из Главы 1 на корпусе new-corpus.
Сравнение результатов с данными из монографии.
Результаты сохраняются в файл result_chapter1_newcorpus.txt
"""

import os
import re
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import math
from pymystem3 import Mystem

# Пути
NEW_CORPUS_DIR = Path("/new-corpus")
RESULTS_FILE = Path("/andreev_chapter1_newcorpus_results.json")
OUTPUT_FILE = Path("/result_chapter1_newcorpus.txt")

# Данные Андреева из монографии (для сравнения)
ANDREEV_DATA = {
    "early_period": {
        "poems": ["ГП-1", "ГП-2", "ГП-3", "ГП-4", "ГП-5", "ГП-6", "ГП-7", "ГП-8", "ГП-9"],
        "total_metaphors": 626,
        "target_frequencies": {
            "Время": 0.1789, "Свет": 0.0815, "Информация": 0.0224,
            "Звук": 0.0208, "Экзистенция": 0.0224, "Вода": 0.0559,
            "Психическая сфера": 0.1214, "Существо": 0.0431,
            "Растение": 0.1262, "Пространство": 0.1581,
            "Драгоценность": 0.0176, "Социальный феномен": 0.0288,
            "Вещество": 0.0128, "Ткань": 0.0128, "Транспорт": 0.0240,
            "Орган": 0.0591, "Предмет": 0.0144
        },
        "h_point": 10,
        "concentration_index": 0.75,
        "cv": 0.16
    },
    "late_period": {
        "poems": ["СТ-1", "СТ-2", "СТ-3"],
        "total_metaphors": 362,
        "target_frequencies": {
            "Вода": 0.0414, "Существо": 0.0635, "Время": 0.2873,
            "Социальный феномен": 0.0635, "Пространство": 0.0884,
            "Психическая сфера": 0.0829, "Предмет": 0.0470,
            "Орган": 0.0635, "Информация": 0.0552, "Свет": 0.0718,
            "Вещество": 0.0166, "Звук": 0.0304, "Экзистенция": 0.0249,
            "Растение": 0.0525, "Транспорт": 0.0055, "Драгоценность": 0.0055
        },
        "h_point": 6.5,
        "concentration_index": 0.84,
        "cv": 0.38
    }
}

# Словарь концептов (для проверки наличия в тексте)
CONCEPT_KEYWORDS = {
    "Растение": ["растение", "дерев", "ветк", "лист", "дуб", "сосн", "ствол", "трава", "цветок", "лес", "сад", "рощ", "парк", "корн", "листв"],
    "Пространство": ["пространств", "небо", "облак", "туман", "земл", "территор", "поле", "гор", "равнин", "пустын", "дом", "арк", "здан", "крыш", "окн", "палат", "храм", "лестниц"],
    "Свет": ["звезд", "лампа", "лун", "луч", "свет", "сиян", "солнц", "свеч", "темнот", "зар"],
    "Существо": ["человек", "брат", "воин", "мать", "читатель", "певец", "птиц", "рыб", "жук", "ангел", "ласточк", "бабочк", "существ"],
    "Психическая сфера": ["гнев", "любов", "надежд", "ненавист", "печал", "радост", "сон", "страх", "чувств", "иде", "мысл", "памят", "размышлен", "душ"],
    "Транспорт": ["корабл", "лодк", "поезд", "паровоз", "телег", "автобус", "машин"],
    "Орган": ["сердц", "глаз", "рук", "плеч", "лиц", "волос", "голов", "ног"],
    "Время": ["миг", "мгновен", "дн", "месяц", "год", "век", "времен", "час", "ноч", "утр"],
    "Предмет": ["предмет", "вещ", "стол", "стул", "книг"],
    "Вода": ["вод", "рек", "ручь", "море", "волн", "озер", "пруд"],
    "Звук": ["звук", "голос", "песн", "звон", "музык"],
    "Информация": ["слов", "стих", "книг", "речь", "язык", "письм"],
    "Социальный феномен": ["власт", "войн", "мир", "равенств", "свобод", "цар", "княз"],
    "Экзистенция": ["жизн", "рожден", "смерт", "судьб", "быти"],
    "Драгоценность": ["золот", "янтар", "жемчуг", "алмаз", "серебр"],
    "Ткань": ["ткань", "бархат", "шелк", "вуаль", "занавес", "шарф", "плать", "парч"],
    "Вещество": ["камень", "желез", "стекл", "песок", "глин"],
    "Огонь": ["огонь", "плам", "костер", "пожар", "гор"],
    "Контейнер": ["комнат", "шкаф", "ящик", "клетк", "ковчег"],
    "Стихия": ["ветер", "гроз", "мороз", "снег", "шторм", "ураган", "буря"],
    "Орудие": ["нож", "меч", "копье", "топор", "пила", "кинжал"]
}

TARGET_CONCEPTS = [
    "Растение", "Пространство", "Свет", "Существо", "Психическая сфера",
    "Транспорт", "Орган", "Время", "Предмет", "Вода", "Звук", "Информация",
    "Социальный феномен", "Экзистенция", "Драгоценность", "Ткань", "Вещество"
]


class ConceptAnalyzer:
    def __init__(self):
        self.mystem = Mystem()
        self.concept_keywords = CONCEPT_KEYWORDS
    
    def lemmatize_text(self, text):
        # Удаляем строки с комментариями (начинаются с #)
        lines = text.split('\n')
        clean_lines = [line for line in lines if not line.startswith('#')]
        clean_text = ' '.join(clean_lines)
        lemmas = self.mystem.lemmatize(clean_text)
        lemmas = [l for l in lemmas if l.strip() and not l.isspace()]
        return lemmas
    
    def detect_concepts(self, lemmas, concept_list):
        concept_counts = defaultdict(int)
        for lemma in lemmas:
            lemma_lower = lemma.lower()
            for concept, keywords in self.concept_keywords.items():
                if concept not in concept_list:
                    continue
                for keyword in keywords:
                    if keyword in lemma_lower:
                        concept_counts[concept] += 1
                        break
        return concept_counts
    
    def analyze_text(self, text, concept_list):
        lemmas = self.lemmatize_text(text)
        concept_counts = self.detect_concepts(lemmas, concept_list)
        total = sum(concept_counts.values())
        return concept_counts, total, lemmas


def read_poems_from_new_corpus():
    """
    Чтение ВСЕХ текстов из папки new-corpus.
    Использует rglob() для рекурсивного обхода.
    Ожидается структура:
        new-corpus/early/ - ранний период
        new-corpus/late/ - зрелый период
    """
    poems = {"early": {}, "late": {}}
    
    # Рекурсивный обход папки early
    early_dir = NEW_CORPUS_DIR / "early"
    if early_dir.exists():
        for file in early_dir.rglob("*.txt"):
            # Пропускаем файлы в подпапках, которые могут быть служебными
            if file.parent.name.startswith('.'):
                continue
            # Используем полное имя файла как код
            code = file.stem
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read()
                poems["early"][code] = text
            except Exception as e:
                print(f"Ошибка чтения {file}: {e}")
    
    # Рекурсивный обход папки late
    late_dir = NEW_CORPUS_DIR / "late"
    if late_dir.exists():
        for file in late_dir.rglob("*.txt"):
            if file.parent.name.startswith('.'):
                continue
            code = file.stem
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read()
                poems["late"][code] = text
            except Exception as e:
                print(f"Ошибка чтения {file}: {e}")
    
    return poems


def calculate_frequencies(concept_counts, total):
    if total == 0:
        return {}
    return {concept: count / total for concept, count in concept_counts.items()}


def find_h_point(frequencies):
    sorted_items = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    for i, (concept, freq) in enumerate(sorted_items, 1):
        if abs(i - freq) < 0.1:
            return i
    for i in range(len(sorted_items) - 1):
        r1, f1 = i + 1, sorted_items[i][1]
        r2, f2 = i + 2, sorted_items[i + 1][1]
        if r1 > f1 and r2 < f2:
            h = (f1 * r2 - f2 * r1) / (r2 - r1 + f2 - f1)
            return h
    return None


def calculate_concentration_index(frequencies, h_point):
    if h_point is None or h_point < 1:
        return 0
    sorted_items = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    f1 = sorted_items[0][1] if sorted_items else 1
    total = 0
    for i, (concept, freq) in enumerate(sorted_items):
        r = i + 1
        if r < h_point:
            total += (h_point - r) * freq
    if h_point <= 1 or f1 == 0:
        return 0
    C = 2 * total / (h_point * (h_point - 1) * f1)
    return C


def calculate_cv(frequencies_by_text):
    concepts = list(frequencies_by_text[0].keys()) if frequencies_by_text else []
    if not concepts:
        return 0
    cv_values = []
    for concept in concepts:
        values = [freqs.get(concept, 0) for freqs in frequencies_by_text]
        mean = sum(values) / len(values) if values else 0
        if mean == 0:
            continue
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance)
        cv = std / mean
        cv_values.append(cv)
    return sum(cv_values) / len(cv_values) if cv_values else 0


def save_results_json(results):
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def compare_results(our_results, andreev_results):
    comparison = {"early": {}, "late": {}, "summary": {}}
    
    for period in ["early", "late"]:
        period_name = "early_period" if period == "early" else "late_period"
        our = our_results.get(period, {})
        andreev = andreev_results.get(period_name, {})
        
        our_h = our.get("h_point")
        andreev_h = andreev.get("h_point")
        h_diff = abs(our_h - andreev_h) if our_h and andreev_h else None
        
        our_c = our.get("concentration_index")
        andreev_c = andreev.get("concentration_index")
        c_diff = abs(our_c - andreev_c) if our_c and andreev_c else None
        
        our_cv = our.get("cv")
        andreev_cv = andreev.get("cv")
        cv_diff = abs(our_cv - andreev_cv) if our_cv and andreev_cv else None
        
        our_freq = our.get("target_frequencies", {})
        andreev_freq = andreev.get("target_frequencies", {})
        
        freq_comparison = {}
        for concept in set(our_freq.keys()) | set(andreev_freq.keys()):
            our_val = our_freq.get(concept, 0)
            andreev_val = andreev_freq.get(concept, 0)
            diff = abs(our_val - andreev_val)
            freq_comparison[concept] = {
                "our": our_val,
                "andreev": andreev_val,
                "diff": diff
            }
        
        comparison[period] = {
            "h_point": {"our": our_h, "andreev": andreev_h, "diff": h_diff},
            "concentration_index": {"our": our_c, "andreev": andreev_c, "diff": c_diff},
            "cv": {"our": our_cv, "andreev": andreev_cv, "diff": cv_diff},
            "frequencies": freq_comparison,
            "total_metaphors": {
                "our": our.get("total_metaphors", 0),
                "andreev": andreev.get("total_metaphors", 0),
                "diff": abs(our.get("total_metaphors", 0) - andreev.get("total_metaphors", 0))
            }
        }
    
    all_diffs = []
    for period in ["early", "late"]:
        data = comparison[period]
        if data["h_point"]["diff"] is not None:
            all_diffs.append(data["h_point"]["diff"])
        if data["concentration_index"]["diff"] is not None:
            all_diffs.append(data["concentration_index"]["diff"])
        if data["cv"]["diff"] is not None:
            all_diffs.append(data["cv"]["diff"])
        for concept_data in data["frequencies"].values():
            all_diffs.append(concept_data["diff"])
        all_diffs.append(data["total_metaphors"]["diff"] / 100)
    
    if all_diffs:
        avg_diff = sum(all_diffs) / len(all_diffs)
        max_diff = max(all_diffs)
        if avg_diff < 0.02:
            accuracy = "Отличная"
        elif avg_diff < 0.05:
            accuracy = "Хорошая"
        elif avg_diff < 0.10:
            accuracy = "Удовлетворительная"
        else:
            accuracy = "Требуется уточнение"
    else:
        avg_diff = None
        max_diff = None
        accuracy = "Нет данных для сравнения"
    
    comparison["summary"] = {
        "avg_diff": avg_diff,
        "max_diff": max_diff,
        "accuracy": accuracy,
        "total_poems_early": len(our_results.get("early", {}).get("poems", [])),
        "total_poems_late": len(our_results.get("late", {}).get("poems", []))
    }
    
    return comparison


def write_output(comparison, results, output_file):
    """Записывает результаты в файл."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ВОСПРОИЗВЕДЕНИЕ ПОДСЧЕТОВ АНДРЕЕВА (ГЛАВА 1)\n")
        f.write("НА КОРПУСЕ new-corpus\n")
        f.write("РЕЗУЛЬТАТЫ ОЦЕНКИ ТОЧНОСТИ\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Дата анализа: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Корпус: {NEW_CORPUS_DIR}\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("СТАТИСТИКА ПО КОРПУСУ\n")
        f.write("-" * 80 + "\n")
        
        for period in ["early", "late"]:
            period_label = "Ранний период (до 1929)" if period == "early" else "Зрелый период (1929-1951)"
            data = results.get(period, {})
            f.write(f"\n  {period_label}:\n")
            f.write(f"    Стихотворений: {len(data.get('poems', []))}\n")
            f.write(f"    Всего метафор: {data.get('total_metaphors', 0)}\n")
            f.write(f"    Концептов: {len(data.get('target_frequencies', {}))}\n")
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("СРАВНЕНИЕ С ДАННЫМИ АНДРЕЕВА\n")
        f.write("-" * 80 + "\n")
        
        for period in ["early", "late"]:
            period_label = "РАННИЙ ПЕРИОД (до 1929)" if period == "early" else "ЗРЕЛЫЙ ПЕРИОД (1929-1951)"
            data = comparison[period]
            
            f.write(f"\n{'─' * 80}\n")
            f.write(f"📊 {period_label}\n")
            f.write(f"{'─' * 80}\n")
            
            tm = data["total_metaphors"]
            f.write(f"\n  Общее количество метафор:\n")
            f.write(f"    Наши данные: {tm['our']}\n")
            f.write(f"    Данные Андреева: {tm['andreev']}\n")
            f.write(f"    Разница: {tm['diff']:.0f}\n")
            
            h = data["h_point"]
            f.write(f"\n  Точка Хирша (h-point):\n")
            f.write(f"    Наши данные: {h['our']:.2f}\n" if h['our'] else "    Наши данные: Н/Д\n")
            f.write(f"    Данные Андреева: {h['andreev']:.2f}\n" if h['andreev'] else "    Данные Андреева: Н/Д\n")
            if h['diff'] is not None:
                f.write(f"    Разница: {h['diff']:.4f}\n")
            
            c = data["concentration_index"]
            f.write(f"\n  Индекс концентрации ядра:\n")
            f.write(f"    Наши данные: {c['our']:.4f}\n" if c['our'] else "    Наши данные: Н/Д\n")
            f.write(f"    Данные Андреева: {c['andreev']:.4f}\n" if c['andreev'] else "    Данные Андреева: Н/Д\n")
            if c['diff'] is not None:
                f.write(f"    Разница: {c['diff']:.4f}\n")
            
            cv = data["cv"]
            f.write(f"\n  Коэффициент вариации (CV):\n")
            f.write(f"    Наши данные: {cv['our']:.4f}\n" if cv['our'] else "    Наши данные: Н/Д\n")
            f.write(f"    Данные Андреева: {cv['andreev']:.4f}\n" if cv['andreev'] else "    Данные Андреева: Н/Д\n")
            if cv['diff'] is not None:
                f.write(f"    Разница: {cv['diff']:.4f}\n")
            
            freq = data["frequencies"]
            if freq:
                f.write(f"\n  Частоты концептов-целей (все):\n")
                sorted_freq = sorted(freq.items(), key=lambda x: x[1]["andreev"], reverse=True)
                f.write(f"    {'Концепт':<22} {'Наши':>10} {'Андреев':>10} {'Разница':>10}\n")
                f.write(f"    {'-' * 22} {'-' * 10} {'-' * 10} {'-' * 10}\n")
                for concept, vals in sorted_freq:
                    f.write(f"    {concept:<22} {vals['our']:>10.4f} {vals['andreev']:>10.4f} {vals['diff']:>10.4f}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("ОЦЕНКА ТОЧНОСТИ\n")
        f.write("=" * 80 + "\n")
        
        summary = comparison["summary"]
        f.write(f"\n  Всего стихотворений в раннем периоде: {summary['total_poems_early']}\n")
        f.write(f"  Всего стихотворений в зрелом периоде: {summary['total_poems_late']}\n")
        f.write(f"\n  Средняя разница: {summary['avg_diff']:.4f}\n" if summary['avg_diff'] else "  Средняя разница: Н/Д\n")
        f.write(f"  Максимальная разница: {summary['max_diff']:.4f}\n" if summary['max_diff'] else "  Максимальная разница: Н/Д\n")
        f.write(f"\n  📈 Оценка точности: {summary['accuracy']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ\n")
        f.write("=" * 80 + "\n")
        
        if summary['accuracy'] == "Отличная":
            f.write("\n  Результаты на корпусе new-corpus практически полностью совпадают с данными Андреева.\n")
            f.write("  Это означает, что выборка текстов Набокова из нового корпуса хорошо репрезентирует его поэтический стиль.\n")
        elif summary['accuracy'] == "Хорошая":
            f.write("\n  Результаты на корпусе new-corpus близки к данным Андреева.\n")
            f.write("  Небольшие расхождения могут быть связаны с:\n")
            f.write("    - различным составом стихотворений\n")
            f.write("    - разной длиной текстов\n")
            f.write("    - особенностями методики выделения концептов\n")
        elif summary['accuracy'] == "Удовлетворительная":
            f.write("\n  Результаты на корпусе new-corpus требуют уточнения.\n")
            f.write("  Возможные причины расхождений:\n")
            f.write("    - неполнота корпуса (отсутствие некоторых ключевых текстов)\n")
            f.write("    - различия в методике выделения концептов\n")
            f.write("    - разные версии текстов\n")
        else:
            f.write("\n  Результаты требуют проверки и уточнения методики.\n")
            f.write("  Рекомендуется:\n")
            f.write("    - проверить состав корпуса\n")
            f.write("    - уточнить словарь концептов\n")
            f.write("    - проверить работу лемматизатора\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("КОНЕЦ ОТЧЕТА\n")
        f.write("=" * 80 + "\n")
    
    print(f"\n✅ Результаты сохранены в {output_file}")


def print_summary(comparison):
    """Краткий вывод в консоль."""
    print("\n" + "=" * 60)
    print("КРАТКИЙ ИТОГ")
    print("=" * 60)
    summary = comparison["summary"]
    print(f"\n  Средняя разница: {summary['avg_diff']:.4f}" if summary['avg_diff'] else "  Средняя разница: Н/Д")
    print(f"  Оценка точности: {summary['accuracy']}")
    print(f"\n  Полный отчет сохранен в {OUTPUT_FILE}")


def main():
    print("=" * 70)
    print("ВОСПРОИЗВЕДЕНИЕ ПОДСЧЕТОВ АНДРЕЕВА (ГЛАВА 1)")
    print("НА КОРПУСЕ new-corpus")
    print("=" * 70)
    
    poems_by_period = read_poems_from_new_corpus()
    
    print(f"\n📊 Найдено стихотворений:")
    print(f"  Ранний период (early): {len(poems_by_period['early'])}")
    # Показываем несколько примеров
    early_codes = list(poems_by_period['early'].keys())
    if early_codes:
        print(f"    Примеры: {', '.join(early_codes[:5])}")
        if len(early_codes) > 5:
            print(f"    ... и еще {len(early_codes) - 5}")
    
    print(f"  Зрелый период (late): {len(poems_by_period['late'])}")
    late_codes = list(poems_by_period['late'].keys())
    if late_codes:
        print(f"    Примеры: {', '.join(late_codes[:5])}")
        if len(late_codes) > 5:
            print(f"    ... и еще {len(late_codes) - 5}")
    
    if not poems_by_period['early'] and not poems_by_period['late']:
        print("\n❌ Нет стихотворений для анализа")
        print(f"   Проверьте содержимое папок:")
        print(f"   - {NEW_CORPUS_DIR / 'early'}")
        print(f"   - {NEW_CORPUS_DIR / 'late'}")
        return
    
    analyzer = ConceptAnalyzer()
    results = {}
    
    for period in ["early", "late"]:
        print(f"\n{'─' * 70}")
        print(f"АНАЛИЗ: {'Ранний период' if period == 'early' else 'Зрелый период'}")
        print(f"{'─' * 70}")
        
        poems = poems_by_period[period]
        if not poems:
            print("  Нет стихотворений для анализа")
            results[period] = {"poems": [], "concept_counts": {}, "total_metaphors": 0}
            continue
        
        concept_counts_by_text = []
        all_concept_counts = defaultdict(int)
        total_metaphors = 0
        
        # Обрабатываем все тексты
        for code, text in poems.items():
            concept_counts, total, lemmas = analyzer.analyze_text(text, TARGET_CONCEPTS)
            concept_counts_by_text.append(concept_counts)
            for concept, count in concept_counts.items():
                all_concept_counts[concept] += count
            total_metaphors += total
            print(f"  {code}: {total} метафор, {len(concept_counts)} концептов")
        
        frequencies = calculate_frequencies(all_concept_counts, total_metaphors)
        h_point = find_h_point(frequencies)
        concentration_index = calculate_concentration_index(frequencies, h_point)
        cv = calculate_cv(concept_counts_by_text)
        
        results[period] = {
            "poems": list(poems.keys()),
            "concept_counts": dict(all_concept_counts),
            "total_metaphors": total_metaphors,
            "target_frequencies": frequencies,
            "h_point": h_point,
            "concentration_index": concentration_index,
            "cv": cv
        }
        
        print(f"\n  Итоги:")
        print(f"    Всего метафор: {total_metaphors}")
        print(f"    Всего концептов: {len(frequencies)}")
        print(f"    Точка Хирша (h): {h_point:.2f}" if h_point else "    Точка Хирша (h): Н/Д")
        print(f"    Индекс концентрации: {concentration_index:.4f}")
        print(f"    Коэффициент вариации (CV): {cv:.4f}")
    
    # Сравнение
    comparison = compare_results(results, ANDREEV_DATA)
    
    # Сохраняем JSON
    save_results_json(results)
    print(f"\n✅ Результаты сохранены в {RESULTS_FILE}")
    
    # Записываем в файл
    write_output(comparison, results, OUTPUT_FILE)
    
    # Выводим краткий итог в консоль
    print_summary(comparison)


if __name__ == "__main__":
    main()