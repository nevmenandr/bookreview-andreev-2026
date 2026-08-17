#!/usr/bin/env python3
"""
Визуализация сравнения результатов подсчетов с данными Андреева
по всем четырем главам монографии.
Каждый график сохраняется в отдельный файл.
Обновленная версия на основе уточненных данных из JSON-файлов.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Пути
OUTPUT_DIR = Path("../visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===================================================================
# ДАННЫЕ ДЛЯ ВИЗУАЛИЗАЦИИ (из JSON-файлов результатов)
# ===================================================================

# Глава 1: Образная система (из andreev_chapter1_results.json)
CHAPTER1_DATA = {
    "early": {
        "our": {
            "poems": 9,
            "metaphors": 448,
            "concepts": 17,
            "cv": 0.8943
        },
        "andreev": {
            "poems": 9,
            "metaphors": 626,
            "concepts": 17,
            "cv": 0.16
        }
    },
    "late": {
        "our": {
            "poems": 3,
            "metaphors": 224,
            "concepts": 16,
            "cv": 0.6034
        },
        "andreev": {
            "poems": 3,
            "metaphors": 362,
            "concepts": 16,
            "cv": 0.38
        }
    },
    "early_freq": {
        "our": {
            "Растение": 0.1362, "Пространство": 0.1629, "Свет": 0.0804,
            "Существо": 0.0424, "Психическая сфера": 0.1384, "Транспорт": 0.0223,
            "Орган": 0.0513, "Вода": 0.0513, "Время": 0.1696, "Предмет": 0.0112
        },
        "andreev": {
            "Растение": 0.1500, "Пространство": 0.1100, "Свет": 0.1100,
            "Существо": 0.0800, "Психическая сфера": 0.0800, "Транспорт": 0.0700,
            "Орган": 0.0600, "Вода": 0.0500, "Время": 0.0500, "Предмет": 0.0500
        }
    },
    "late_freq": {
        "our": {
            "Существо": 0.0714, "Информация": 0.0670, "Пространство": 0.0804,
            "Социальный феномен": 0.0536, "Свет": 0.0759, "Звук": 0.0223,
            "Психическая сфера": 0.0893, "Экзистенция": 0.0179, "Растение": 0.0536,
            "Время": 0.2812
        },
        "andreev": {
            "Существо": 0.2000, "Информация": 0.1500, "Пространство": 0.1100,
            "Социальный феномен": 0.0800, "Свет": 0.0800, "Звук": 0.0700,
            "Психическая сфера": 0.0600, "Экзистенция": 0.0600, "Растение": 0.0500,
            "Время": 0.0500
        }
    }
}

# Глава 2: Частеречная структура (из author-corpus2_results.json)
CHAPTER2_DATA = {
    "Гроздь": {
        "our": {"poems": 4, "words": 767, "nominality": 0.353, "static_dynamic": 0.442},
        "andreev": {"poems": 4, "nominality": 0.30, "static_dynamic": 0.54}
    },
    "Горний путь": {
        "our": {"poems": 15, "words": 3010, "nominality": 0.392, "static_dynamic": 0.464},
        "andreev": {"poems": 15, "nominality": 0.35, "static_dynamic": 0.67}
    },
    "Возвращение Чорба": {
        "our": {"poems": 13, "words": 1651, "nominality": 0.385, "static_dynamic": 0.427},
        "andreev": {"poems": 13, "nominality": 0.32, "static_dynamic": 0.46}
    },
    "Стихотворения 1929-1951": {
        "our": {"poems": 5, "words": 1653, "nominality": 0.396, "static_dynamic": 0.389},
        "andreev": {"poems": 5, "nominality": 0.29, "static_dynamic": 0.46}
    }
}

# Глава 3: Атрибутивная схема (из results_chapter3.json и final_report_chapter3.txt)
CHAPTER3_DATA = {
    "Гроздь": {
        "our": {
            "texts": 38,
            "density": 12.70,
            "h_index": 13,
            "concentration": 0.9165,
            "buzman": 0.500,
            "inversion": 17.77,
            "pfa": 18.94
        },
        "andreev": {
            "texts": 38,
            "density": 25.00,
            "h_index": 23.16,
            "concentration": 0.75,
            "buzman": 0.76,
            "inversion": 28.93,
            "pfa": 15.36
        }
    },
    "Возвращение Чорба": {
        "our": {
            "texts": 24,
            "density": 10.81,
            "h_index": 11,
            "concentration": 0.8024,
            "buzman": 0.500,
            "inversion": 18.10,
            "pfa": 8.27
        },
        "andreev": {
            "texts": 24,
            "density": 24.00,
            "h_index": 18.20,
            "concentration": 0.84,
            "buzman": 0.76,
            "inversion": 22.64,
            "pfa": 8.06
        }
    }
}

# Глава 4: Соотношение слоговых типов (из author-corpus4_results.json и result_chapter4.txt)
CHAPTER4_DATA = {
    "Гроздь_4-ст": {
        "our": {
            "open_pct": 30.9,
            "u_value": -15.76,
            "chi_square": 593.48,
            "symmetry_T": 1.452,
            "similarity": 1.67,
            "texts": 12
        },
        "andreev": {
            "open_pct": 59.0,
            "u_value": 7.49,
            "chi_square": 943.10,
            "symmetry_T": 0.723,
            "similarity": 5.30,
            "texts": 12
        }
    },
    "Гроздь_5-ст": {
        "our": {
            "open_pct": 31.6,
            "u_value": -10.06,
            "chi_square": 272.68,
            "symmetry_T": 1.434,
            "similarity": 0.00,
            "texts": 5
        },
        "andreev": {
            "open_pct": 54.0,
            "u_value": 2.33,
            "chi_square": 523.62,
            "symmetry_T": 0.622,
            "similarity": 6.70,
            "texts": 5
        }
    },
    "Возвращение Чорба_4-ст": {
        "our": {
            "open_pct": 34.4,
            "u_value": -12.78,
            "chi_square": 595.11,
            "symmetry_T": 1.446,
            "similarity": 0.00,
            "texts": 9
        },
        "andreev": {
            "open_pct": 62.0,
            "u_value": 11.23,
            "chi_square": 1310.73,
            "symmetry_T": 0.614,
            "similarity": 5.40,
            "texts": 9
        }
    },
    "Возвращение Чорба_5-ст": {
        "our": {
            "open_pct": 33.7,
            "u_value": -11.51,
            "chi_square": 400.62,
            "symmetry_T": 1.431,
            "similarity": 0.00,
            "texts": 7
        },
        "andreev": {
            "open_pct": 61.0,
            "u_value": 9.72,
            "chi_square": 1140.94,
            "symmetry_T": 0.616,
            "similarity": 6.50,
            "texts": 7
        }
    }
}


# ===================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ===================================================================

def create_bar_chart(categories, our_values, andreev_values, title, ylabel, filename,
                     our_label="Наши данные", andreev_label="Данные Андреева",
                     add_values=True, ylim=None, rotate_labels=45):
    """Создает столбчатую диаграмму для сравнения двух наборов данных."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, our_values, width, label=our_label, color='#2ecc71', alpha=0.8, edgecolor='#27ae60')
    bars2 = ax.bar(x + width/2, andreev_values, width, label=andreev_label, color='#e74c3c', alpha=0.8, edgecolor='#c0392b')
    
    ax.set_xlabel('Категория', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=rotate_labels, ha='right')
    ax.legend(loc='upper right', fontsize=11)
    
    if ylim:
        ax.set_ylim(ylim)
    
    if add_values:
        all_values = our_values + andreev_values
        max_val = max(all_values) if all_values else 1
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + (max_val * 0.02),
                            f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ {filename}")


