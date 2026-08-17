#!/usr/bin/env python3
"""
Воспроизведение подсчетов Андреева из Главы 2 на корпусе author-corpus.
Сравнение результатов с данными из монографии.
Результаты сохраняются в файл result_chapter2.txt
"""

import os
import re
import json
import math
from pathlib import Path
from collections import defaultdict, Counter
from pymystem3 import Mystem

# Пути
CORPUS_DIR = Path("../../author-corpus")
RESULTS_FILE = Path("../result/author-corpus2_results.json")
OUTPUT_FILE = Path("../result/result_chapter2.txt")

# Данные Андреева из монографии (для сравнения)
ANDREEV_DATA = {
    "Гроздь": {
        "poems": ["ГР-1", "ГР-2", "ГР-3", "ГР-4"],
        "frequencies": {
            "СЩ": {"mean": 31.38, "cv": 16.19},
            "ГЛ": {"mean": 13.37, "cv": 26.23},
            "ПЛ": {"mean": 15.30, "cv": 17.16},
            "НЧ": {"mean": 4.21, "cv": 22.52},
            "МС": {"mean": 4.99, "cv": 75.22},
            "МП": {"mean": 4.14, "cv": 61.03},
            "ПЧ": {"mean": 2.22, "cv": 14.48}
        },
        "nominality": {"mean": 0.30, "deviation_count": 2},
        "static_dynamic": {"mean": 0.54, "deviation_count": 3}
    },
    "Горний путь": {
        "poems": ["ГП-1", "ГП-2", "ГП-3", "ГП-4", "ГП-5", "ГП-6", "ГП-7", "ГП-8", 
                  "ГП-9", "ГП-10", "ГП-11", "ГП-12", "ГП-13", "ГП-14", "ГП-15"],
        "frequencies": {
            "СЩ": {"mean": 27.85, "cv": 14.95},
            "ГЛ": {"mean": 15.64, "cv": 20.25},
            "ПЛ": {"mean": 13.03, "cv": 21.08},
            "НЧ": {"mean": 6.52, "cv": 33.76},
            "МС": {"mean": 6.71, "cv": 35.53},
            "МП": {"mean": 3.55, "cv": 52.15},
            "ПЧ": {"mean": 2.14, "cv": 50.94}
        },
        "nominality": {"mean": 0.35, "deviation_count": 2},
        "static_dynamic": {"mean": 0.67, "deviation_count": 4}
    },
    "Возвращение Чорба": {
        "poems": ["ВЧ-1", "ВЧ-2", "ВЧ-3", "ВЧ-4", "ВЧ-5", "ВЧ-6", "ВЧ-7", "ВЧ-8", 
                  "ВЧ-9", "ВЧ-10", "ВЧ-11", "ВЧ-12", "ВЧ-13"],
        "frequencies": {
            "СЩ": {"mean": 31.02, "cv": 13.34},
            "ГЛ": {"mean": 14.64, "cv": 24.62},
            "ПЛ": {"mean": 12.31, "cv": 18.60},
            "НЧ": {"mean": 4.30, "cv": 29.89},
            "МС": {"mean": 5.09, "cv": 55.53},
            "МП": {"mean": 3.74, "cv": 57.85},
            "ПЧ": {"mean": 2.04, "cv": 75.19}
        },
        "nominality": {"mean": 0.32, "deviation_count": 0},
        "static_dynamic": {"mean": 0.46, "deviation_count": 4}
    },
    "Стихотворения 1929-1951": {
        "poems": ["СТ-1", "СТ-2", "СТ-3", "СТ-4", "СТ-5"],
        "frequencies": {
            "СЩ": {"mean": 30.36, "cv": 4.33},
            "ГЛ": {"mean": 12.26, "cv": 15.39},
            "ПЛ": {"mean": 10.51, "cv": 12.92},
            "НЧ": {"mean": 4.78, "cv": 18.68},
            "МС": {"mean": 7.17, "cv": 43.25},
            "МП": {"mean": 3.96, "cv": 23.88},
            "ПЧ": {"mean": 1.90, "cv": 37.43}
        },
        "nominality": {"mean": 0.29, "deviation_count": 3},
        "static_dynamic": {"mean": 0.46, "deviation_count": 2}
    }
}

