#!/usr/bin/env python3
"""
Воспроизведение подсчетов Андреева из Главы 4 на корпусе author-corpus.
Сравнение результатов с данными из монографии.
Результаты сохраняются в файл result_chapter4.txt

ВСЕ ФАЙЛЫ ДЛЯ ГЛАВЫ 4 НАХОДЯТСЯ В ПАПКЕ chapter_4.
СКРИПТ ЧИТАЕТ ИХ НЕПОСРЕДСТВЕННО ОТТУДА.
"""

import os
import sys
import json
import math
import re
from pathlib import Path
from collections import defaultdict, Counter

# Пути
CORPUS_DIR = Path("../../author-corpus")
RESULTS_FILE = Path("../result/author-corpus4_results.json")
OUTPUT_FILE = Path("../result/result_chapter4.txt")

# Данные Андреева из монографии (для сравнения)
ANDREEV_DATA = {
    "Гроздь_4-ст": {
        "poems": [f"ФГ-{i}" for i in range(1, 13)],
        "avg_syllables_per_line": 8.5,
        "open_syllables_pct": 59,
        "u_value": 7.49,
        "chi_square_symmetry": 943.10,
        "symmetry_index_T": 0.723,
        "similarity_mean": 5.3,
        "similarity_cv": 13.5,
        "cv": {
            "Г": 40.5, "СГ": 35.6, "ССГ": 57.6, "СГС": 38.4,
            "ССГС": 43.6, "СГСС": 133.1, "СССГ": 106.2,
            "ГС": 93.9, "СССГС": 134.8
        }
    },
    "Гроздь_5-ст": {
        "poems": [f"ФГ-{i}" for i in range(13, 18)],
        "avg_syllables_per_line": 10.3,
        "open_syllables_pct": 54,
        "u_value": 2.33,
        "chi_square_symmetry": 523.62,
        "symmetry_index_T": 0.622,
        "similarity_mean": 6.7,
        "similarity_cv": 18.9,
        "cv": {
            "Г": 31.1, "СГ": 31.2, "ССГ": 34.4, "СГС": 31.6,
            "ССГС": 37.6, "СГСС": 49.4, "СССГ": 50.6,
            "ГС": 41.6, "СССГС": 45.4
        }
    },
    "Возвращение Чорба_4-ст": {
        "poems": [f"ФЧ-{i}" for i in range(1, 10)],
        "open_syllables_pct": 62,
        "u_value": 11.23,
        "chi_square_symmetry": 1310.73,
        "symmetry_index_T": 0.614,
        "similarity_mean": 5.4,
        "similarity_cv": 5.4,
        "cv": {
            "Г": 51.3, "СГ": 38.1, "ССГ": 39.1, "СГС": 39.3,
            "ССГС": 51.3, "СГСС": 116.2, "СССГ": 67.2,
            "ГС": 25.0, "СССГС": 167.4
        }
    },
    "Возвращение Чорба_5-ст": {
        "poems": [f"ФЧ-{i}" for i in range(10, 17)],
        "open_syllables_pct": 61,
        "u_value": 9.72,
        "chi_square_symmetry": 1140.94,
        "symmetry_index_T": 0.616,
        "similarity_mean": 6.5,
        "similarity_cv": 11.4,
        "cv": {
            "Г": 49.4, "СГ": 34.5, "ССГ": 44.5, "СГС": 46.0,
            "ССГС": 30.6, "СГСС": 116.4, "СССГ": 46.2,
            "ГС": 47.4, "СССГС": 76.4
        }
    }
}

# ===================================================================
# СТРУКТУРА ПАПОК ДЛЯ ГЛАВЫ 4
# ===================================================================

# Все файлы находятся в папке chapter_4
# Структура:
#   chapter_4/Гроздь/4-ст ямб/   -> ФГ-1.txt ... ФГ-12.txt
#   chapter_4/Гроздь/5-ст ямб/   -> ФГ-13.txt ... ФГ-17.txt
#   chapter_4/Возвращение Чорба/4-ст ямб/ -> ФЧ-1.txt ... ФЧ-9.txt
#   chapter_4/Возвращение Чорба/5-ст ямб/ -> ФЧ-10.txt ... ФЧ-16.txt