def create_accuracy_chart(chapter_results):
    """Создает диаграмму точности воспроизведения по главам."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    chapters = list(chapter_results.keys())
    accuracies = list(chapter_results.values())
    
    colors = []
    for acc in accuracies:
        if acc >= 80:
            colors.append('#2ecc71')
        elif acc >= 60:
            colors.append('#f1c40f')
        elif acc >= 40:
            colors.append('#e67e22')
        else:
            colors.append('#e74c3c')
    
    bars = ax.bar(chapters, accuracies, color=colors, alpha=0.8, edgecolor='#2c3e50', linewidth=1.5)
    
    ax.set_xlabel('Глава', fontsize=12)
    ax.set_ylabel('Точность воспроизведения (%)', fontsize=12)
    ax.set_title('Сравнение точности воспроизведения результатов по главам', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.axhline(y=80, color='#2ecc71', linestyle='--', alpha=0.5, linewidth=2, label='Отлично (80%)')
    ax.axhline(y=60, color='#f1c40f', linestyle='--', alpha=0.5, linewidth=2, label='Хорошо (60%)')
    ax.axhline(y=40, color='#e67e22', linestyle='--', alpha=0.5, linewidth=2, label='Удовлетворительно (40%)')
    ax.legend(loc='upper left', fontsize=10)
    
    for bar, acc in zip(bars, accuracies):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                f'{acc:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '00_accuracy_overview.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 00_accuracy_overview.png")


# ===================================================================
# ВИЗУАЛИЗАЦИЯ ДЛЯ ГЛАВЫ 1
# ===================================================================

def visualize_chapter1():
    """Визуализация результатов для Главы 1."""
    print("\n📊 Глава 1: Образная система")
    
    categories = ['Ранний период', 'Зрелый период']
    
    # 1. Количество стихотворений
    our_poems = [CHAPTER1_DATA['early']['our']['poems'], CHAPTER1_DATA['late']['our']['poems']]
    andreev_poems = [CHAPTER1_DATA['early']['andreev']['poems'], CHAPTER1_DATA['late']['andreev']['poems']]
    
    create_bar_chart(
        categories, our_poems, andreev_poems,
        'Глава 1: Количество стихотворений по периодам',
        'Количество стихотворений',
        '01_chapter1_poems_count.png'
    )
    
    # 2. Коэффициент вариации (CV)
    our_cv = [CHAPTER1_DATA['early']['our']['cv'], CHAPTER1_DATA['late']['our']['cv']]
    andreev_cv = [CHAPTER1_DATA['early']['andreev']['cv'], CHAPTER1_DATA['late']['andreev']['cv']]
    
    create_bar_chart(
        categories, our_cv, andreev_cv,
        'Глава 1: Коэффициент вариации (CV) по периодам\n(Чем ниже CV, тем стабильнее стиль)',
        'Коэффициент вариации (CV)',
        '02_chapter1_cv.png',
        ylim=(0, 1.0)
    )
    
    # 3. Частоты концептов (ранний период)
    early_concepts = list(CHAPTER1_DATA['early_freq']['our'].keys())
    our_early = [CHAPTER1_DATA['early_freq']['our'][c] for c in early_concepts]
    andreev_early = [CHAPTER1_DATA['early_freq']['andreev'][c] for c in early_concepts]
    
    create_bar_chart(
        early_concepts, our_early, andreev_early,
        'Глава 1: Частоты концептов-целей (ранний период)',
        'Частота',
        '03_chapter1_early_concepts.png'
    )
    
    # 4. Частоты концептов (зрелый период)
    late_concepts = list(CHAPTER1_DATA['late_freq']['our'].keys())
    our_late = [CHAPTER1_DATA['late_freq']['our'][c] for c in late_concepts]
    andreev_late = [CHAPTER1_DATA['late_freq']['andreev'][c] for c in late_concepts]
    
    create_bar_chart(
        late_concepts, our_late, andreev_late,
        'Глава 1: Частоты концептов-целей (зрелый период)',
        'Частота',
        '04_chapter1_late_concepts.png'
    )


# ===================================================================
# ВИЗУАЛИЗАЦИЯ ДЛЯ ГЛАВЫ 2
# ===================================================================

def visualize_chapter2():
    """Визуализация результатов для Главы 2."""
    print("\n📊 Глава 2: Частеречная структура")
    
    collections = list(CHAPTER2_DATA.keys())
    
    # 1. Количество стихотворений
    our_poems = [CHAPTER2_DATA[c]['our']['poems'] for c in collections]
    andreev_poems = [CHAPTER2_DATA[c]['andreev']['poems'] for c in collections]
    
    create_bar_chart(
        collections, our_poems, andreev_poems,
        'Глава 2: Количество стихотворений по сборникам',
        'Количество стихотворений',
        '05_chapter2_poems_count.png'
    )
    
    # 2. Номинальность
    our_nom = [CHAPTER2_DATA[c]['our']['nominality'] for c in collections]
    andreev_nom = [CHAPTER2_DATA[c]['andreev']['nominality'] for c in collections]
    
    create_bar_chart(
        collections, our_nom, andreev_nom,
        'Глава 2: Номинальность (ГЛ/СЩ) по сборникам\n(Чем ниже значение, тем выше номинальность)',
        'Коэффициент номинальности',
        '06_chapter2_nominality.png'
    )
    
    # 3. Статика/динамика
    our_sd = [CHAPTER2_DATA[c]['our']['static_dynamic'] for c in collections]
    andreev_sd = [CHAPTER2_DATA[c]['andreev']['static_dynamic'] for c in collections]
    
    create_bar_chart(
        collections, our_sd, andreev_sd,
        'Глава 2: Статика/динамика (ПЛ/ГЛ) по сборникам\n(Чем выше значение, тем статичнее описание)',
        'Коэффициент статики/динамики',
        '07_chapter2_static_dynamic.png'
    )


# ===================================================================
# ВИЗУАЛИЗАЦИЯ ДЛЯ ГЛАВЫ 3
# ===================================================================

def visualize_chapter3():
    """Визуализация результатов для Главы 3."""
    print("\n📊 Глава 3: Атрибутивная схема")
    
    collections = list(CHAPTER3_DATA.keys())
    
    # 1. Количество текстов
    our_texts = [CHAPTER3_DATA[c]['our']['texts'] for c in collections]
    andreev_texts = [CHAPTER3_DATA[c]['andreev']['texts'] for c in collections]
    
    create_bar_chart(
        collections, our_texts, andreev_texts,
        'Глава 3: Количество текстов по сборникам',
        'Количество текстов',
        '08_chapter3_texts_count.png'
    )
    
    # 2. Плотность атрибутов
    our_density = [CHAPTER3_DATA[c]['our']['density'] for c in collections]
    andreev_density = [CHAPTER3_DATA[c]['andreev']['density'] for c in collections]
    
    create_bar_chart(
        collections, our_density, andreev_density,
        'Глава 3: Средняя плотность атрибутов (на 100 слов)\n(Чем выше, тем больше определений)',
        'Плотность атрибутов (на 100 слов)',
        '09_chapter3_density.png'
    )
    
    # 3. h-индекс
    our_h = [CHAPTER3_DATA[c]['our']['h_index'] for c in collections]
    andreev_h = [CHAPTER3_DATA[c]['andreev']['h_index'] for c in collections]
    
    create_bar_chart(
        collections, our_h, andreev_h,
        'Глава 3: h-индекс (точка Хирша)\n(Отражает концентрацию атрибутов в текстах-лидерах)',
        'h-индекс',
        '10_chapter3_h_index.png'
    )
    
    # 4. Коэффициент Бузмана
    our_b = [CHAPTER3_DATA[c]['our']['buzman'] for c in collections]
    andreev_b = [CHAPTER3_DATA[c]['andreev']['buzman'] for c in collections]
    
    create_bar_chart(
        collections, our_b, andreev_b,
        'Глава 3: Коэффициент Бузмана\n(Чем выше, тем сильнее преобладание адъективных атрибутов)',
        'Коэффициент Бузмана',
        '11_chapter3_buzman.png'
    )
    
    # 5. Инверсия
    our_inv = [CHAPTER3_DATA[c]['our']['inversion'] for c in collections]
    andreev_inv = [CHAPTER3_DATA[c]['andreev']['inversion'] for c in collections]
    
    create_bar_chart(
        collections, our_inv, andreev_inv,
        'Глава 3: Процент инвертированных атрибутов\n(Отражает использование нестандартного порядка слов)',
        'Инверсия (%)',
        '12_chapter3_inversion.png'
    )
    
    # 6. ПФА
    our_pfa = [CHAPTER3_DATA[c]['our']['pfa'] for c in collections]
    andreev_pfa = [CHAPTER3_DATA[c]['andreev']['pfa'] for c in collections]
    
    create_bar_chart(
        collections, our_pfa, andreev_pfa,
        'Глава 3: Полифункциональные атрибуты (ПФА) в %\n(Атрибуты, которые сами имеют определения)',
        'ПФА (%)',
        '13_chapter3_pfa.png'
    )
    
    # 7. Индекс концентрации
    our_conc = [CHAPTER3_DATA[c]['our']['concentration'] for c in collections]
    andreev_conc = [CHAPTER3_DATA[c]['andreev']['concentration'] for c in collections]
    
    create_bar_chart(
        collections, our_conc, andreev_conc,
        'Глава 3: Индекс концентрации ядра\n(Отражает концентрацию атрибутов в частотном ядре)',
        'Индекс концентрации',
        '14_chapter3_concentration.png'
    )


# ===================================================================
# ВИЗУАЛИЗАЦИЯ ДЛЯ ГЛАВЫ 4
# ===================================================================

def visualize_chapter4():
    """Визуализация результатов для Главы 4."""
    print("\n📊 Глава 4: Соотношение слоговых типов")
    
    collections = ['Гроздь_4-ст', 'Гроздь_5-ст', 'Возвращение Чорба_4-ст', 'Возвращение Чорба_5-ст']
    labels = ['Гроздь\n4-ст', 'Гроздь\n5-ст', 'ВЧ\n4-ст', 'ВЧ\n5-ст']
    
    # 1. Количество текстов
    our_texts = [CHAPTER4_DATA[c]['our']['texts'] for c in collections]
    andreev_texts = [CHAPTER4_DATA[c]['andreev']['texts'] for c in collections]
    
    create_bar_chart(
        labels, our_texts, andreev_texts,
        'Глава 4: Количество текстов по группам\n(ВСЕ тексты на месте!)',
        'Количество текстов',
        '15_chapter4_texts_count.png'
    )
    
    # 2. Открытые слоги (%)
    our_open = [CHAPTER4_DATA[c]['our']['open_pct'] for c in collections]
    andreev_open = [CHAPTER4_DATA[c]['andreev']['open_pct'] for c in collections]
    
    create_bar_chart(
        labels, our_open, andreev_open,
        'Глава 4: Открытые слоги (%)\n(Чем выше, тем больше открытых слогов)',
        'Открытые слоги (%)',
        '16_chapter4_open_syllables.png'
    )
    
    # 3. Индекс асимметрии T
    our_T = [CHAPTER4_DATA[c]['our']['symmetry_T'] for c in collections]
    andreev_T = [CHAPTER4_DATA[c]['andreev']['symmetry_T'] for c in collections]
    
    create_bar_chart(
        labels, our_T, andreev_T,
        'Глава 4: Индекс асимметрии слогов (T)\n(Чем выше, тем сильнее асимметрия)',
        'Индекс асимметрии T',
        '17_chapter4_symmetry_T.png'
    )
    
    # 4. U-критерий
    our_u = [CHAPTER4_DATA[c]['our']['u_value'] for c in collections]
    andreev_u = [CHAPTER4_DATA[c]['andreev']['u_value'] for c in collections]
    
    create_bar_chart(
        labels, our_u, andreev_u,
        'Глава 4: U-критерий (открытые/закрытые слоги)\n(Положительное значение = преобладание открытых слогов)',
        'U-критерий',
        '18_chapter4_u_value.png'
    )
    
    # 5. χ² симметрии (логарифмическая шкала)
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(labels))
    width = 0.35
    
    our_chi = [CHAPTER4_DATA[c]['our']['chi_square'] for c in collections]
    andreev_chi = [CHAPTER4_DATA[c]['andreev']['chi_square'] for c in collections]
    
    bars1 = ax.bar(x - width/2, our_chi, width, label='Наши данные', color='#2ecc71', alpha=0.8, edgecolor='#27ae60')
    bars2 = ax.bar(x + width/2, andreev_chi, width, label='Данные Андреева', color='#e74c3c', alpha=0.8, edgecolor='#c0392b')
    
    ax.set_xlabel('Группа', fontsize=12)
    ax.set_ylabel('χ² симметрии (логарифмическая шкала)', fontsize=12)
    ax.set_title('Глава 4: χ² симметрии слогов\n(Чем выше, тем сильнее асимметрия)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_yscale('log')
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '19_chapter4_chi_square.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 19_chapter4_chi_square.png")
    
    # 6. Сходство строк
    our_sim = [CHAPTER4_DATA[c]['our']['similarity'] for c in collections]
    andreev_sim = [CHAPTER4_DATA[c]['andreev']['similarity'] for c in collections]
    
    create_bar_chart(
        labels, our_sim, andreev_sim,
        'Глава 4: Сходство соседних строк (среднее)\n(Чем выше, тем больше сходство слогового состава строк)',
        'Индекс сходства',
        '20_chapter4_similarity.png'
    )


# ===================================================================
# ОБЩАЯ ТОЧНОСТЬ И ПОКРЫТИЕ
# ===================================================================

def create_accuracy_overview():
    """Создает обзор точности по всем главам."""
    print("\n📊 Общая точность воспроизведения")
    
    # Оценка точности на основе данных из отчетов
    # Глава 1: avg_diff = 0.0582 -> ~70% точности
    # Глава 2: avg_diff = 19.1914 -> ~5% точности
    # Глава 3: 0 из 10 проверок пройдено -> 0%
    # Глава 4: avg_diff = 24.5412 -> ~5% точности
    
    chapter_accuracy = {
        'Глава 1': 70.0,
        'Глава 2': 5.0,
        'Глава 3': 0.0,
        'Глава 4': 5.0
    }
    
    create_accuracy_chart(chapter_accuracy)
    
    # Покрытие корпуса по главам
    fig, ax = plt.subplots(figsize=(10, 6))
    
    chapters = ['Глава 1', 'Глава 2', 'Глава 3', 'Глава 4']
    # Все тексты теперь на месте!
    our_texts = [12, 37, 62, 33]
    andreev_texts = [12, 37, 62, 33]
    coverage = [(o/a*100) for o, a in zip(our_texts, andreev_texts)]
    
    bars = ax.bar(chapters, coverage, color=['#2ecc71', '#2ecc71', '#2ecc71', '#2ecc71'], 
                  alpha=0.8, edgecolor='#27ae60', linewidth=1.5)
    
    ax.set_xlabel('Глава', fontsize=12)
    ax.set_ylabel('Покрытие корпуса (%)', fontsize=12)
    ax.set_title('Покрытие корпуса Андреева нашими текстами по главам\n(100% во всех главах!)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 120)
    ax.axhline(y=100, color='#2ecc71', linestyle='--', alpha=0.5, linewidth=2, label='Полное покрытие (100%)')
    ax.legend(loc='upper right', fontsize=10)
    
    for bar, cov in zip(bars, coverage):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                f'{cov:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '21_coverage_by_chapter.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 21_coverage_by_chapter.png")


# ===================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ===================================================================

def main():
    print("=" * 70)
    print("ВИЗУАЛИЗАЦИЯ СРАВНЕНИЯ РЕЗУЛЬТАТОВ С ДАННЫМИ АНДРЕЕВА")
    print("=" * 70)
    print(f"\n📁 Сохранение в: {OUTPUT_DIR}")
    
    # Создаем все визуализации
    visualize_chapter1()
    visualize_chapter2()
    visualize_chapter3()
    visualize_chapter4()
    create_accuracy_overview()
    
    print("\n" + "=" * 70)
    print("ГОТОВО!")
    print("=" * 70)
    print(f"\nВсе графики сохранены в: {OUTPUT_DIR}")
    print("\nСписок созданных файлов:")
    for file in sorted(OUTPUT_DIR.glob("*.png")):
        print(f"  📊 {file.name}")


if __name__ == "__main__":
    main()