# Сопоставление кодов стихотворений со сборниками
POEM_COLLECTIONS = {
    "ГР-1": "Гроздь", "ГР-2": "Гроздь", "ГР-3": "Гроздь", "ГР-4": "Гроздь",
    "ГП-1": "Горний путь", "ГП-2": "Горний путь", "ГП-3": "Горний путь",
    "ГП-4": "Горний путь", "ГП-5": "Горний путь", "ГП-6": "Горний путь",
    "ГП-7": "Горний путь", "ГП-8": "Горний путь", "ГП-9": "Горний путь",
    "ГП-10": "Горний путь", "ГП-11": "Горний путь", "ГП-12": "Горний путь",
    "ГП-13": "Горний путь", "ГП-14": "Горний путь", "ГП-15": "Горний путь",
    "ВЧ-1": "Возвращение Чорба", "ВЧ-2": "Возвращение Чорба",
    "ВЧ-3": "Возвращение Чорба", "ВЧ-4": "Возвращение Чорба",
    "ВЧ-5": "Возвращение Чорба", "ВЧ-6": "Возвращение Чорба",
    "ВЧ-7": "Возвращение Чорба", "ВЧ-8": "Возвращение Чорба",
    "ВЧ-9": "Возвращение Чорба", "ВЧ-10": "Возвращение Чорба",
    "ВЧ-11": "Возвращение Чорба", "ВЧ-12": "Возвращение Чорба",
    "ВЧ-13": "Возвращение Чорба",
    "СТ-1": "Стихотворения 1929-1951", "СТ-2": "Стихотворения 1929-1951",
    "СТ-3": "Стихотворения 1929-1951", "СТ-4": "Стихотворения 1929-1951",
    "СТ-5": "Стихотворения 1929-1951"
}


class POSAnalyzer:
    """Анализирует частеречную структуру текста."""
    
    def __init__(self):
        self.mystem = Mystem()
        
        # Части речи в pymystem3
        self.pos_tags = {
            'A': 'ПЛ',      # прилагательное
            'ADV': 'НЧ',    # наречие
            'ADVPRO': 'НЧ', # местоименное наречие
            'ANUM': 'ЧИС',  # числительное-прилагательное
            'APRO': 'МП',   # местоимение-прилагательное
            'COM': 'ЧАСТ',  # часть композита
            'CONJ': 'СОЮЗ', # союз
            'INTJ': 'МЕЖД', # междометие
            'NUM': 'ЧИС',   # числительное
            'PART': 'ЧАСТ', # частица
            'PR': 'ПРЕДЛ',  # предлог
            'S': 'СЩ',      # существительное
            'SPRO': 'МС',   # местоимение-существительное
            'V': 'ГЛ',      # глагол
            'ADPRO': 'МП',  # местоимение-прилагательное
        }
    
    def pos_tag_text(self, text):
        """Определяет части речи для всех слов в тексте."""
        # Удаляем метаданные (строки, начинающиеся с #)
        lines = text.split('\n')
        clean_lines = [line for line in lines if not line.startswith('#')]
        clean_text = ' '.join(clean_lines)
        
        # Анализируем с помощью mystem
        analyzed = self.mystem.analyze(clean_text)
        
        pos_counts = defaultdict(int)
        word_count = 0
        
        for item in analyzed:
            if 'analysis' not in item or not item['analysis']:
                continue
            
            analysis = item['analysis'][0]
            pos = analysis.get('gr', '')
            
            # Извлекаем основную часть речи
            if pos:
                pos_code = pos.split('=')[0] if '=' in pos else pos
                # Берем первую часть (до запятой или дефиса)
                pos_code = pos_code.split(',')[0].split('-')[0]
                
                # Упрощаем POS-теги
                if pos_code in self.pos_tags:
                    simplified_pos = self.pos_tags[pos_code]
                    pos_counts[simplified_pos] += 1
                    word_count += 1
        
        return pos_counts, word_count