FOLDER_MAPPING = {
    "Гроздь_4-ст": "Гроздь/4-ст ямб",
    "Гроздь_5-ст": "Гроздь/5-ст ямб",
    "Возвращение Чорба_4-ст": "Возвращение Чорба/4-ст ямб",
    "Возвращение Чорба_5-ст": "Возвращение Чорба/5-ст ямб",
}

# Ожидаемые коды для каждой группы (для проверки)
EXPECTED_CODES = {
    "Гроздь_4-ст": [f"ФГ-{i}" for i in range(1, 13)],
    "Гроздь_5-ст": [f"ФГ-{i}" for i in range(13, 18)],
    "Возвращение Чорба_4-ст": [f"ФЧ-{i}" for i in range(1, 10)],
    "Возвращение Чорба_5-ст": [f"ФЧ-{i}" for i in range(10, 17)],
}


class SyllableAnalyzer:
    """Анализирует слоговую структуру текста."""
    
    # Типы слогов по структуре
    SYLLABLE_TYPES = {
        'Г': r'^[аеёиоуыэюя]$',
        'СГ': r'^[бвгджзйклмнпрстфхцчшщ][аеёиоуыэюя]$',
        'ССГ': r'^[бвгджзйклмнпрстфхцчшщ]{2}[аеёиоуыэюя]$',
        'СГС': r'^[бвгджзйклмнпрстфхцчшщ][аеёиоуыэюя][бвгджзйклмнпрстфхцчшщ]$',
        'ССГС': r'^[бвгджзйклмнпрстфхцчшщ]{2}[аеёиоуыэюя][бвгджзйклмнпрстфхцчшщ]$',
        'СГСС': r'^[бвгджзйклмнпрстфхцчшщ][аеёиоуыэюя][бвгджзйклмнпрстфхцчшщ]{2}$',
        'СССГ': r'^[бвгджзйклмнпрстфхцчшщ]{3}[аеёиоуыэюя]$',
        'ГС': r'^[аеёиоуыэюя][бвгджзйклмнпрстфхцчшщ]$',
        'ССГСС': r'^[бвгджзйклмнпрстфхцчшщ]{2}[аеёиоуыэюя][бвгджзйклмнпрстфхцчшщ]{2}$',
        'СССГС': r'^[бвгджзйклмнпрстфхцчшщ]{3}[аеёиоуыэюя][бвгджзйклмнпрстфхцчшщ]$',
        'ССССГ': r'^[бвгджзйклмнпрстфхцчшщ]{4}[аеёиоуыэюя]$',
        'ССССГС': r'^[бвгджзйклмнпрстфхцчшщ]{4}[аеёиоуыэюя][бвгджзйклмнпрстфхцчшщ]$',
        'СССГСС': r'^[бвгджзйклмнпрстфхцчшщ]{3}[аеёиоуыэюя][бвгджзйклмнпрстфхцчшщ]{2}$',
    }
    
    VOWELS = set('аеёиоуыэюя')
    CONSONANTS = set('бвгджзйклмнпрстфхцчшщ')
    
    def __init__(self):
        self.type_patterns = {}
        for type_name, pattern in self.SYLLABLE_TYPES.items():
            self.type_patterns[type_name] = re.compile(pattern)
    
    def _split_into_syllables(self, word):
        """Разбивает слово на слоги (упрощенная версия)."""
        if not word:
            return []
        
        syllables = []
        current = ""
        
        for char in word.lower():
            if char in self.VOWELS:
                current += char
                syllables.append(current)
                current = ""
            elif char in self.CONSONANTS:
                if syllables and len(syllables[-1]) > 0 and syllables[-1][-1] in self.VOWELS:
                    if current:
                        syllables[-1] += current + char
                        current = ""
                    else:
                        syllables[-1] += char
                else:
                    current += char
        
        if current:
            if syllables:
                syllables[-1] += current
            else:
                syllables.append(current)
        
        return syllables
    
    def _get_syllable_type(self, syllable):
        """Определяет тип слога по его структуре."""
        if not syllable:
            return None
        for type_name, pattern in self.type_patterns.items():
            if pattern.match(syllable.lower()):
                return type_name
        return None
    
    def _is_open_syllable(self, syllable_type):
        """Проверяет, является ли слог открытым."""
        open_types = ['Г', 'СГ', 'ССГ', 'СССГ']
        return syllable_type in open_types
    
    def _count_consonants(self, syllable):
        """Подсчитывает количество согласных в инициали и финали."""
        if not syllable:
            return 0, 0
        
        syl_lower = syllable.lower()
        
        # Согласные в начале (инициаль)
        init = ""
        for char in syl_lower:
            if char in self.VOWELS:
                break
            init += char
        
        # Согласные в конце (финаль)
        final = ""
        for char in reversed(syl_lower):
            if char in self.VOWELS:
                break
            final = char + final
        
        return len(init), len(final)
    
    def analyze_text(self, text):
        """Полный анализ слоговой структуры текста."""
        # Разбиваем на строки
        lines = text.split('\n')
        
        # Убираем пустые строки и строки с комментариями
        clean_lines = [line for line in lines if line.strip() and not line.startswith('#')]
        
        # Объединяем строки для подсчета слов
        clean_text = ' '.join(clean_lines)
        
        # Находим все слова (только буквы, включая русские и английские)
        words = re.findall(r'[а-яА-ЯёЁa-zA-Z]+', clean_text)
        
        if not words:
            return self._empty_result()
        
        syllable_types = defaultdict(int)
        open_count = 0
        closed_count = 0
        total_syllables = 0
        init_final_counts = defaultdict(lambda: defaultdict(int))
        
        # Разбиваем слова на слоги
        for word in words:
            syllables = self._split_into_syllables(word)
            for syl in syllables:
                if not syl:
                    continue
                syl_type = self._get_syllable_type(syl)
                if syl_type:
                    syllable_types[syl_type] += 1
                    total_syllables += 1
                    
                    if self._is_open_syllable(syl_type):
                        open_count += 1
                    else:
                        closed_count += 1
                    
                    init_count, final_count = self._count_consonants(syl)
                    if init_count <= 3 and final_count <= 3:
                        init_final_counts[init_count][final_count] += 1
        
        # Расчет процента открытых слогов
        open_pct = open_count / total_syllables * 100 if total_syllables > 0 else 0
        
        # U-критерий для открытых/закрытых слогов
        p = open_count / (open_count + closed_count) if (open_count + closed_count) > 0 else 0.5
        n = open_count + closed_count
        u_value = (p - 0.5) / math.sqrt(0.5 * 0.5 / n) if n > 0 else 0
        
        # χ² для симметрии слогов
        chi_square = 0
        for i in range(4):
            for j in range(4):
                if i != j:
                    n_ij = init_final_counts[i][j]
                    n_ji = init_final_counts[j][i]
                    if n_ij + n_ji > 0:
                        chi_square += (n_ij - n_ji) ** 2 / (n_ij + n_ji)
        
        # Индекс асимметрии T
        total_pairs = sum(sum(row.values()) for row in init_final_counts.values())
        if total_pairs > 0:
            asym_sum = 0
            for i in range(4):
                for j in range(4):
                    if i != j:
                        n_ij = init_final_counts[i][j]
                        n_ji = init_final_counts[j][i]
                        if n_ij + n_ji > 0:
                            asym_sum += abs(n_ij - n_ji) / (n_ij + n_ji)
            T = asym_sum / 6
        else:
            T = 0
        
        # Сходство строк (проверяем слова в строках)
        similarities = []
        if len(clean_lines) >= 2:
            for i in range(len(clean_lines) - 1):
                line1 = clean_lines[i]
                line2 = clean_lines[i + 1]
                
                # Находим слова в каждой строке
                words1 = re.findall(r'[а-яА-ЯёЁa-zA-Z]+', line1)
                words2 = re.findall(r'[а-яА-ЯёЁa-zA-Z]+', line2)
                
                if not words1 or not words2:
                    continue
                
                # Сравниваем слоги первых слов
                match_count = 0
                min_len = min(len(words1), len(words2))
                for j in range(min_len):
                    syl1 = self._split_into_syllables(words1[j]) if words1[j] else []
                    syl2 = self._split_into_syllables(words2[j]) if words2[j] else []
                    if syl1 and syl2:
                        type1 = self._get_syllable_type(syl1[0])
                        type2 = self._get_syllable_type(syl2[0])
                        if type1 and type2 and type1 == type2:
                            match_count += 1
                similarities.append(match_count)
        
        similarity_mean = sum(similarities) / len(similarities) if similarities else 0
        similarity_cv = self._calculate_cv(similarities) if similarities else 0
        
        # Коэффициенты вариации - собираем данные по каждому типу
        cv = {}
        for syl_type in ['Г', 'СГ', 'ССГ', 'СГС', 'ССГС', 'СГСС', 'СССГ', 'ГС', 'СССГС']:
            # Считаем частоту этого типа во всех словах
            freq = syllable_types.get(syl_type, 0) / total_syllables * 100 if total_syllables > 0 else 0
            cv[syl_type] = freq  # Здесь будем хранить частоту, а CV посчитаем позже для всего корпуса
        
        return {
            'syllable_types': dict(syllable_types),
            'total_syllables': total_syllables,
            'open_count': open_count,
            'closed_count': closed_count,
            'open_pct': open_pct,
            'u_value': u_value,
            'chi_square_symmetry': chi_square,
            'symmetry_index_T': T,
            'similarity_mean': similarity_mean,
            'similarity_cv': similarity_cv,
            'cv': cv,
            'init_final_counts': {str(k): dict(v) for k, v in init_final_counts.items()}
        }
    
    def _calculate_cv(self, values):
        """Вычисляет коэффициент вариации."""
        if not values or len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        if mean == 0:
            return 0
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance)
        return std / mean * 100
    
    def _empty_result(self):
        """Возвращает пустой результат."""
        return {
            'syllable_types': {},
            'total_syllables': 0,
            'open_count': 0,
            'closed_count': 0,
            'open_pct': 0,
            'u_value': 0,
            'chi_square_symmetry': 0,
            'symmetry_index_T': 0,
            'similarity_mean': 0,
            'similarity_cv': 0,
            'cv': {},
            'init_final_counts': {}
        }


def read_poems_by_group():
    """
    Читает все стихотворения из папки chapter_4.
    Все файлы для Главы 4 находятся именно там.
    """
    poems_by_group = defaultdict(dict)
    
    print("\n🔍 Чтение файлов из папки chapter_4...")
    print(f"Корпус: {CORPUS_DIR}")
    
    chapter_4_dir = CORPUS_DIR / "chapter_4"
    if not chapter_4_dir.exists():
        print(f"  ❌ Папка {chapter_4_dir} не найдена")
        return {}
    
    print(f"  ✅ Папка {chapter_4_dir} найдена")
    
    total_found = 0
    total_expected = 0
    
    for group, rel_path in FOLDER_MAPPING.items():
        folder_path = chapter_4_dir / rel_path
        expected_codes = EXPECTED_CODES.get(group, [])
        total_expected += len(expected_codes)
        
        if not folder_path.exists():
            print(f"  ⚠️ Папка {folder_path} не найдена")
            continue
        
        # Читаем все .txt файлы в папке
        files = list(folder_path.glob("*.txt"))
        print(f"\n  📁 {rel_path}: найдено {len(files)} файлов")
        
        for file in sorted(files):
            code = file.stem  # Имя файла без расширения (например, "ФГ-1")
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read()
                poems_by_group[group][code] = text
                total_found += 1
                print(f"    ✅ {code}")
            except Exception as e:
                print(f"    ❌ Ошибка чтения {file}: {e}")
    
    # Проверка: все ли ожидаемые файлы найдены
    print(f"\n{'='*60}")
    print("📊 ПРОВЕРКА ПОЛНОТЫ КОРПУСА")
    print("="*60)
    
    all_found = True
    for group, expected_codes in EXPECTED_CODES.items():
        found_codes = set(poems_by_group.get(group, {}).keys())
        missing = [c for c in expected_codes if c not in found_codes]
        extra = [c for c in found_codes if c not in expected_codes]
        
        status = "✅" if not missing and not extra else "⚠️"
        print(f"  {status} {group}: {len(found_codes)}/{len(expected_codes)}")
        if missing:
            print(f"      ❌ Отсутствуют: {', '.join(missing)}")
            all_found = False
        if extra:
            print(f"      📌 Лишние: {', '.join(extra)}")
    
    if all_found:
        print("\n  ✅ ВСЕ ФАЙЛЫ НА МЕСТЕ! Корпус полностью соответствует корпусу Андреева.")
    else:
        print("\n  ⚠️ Есть пропуски. Проверьте структуру папок.")
    
    print(f"\nИтого: {total_found} из {total_expected} файлов")
    
    return dict(poems_by_group)