def read_poems_by_period():
    """Читает стихотворения из папки author-corpus по сборникам."""
    poems_by_collection = defaultdict(dict)
    
    for collection_name in ["Гроздь", "Горний путь", "Возвращение Чорба", "Стихотворения 1929-1951"]:
        # Ищем папку сборника в разных главах
        for chapter in ["chapter_2", "chapter_3", "chapter_4"]:
            dir_path = CORPUS_DIR / chapter / collection_name
            if dir_path.exists():
                for file in dir_path.glob("*.txt"):
                    # Извлекаем код (ГР-1, ГП-2, ...)
                    code = file.stem.split('_')[0] if '_' in file.stem else file.stem
                    # Проверяем, что код принадлежит этому сборнику
                    if POEM_COLLECTIONS.get(code) == collection_name:
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                text = f.read()
                            poems_by_collection[collection_name][code] = text
                        except Exception as e:
                            print(f"Ошибка чтения {file}: {e}")
        
        # Если не нашли в подпапках, ищем в chapter_1 (для главы 1)
        if collection_name in ["Горний путь", "Стихотворения 1929-1951"]:
            period = "early_period" if collection_name == "Горний путь" else "late_period"
            dir_path = CORPUS_DIR / "chapter_1" / period
            if dir_path.exists():
                for file in dir_path.glob("*.txt"):
                    code = file.stem.split('_')[0] if '_' in file.stem else file.stem
                    if POEM_COLLECTIONS.get(code) == collection_name:
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                text = f.read()
                            poems_by_collection[collection_name][code] = text
                        except Exception as e:
                            print(f"Ошибка чтения {file}: {e}")
    
    return dict(poems_by_collection)


def calculate_cv(values):
    """Вычисляет коэффициент вариации."""
    if not values:
        return 0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(variance)
    return std / mean


def calculate_buzman(v1, v2):
    """Вычисляет коэффициент Бузмана."""
    if v1 + v2 == 0:
        return 0
    return v1 / (v1 + v2)


def calculate_chi_square(v1, v2):
    """Вычисляет хи-квадрат для коэффициента Бузмана."""
    if v1 + v2 == 0:
        return 0
    return (v1 - v2) ** 2 / (v1 + v2)


def compare_results(our_results, andreev_results):
    """Сравнивает наши подсчеты с данными Андреева."""
    comparison = {}
    
    for collection in andreev_results.keys():
        our = our_results.get(collection, {})
        andreev = andreev_results.get(collection, {})
        
        # Сравниваем частоты частей речи
        freq_comparison = {}
        for pos in ["СЩ", "ГЛ", "ПЛ", "НЧ", "МС", "МП", "ПЧ"]:
            our_mean = our.get("frequencies", {}).get(pos, {}).get("mean", 0)
            our_cv = our.get("frequencies", {}).get(pos, {}).get("cv", 0)
            andreev_mean = andreev.get("frequencies", {}).get(pos, {}).get("mean", 0)
            andreev_cv = andreev.get("frequencies", {}).get(pos, {}).get("cv", 0)
            
            freq_comparison[pos] = {
                "our_mean": our_mean,
                "andreev_mean": andreev_mean,
                "mean_diff": abs(our_mean - andreev_mean),
                "our_cv": our_cv,
                "andreev_cv": andreev_cv,
                "cv_diff": abs(our_cv - andreev_cv)
            }
        
        # Сравниваем номинальность
        our_nom = our.get("nominality", {})
        andreev_nom = andreev.get("nominality", {})
        
        # Сравниваем статику/динамику
        our_sd = our.get("static_dynamic", {})
        andreev_sd = andreev.get("static_dynamic", {})
        
        comparison[collection] = {
            "frequencies": freq_comparison,
            "nominality": {
                "our_mean": our_nom.get("mean", 0),
                "andreev_mean": andreev_nom.get("mean", 0),
                "mean_diff": abs(our_nom.get("mean", 0) - andreev_nom.get("mean", 0)),
                "our_deviation_count": our_nom.get("deviation_count", 0),
                "andreev_deviation_count": andreev_nom.get("deviation_count", 0)
            },
            "static_dynamic": {
                "our_mean": our_sd.get("mean", 0),
                "andreev_mean": andreev_sd.get("mean", 0),
                "mean_diff": abs(our_sd.get("mean", 0) - andreev_sd.get("mean", 0)),
                "our_deviation_count": our_sd.get("deviation_count", 0),
                "andreev_deviation_count": andreev_sd.get("deviation_count", 0)
            },
            "poems": {
                "our": len(our.get("poems", [])),
                "andreev": len(andreev.get("poems", []))
            }
        }
    
    # Вычисляем общую точность
    all_diffs = []
    for collection, data in comparison.items():
        for pos, freq_data in data["frequencies"].items():
            all_diffs.append(freq_data["mean_diff"])
            all_diffs.append(freq_data["cv_diff"])
        all_diffs.append(data["nominality"]["mean_diff"])
        all_diffs.append(data["static_dynamic"]["mean_diff"])
    
    if all_diffs:
        avg_diff = sum(all_diffs) / len(all_diffs)
        max_diff = max(all_diffs)
        if avg_diff < 0.5:
            accuracy = "Отличная"
        elif avg_diff < 1.0:
            accuracy = "Хорошая"
        elif avg_diff < 2.0:
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
        "accuracy": accuracy
    }
    
    return comparison