def compare_results(our_results, andreev_results):
    """Сравнивает наши подсчеты с данными Андреева."""
    comparison = {}
    
    for group in andreev_results.keys():
        our = our_results.get(group, {})
        andreev = andreev_results.get(group, {})
        
        comparison[group] = {
            "open_pct": {
                "our": our.get("open_pct", 0),
                "andreev": andreev.get("open_syllables_pct", 0),
                "diff": abs(our.get("open_pct", 0) - andreev.get("open_syllables_pct", 0))
            },
            "u_value": {
                "our": our.get("u_value", 0),
                "andreev": andreev.get("u_value", 0),
                "diff": abs(our.get("u_value", 0) - andreev.get("u_value", 0))
            },
            "chi_square": {
                "our": our.get("chi_square_symmetry", 0),
                "andreev": andreev.get("chi_square_symmetry", 0),
                "diff": abs(our.get("chi_square_symmetry", 0) - andreev.get("chi_square_symmetry", 0))
            },
            "symmetry_T": {
                "our": our.get("symmetry_index_T", 0),
                "andreev": andreev.get("symmetry_index_T", 0),
                "diff": abs(our.get("symmetry_index_T", 0) - andreev.get("symmetry_index_T", 0))
            },
            "similarity_mean": {
                "our": our.get("similarity_mean", 0),
                "andreev": andreev.get("similarity_mean", 0),
                "diff": abs(our.get("similarity_mean", 0) - andreev.get("similarity_mean", 0))
            },
            "similarity_cv": {
                "our": our.get("similarity_cv", 0),
                "andreev": andreev.get("similarity_cv", 0),
                "diff": abs(our.get("similarity_cv", 0) - andreev.get("similarity_cv", 0))
            },
            "poems_count": {
                "our": len(our.get("poems", [])),
                "andreev": len(andreev.get("poems", []))
            },
            "cv": {}
        }
        
        our_cv = our.get("cv", {})
        andreev_cv = andreev.get("cv", {})
        for syl_type in set(our_cv.keys()) | set(andreev_cv.keys()):
            comparison[group]["cv"][syl_type] = {
                "our": our_cv.get(syl_type, 0),
                "andreev": andreev_cv.get(syl_type, 0),
                "diff": abs(our_cv.get(syl_type, 0) - andreev_cv.get(syl_type, 0))
            }
    
    # Расчет общей точности
    all_diffs = []
    for group, data in comparison.items():
        if group == "summary":
            continue
        all_diffs.append(data["open_pct"]["diff"])
        all_diffs.append(data["u_value"]["diff"])
        all_diffs.append(data["chi_square"]["diff"] / 100)
        all_diffs.append(data["symmetry_T"]["diff"])
        all_diffs.append(data["similarity_mean"]["diff"])
        all_diffs.append(data["similarity_cv"]["diff"])
        for syl_data in data["cv"].values():
            all_diffs.append(syl_data["diff"])
    
    valid_diffs = [d for d in all_diffs if d > 0]
    
    if valid_diffs:
        avg_diff = sum(valid_diffs) / len(valid_diffs)
        max_diff = max(valid_diffs)
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
        f.write("ВОСПРОИЗВЕДЕНИЕ ПОДСЧЕТОВ АНДРЕЕВА (ГЛАВА 4)\n")
        f.write("СООТНОШЕНИЕ СЛОГОВЫХ ТИПОВ\n")
        f.write("РЕЗУЛЬТАТЫ ОЦЕНКИ ТОЧНОСТИ\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Дата анализа: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Корпус: {CORPUS_DIR}\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("СТАТИСТИКА ПО КОРПУСУ\n")
        f.write("-" * 80 + "\n")
        
        for group, data in results.items():
            f.write(f"\n  {group}:\n")
            f.write(f"    Стихотворений: {len(data.get('poems', []))}\n")
            f.write(f"    Всего слогов: {data.get('total_syllables', 0)}\n")
            f.write(f"    Открытые слоги: {data.get('open_pct', 0):.1f}%\n")
            f.write(f"    U-критерий: {data.get('u_value', 0):.2f}\n")
            f.write(f"    χ² симметрии: {data.get('chi_square_symmetry', 0):.2f}\n")
            f.write(f"    Индекс асимметрии T: {data.get('symmetry_index_T', 0):.3f}\n")
            f.write(f"    Сходство строк (ср): {data.get('similarity_mean', 0):.2f}\n")
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("СРАВНЕНИЕ С ДАННЫМИ АНДРЕЕВА\n")
        f.write("-" * 80 + "\n")
        
        for group, data in comparison.items():
            if group == "summary":
                continue
            
            f.write(f"\n{'─' * 80}\n")
            f.write(f"📊 {group}\n")
            f.write(f"{'─' * 80}\n")
            
            poems = data["poems_count"]
            f.write(f"\n  Количество стихотворений:\n")
            f.write(f"    Наши данные: {poems['our']}\n")
            f.write(f"    Данные Андреева: {poems['andreev']}\n")
            
            op = data["open_pct"]
            f.write(f"\n  Открытые слоги (%):\n")
            f.write(f"    Наши данные: {op['our']:.1f}%\n")
            f.write(f"    Данные Андреева: {op['andreev']:.1f}%\n")
            f.write(f"    Разница: {op['diff']:.1f}%\n")
            
            u = data["u_value"]
            f.write(f"\n  U-критерий (открытые/закрытые):\n")
            f.write(f"    Наши данные: {u['our']:.2f}\n")
            f.write(f"    Данные Андреева: {u['andreev']:.2f}\n")
            f.write(f"    Разница: {u['diff']:.2f}\n")
            
            chi = data["chi_square"]
            f.write(f"\n  χ² симметрии слогов:\n")
            f.write(f"    Наши данные: {chi['our']:.2f}\n")
            f.write(f"    Данные Андреева: {chi['andreev']:.2f}\n")
            f.write(f"    Разница: {chi['diff']:.2f}\n")
            
            T = data["symmetry_T"]
            f.write(f"\n  Индекс асимметрии T:\n")
            f.write(f"    Наши данные: {T['our']:.3f}\n")
            f.write(f"    Данные Андреева: {T['andreev']:.3f}\n")
            f.write(f"    Разница: {T['diff']:.3f}\n")
            
            sim = data["similarity_mean"]
            f.write(f"\n  Сходство строк (среднее):\n")
            f.write(f"    Наши данные: {sim['our']:.2f}\n")
            f.write(f"    Данные Андреева: {sim['andreev']:.2f}\n")
            f.write(f"    Разница: {sim['diff']:.2f}\n")
            
            sim_cv = data["similarity_cv"]
            f.write(f"\n  Сходство строк (CV):\n")
            f.write(f"    Наши данные: {sim_cv['our']:.1f}%\n")
            f.write(f"    Данные Андреева: {sim_cv['andreev']:.1f}%\n")
            f.write(f"    Разница: {sim_cv['diff']:.1f}%\n")
            
            cv_data = data["cv"]
            if cv_data:
                f.write(f"\n  Коэффициенты вариации (CV) по типам слогов:\n")
                f.write(f"    {'Тип':<10} {'Наши':>10} {'Андреев':>10} {'Разница':>10}\n")
                f.write(f"    {'-' * 10} {'-' * 10} {'-' * 10} {'-' * 10}\n")
                for syl_type, vals in sorted(cv_data.items()):
                    f.write(f"    {syl_type:<10} {vals['our']:>10.1f} {vals['andreev']:>10.1f} {vals['diff']:>10.1f}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("ОЦЕНКА ТОЧНОСТИ\n")
        f.write("=" * 80 + "\n")
        
        summary = comparison["summary"]
        if summary['avg_diff'] is not None:
            f.write(f"\n  Средняя разница: {summary['avg_diff']:.4f}\n")
            f.write(f"  Максимальная разница: {summary['max_diff']:.4f}\n")
        else:
            f.write("\n  Нет данных для сравнения.\n")
        
        f.write(f"\n  📈 Оценка точности: {summary['accuracy']}\n")
        
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
    if summary['avg_diff'] is not None:
        print(f"\n  Средняя разница: {summary['avg_diff']:.4f}")
    else:
        print("\n  Нет данных для сравнения")
    print(f"  Оценка точности: {summary['accuracy']}")
    print(f"\n  Полный отчет сохранен в {OUTPUT_FILE}")


def aggregate_group_results(analyzer, poems):
    """
    Агрегирует результаты анализа всех стихотворений в группе.
    """
    combined_result = {
        'syllable_types': defaultdict(int),
        'total_syllables': 0,
        'open_count': 0,
        'closed_count': 0,
        'open_pct': 0,
        'u_value': 0,
        'chi_square_symmetry': 0,
        'symmetry_index_T': 0,
        'similarity_mean': 0,
        'similarity_cv': 0,
        'cv': {},
        'init_final_counts': defaultdict(lambda: defaultdict(int)),
        'similarities': [],
        'poems': list(poems.keys()),
        'per_poem_cv_data': defaultdict(list)
    }
    
    for code, text in poems.items():
        result = analyzer.analyze_text(text)
        
        for syl_type, count in result['syllable_types'].items():
            combined_result['syllable_types'][syl_type] += count
        
        combined_result['total_syllables'] += result['total_syllables']
        combined_result['open_count'] += result['open_count']
        combined_result['closed_count'] += result['closed_count']
        
        for k, v in result.get('init_final_counts', {}).items():
            for j, count in v.items():
                combined_result['init_final_counts'][int(k)][int(j)] += count
        
        total = result['total_syllables']
        if total > 0:
            for syl_type in ['Г', 'СГ', 'ССГ', 'СГС', 'ССГС', 'СГСС', 'СССГ', 'ГС', 'СССГС']:
                freq = result['syllable_types'].get(syl_type, 0) / total * 100
                combined_result['per_poem_cv_data'][syl_type].append(freq)
        
        if result['similarity_mean'] > 0:
            combined_result['similarities'].append(result['similarity_mean'])
        
        print(f"    {code}: {result['total_syllables']} слогов, открытые={result['open_pct']:.1f}%, U={result['u_value']:.2f}")
    
    total = combined_result['total_syllables']
    if total > 0:
        combined_result['open_pct'] = combined_result['open_count'] / total * 100
        
        p = combined_result['open_count'] / total
        n = total
        combined_result['u_value'] = (p - 0.5) / math.sqrt(0.5 * 0.5 / n) if n > 0 else 0
        
        chi_square = 0
        init_final = combined_result['init_final_counts']
        for i in range(4):
            for j in range(4):
                if i != j:
                    n_ij = init_final[i][j]
                    n_ji = init_final[j][i]
                    if n_ij + n_ji > 0:
                        chi_square += (n_ij - n_ji) ** 2 / (n_ij + n_ji)
        combined_result['chi_square_symmetry'] = chi_square
        
        total_pairs = sum(sum(row.values()) for row in init_final.values())
        if total_pairs > 0:
            asym_sum = 0
            for i in range(4):
                for j in range(4):
                    if i != j:
                        n_ij = init_final[i][j]
                        n_ji = init_final[j][i]
                        if n_ij + n_ji > 0:
                            asym_sum += abs(n_ij - n_ji) / (n_ij + n_ji)
            combined_result['symmetry_index_T'] = asym_sum / 6
        
        if combined_result['similarities']:
            combined_result['similarity_mean'] = sum(combined_result['similarities']) / len(combined_result['similarities'])
            combined_result['similarity_cv'] = analyzer._calculate_cv(combined_result['similarities'])
        
        for syl_type, values in combined_result['per_poem_cv_data'].items():
            combined_result['cv'][syl_type] = analyzer._calculate_cv(values)
    
    return combined_result


def main():
    print("=" * 70)
    print("ВОСПРОИЗВЕДЕНИЕ ПОДСЧЕТОВ АНДРЕЕВА (ГЛАВА 4)")
    print("СООТНОШЕНИЕ СЛОГОВЫХ ТИПОВ")
    print("=" * 70)
    
    # Читаем стихотворения из папки chapter_4
    poems_by_group = read_poems_by_group()
    
    if not poems_by_group:
        print("\n❌ Нет стихотворений для анализа")
        print("   Убедитесь, что в папке author-corpus/chapter_4 есть файлы.")
        return
    
    # Инициализируем анализатор
    analyzer = SyllableAnalyzer()
    results = {}
    
    for group, poems in poems_by_group.items():
        if not poems:
            continue
        
        print(f"\n{'─' * 70}")
        print(f"АНАЛИЗ: {group}")
        print(f"{'─' * 70}")
        
        results[group] = aggregate_group_results(analyzer, poems)
        
        print(f"\n  Итоги:")
        print(f"    Всего слогов: {results[group]['total_syllables']}")
        print(f"    Открытые слоги: {results[group]['open_pct']:.1f}%")
        print(f"    U-критерий: {results[group]['u_value']:.2f}")
        print(f"    χ² симметрии: {results[group]['chi_square_symmetry']:.2f}")
        print(f"    Индекс асимметрии T: {results[group]['symmetry_index_T']:.3f}")
        print(f"    Сходство строк (ср): {results[group]['similarity_mean']:.2f}")
    
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