def write_output(comparison, results, output_file):
    """Записывает результаты в файл."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ВОСПРОИЗВЕДЕНИЕ ПОДСЧЕТОВ АНДРЕЕВА (ГЛАВА 2)\n")
        f.write("ЧАСТЕРЕЧНАЯ СТРУКТУРА ИНДИВИДУАЛЬНОГО СТИЛЯ\n")
        f.write("РЕЗУЛЬТАТЫ ОЦЕНКИ ТОЧНОСТИ\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Дата анализа: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Корпус: {CORPUS_DIR}\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("СТАТИСТИКА ПО КОРПУСУ\n")
        f.write("-" * 80 + "\n")
        
        for collection, data in results.items():
            f.write(f"\n  {collection}:\n")
            f.write(f"    Стихотворений: {len(data.get('poems', []))}\n")
            f.write(f"    Всего слов: {data.get('total_words', 0)}\n")
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("ЧАСТОТЫ ЧАСТЕЙ РЕЧИ (средние и CV)\n")
        f.write("-" * 80 + "\n")
        
        for collection, data in results.items():
            f.write(f"\n  {collection}:\n")
            freq = data.get("frequencies", {})
            f.write(f"    {'ЧР':<6} {'Среднее':>10} {'CV':>10}\n")
            f.write(f"    {'-' * 6} {'-' * 10} {'-' * 10}\n")
            for pos in ["СЩ", "ГЛ", "ПЛ", "НЧ", "МС", "МП", "ПЧ"]:
                pos_data = freq.get(pos, {})
                mean = pos_data.get("mean", 0)
                cv = pos_data.get("cv", 0)
                f.write(f"    {pos:<6} {mean:>10.2f} {cv:>10.2f}\n")
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("СРАВНЕНИЕ С ДАННЫМИ АНДРЕЕВА\n")
        f.write("-" * 80 + "\n")
        
        for collection, data in comparison.items():
            if collection == "summary":
                continue
            
            f.write(f"\n{'─' * 80}\n")
            f.write(f"📊 {collection}\n")
            f.write(f"{'─' * 80}\n")
            
            # Количество стихотворений
            poems = data["poems"]
            f.write(f"\n  Количество стихотворений:\n")
            f.write(f"    Наши данные: {poems['our']}\n")
            f.write(f"    Данные Андреева: {poems['andreev']}\n")
            
            # Частоты частей речи
            f.write(f"\n  Частоты частей речи:\n")
            f.write(f"    {'ЧР':<6} {'Наши (ср)':>12} {'Андреев (ср)':>14} {'Разница':>10} {'Наши (CV)':>12} {'Андреев (CV)':>14}\n")
            f.write(f"    {'-' * 6} {'-' * 12} {'-' * 14} {'-' * 10} {'-' * 12} {'-' * 14}\n")
            for pos in ["СЩ", "ГЛ", "ПЛ", "НЧ", "МС", "МП", "ПЧ"]:
                freq_data = data["frequencies"].get(pos, {})
                our_mean = freq_data.get("our_mean", 0)
                andreev_mean = freq_data.get("andreev_mean", 0)
                mean_diff = freq_data.get("mean_diff", 0)
                our_cv = freq_data.get("our_cv", 0)
                andreev_cv = freq_data.get("andreev_cv", 0)
                f.write(f"    {pos:<6} {our_mean:>12.2f} {andreev_mean:>14.2f} {mean_diff:>10.2f} {our_cv:>12.2f} {andreev_cv:>14.2f}\n")
            
            # Номинальность
            nom = data["nominality"]
            f.write(f"\n  Номинальность (ГЛ/СЩ):\n")
            f.write(f"    Наши данные: {nom['our_mean']:.2f}\n")
            f.write(f"    Данные Андреева: {nom['andreev_mean']:.2f}\n")
            f.write(f"    Разница: {nom['mean_diff']:.2f}\n")
            f.write(f"    Отклонений от нормы (наши): {nom['our_deviation_count']}\n")
            f.write(f"    Отклонений от нормы (Андреев): {nom['andreev_deviation_count']}\n")
            
            # Статика/динамика
            sd = data["static_dynamic"]
            f.write(f"\n  Статика/динамика (ПЛ/ГЛ):\n")
            f.write(f"    Наши данные: {sd['our_mean']:.2f}\n")
            f.write(f"    Данные Андреева: {sd['andreev_mean']:.2f}\n")
            f.write(f"    Разница: {sd['mean_diff']:.2f}\n")
            f.write(f"    Отклонений от нормы (наши): {sd['our_deviation_count']}\n")
            f.write(f"    Отклонений от нормы (Андреев): {sd['andreev_deviation_count']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("ОЦЕНКА ТОЧНОСТИ\n")
        f.write("=" * 80 + "\n")
        
        summary = comparison["summary"]
        f.write(f"\n  Средняя разница: {summary['avg_diff']:.4f}\n" if summary['avg_diff'] else "  Средняя разница: Н/Д\n")
        f.write(f"  Максимальная разница: {summary['max_diff']:.4f}\n" if summary['max_diff'] else "  Максимальная разница: Н/Д\n")
        f.write(f"\n  📈 Оценка точности: {summary['accuracy']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ\n")
        f.write("=" * 80 + "\n")
        
        if summary['accuracy'] == "Отличная":
            f.write("\n  Результаты программы практически полностью совпадают с данными Андреева.\n")
            f.write("  Различия в пределах погрешности измерений.\n")
        elif summary['accuracy'] == "Хорошая":
            f.write("\n  Результаты программы близки к данным Андреева.\n")
            f.write("  Небольшие расхождения могут быть связаны с:\n")
            f.write("    - различиями в POS-тэггере (pymystem3 vs. используемый Андреевым)\n")
            f.write("    - особенностями разбиения на слова\n")
            f.write("    - неполнотой корпуса\n")
        elif summary['accuracy'] == "Удовлетворительная":
            f.write("\n  Результаты программы требуют уточнения.\n")
            f.write("  Возможные причины расхождений:\n")
            f.write("    - неполный корпус стихотворений\n")
            f.write("    - различия в определении частей речи\n")
            f.write("    - особенности работы лемматизатора/тэггера\n")
        else:
            f.write("\n  Результаты требуют проверки и уточнения методики.\n")
        
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


def analyze_collection(analyzer, poems):
    """Анализирует один сборник."""
    pos_counts_by_text = []
    all_pos_counts = defaultdict(int)
    total_words = 0
    nominality_values = []
    static_dynamic_values = []
    nominality_deviations = 0
    static_dynamic_deviations = 0
    
    for code, text in poems.items():
        pos_counts, word_count = analyzer.pos_tag_text(text)
        if word_count > 0:
            pos_counts_by_text.append(pos_counts)
            for pos, count in pos_counts.items():
                all_pos_counts[pos] += count
            total_words += word_count
            
            # Вычисляем номинальность (ГЛ-СЩ)
            gl = pos_counts.get("ГЛ", 0)
            sc = pos_counts.get("СЩ", 0)
            nominality = calculate_buzman(gl, sc)
            nominality_values.append(nominality)
            
            # Проверяем отклонение от нормы (0.30)
            if abs(nominality - 0.30) > 0.10:
                nominality_deviations += 1
            
            # Вычисляем статику/динамику (ПЛ-ГЛ)
            pl = pos_counts.get("ПЛ", 0)
            gl2 = pos_counts.get("ГЛ", 0)
            static_dynamic = calculate_buzman(pl, gl2)
            static_dynamic_values.append(static_dynamic)
            
            # Проверяем отклонение от нормы (0.50)
            if abs(static_dynamic - 0.50) > 0.10:
                static_dynamic_deviations += 1
            
            print(f"    {code}: {word_count} слов, Ном={nominality:.2f}, СД={static_dynamic:.2f}")
    
    # Вычисляем средние частоты
    freq_means = {}
    for pos in ["СЩ", "ГЛ", "ПЛ", "НЧ", "МС", "МП", "ПЧ"]:
        values = [counts.get(pos, 0) for counts in pos_counts_by_text]
        if values:
            mean = sum(values) / len(values)
            freq_means[pos] = mean
        else:
            freq_means[pos] = 0
    
    # Вычисляем CV для каждой части речи
    freq_cv = {}
    for pos in ["СЩ", "ГЛ", "ПЛ", "НЧ", "МС", "МП", "ПЧ"]:
        values = [counts.get(pos, 0) for counts in pos_counts_by_text]
        cv = calculate_cv(values)
        freq_cv[pos] = cv
    
    # Вычисляем среднюю номинальность
    nominality_mean = sum(nominality_values) / len(nominality_values) if nominality_values else 0
    
    # Вычисляем среднюю статику/динамику
    static_dynamic_mean = sum(static_dynamic_values) / len(static_dynamic_values) if static_dynamic_values else 0
    
    return {
        "poems": list(poems.keys()),
        "total_words": total_words,
        "frequencies": {pos: {"mean": freq_means.get(pos, 0), "cv": freq_cv.get(pos, 0)} 
                       for pos in ["СЩ", "ГЛ", "ПЛ", "НЧ", "МС", "МП", "ПЧ"]},
        "nominality": {
            "mean": nominality_mean,
            "deviation_count": nominality_deviations,
            "values": nominality_values
        },
        "static_dynamic": {
            "mean": static_dynamic_mean,
            "deviation_count": static_dynamic_deviations,
            "values": static_dynamic_values
        }
    }


def main():
    print("=" * 70)
    print("ВОСПРОИЗВЕДЕНИЕ ПОДСЧЕТОВ АНДРЕЕВА (ГЛАВА 2)")
    print("=" * 70)
    
    # Читаем стихотворения
    poems_by_collection = read_poems_by_period()
    
    print(f"\nНайдено стихотворений по сборникам:")
    for collection, poems in poems_by_collection.items():
        print(f"  {collection}: {len(poems)}")
        for code in poems:
            print(f"    - {code}")
    
    if not poems_by_collection:
        print("\n❌ Нет стихотворений для анализа")
        return
    
    # Инициализируем анализатор
    analyzer = POSAnalyzer()
    results = {}
    
    for collection, poems in poems_by_collection.items():
        print(f"\n{'─' * 70}")
        print(f"АНАЛИЗ: {collection}")
        print(f"{'─' * 70}")
        
        if not poems:
            print("  Нет стихотворений для анализа")
            continue
        
        results[collection] = analyze_collection(analyzer, poems)
        
        print(f"\n  Итоги:")
        print(f"    Всего слов: {results[collection]['total_words']}")
        print(f"    Номинальность (ср): {results[collection]['nominality']['mean']:.2f}")
        print(f"    Статика/динамика (ср): {results[collection]['static_dynamic']['mean']:.2f}")
    
    # Сравнение
    comparison = compare_results(results, ANDREEV_DATA)
    
    # Сохраняем JSON
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Результаты сохранены в {RESULTS_FILE}")
    
    # Записываем в файл
    write_output(comparison, results, OUTPUT_FILE)
    
    # Выводим краткий итог в консоль
    print_summary(comparison)


if __name__ == "__main__":
    main()