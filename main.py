"""
Главный модуль утилиты анализа OSPF конфигураций
"""

import sys
import os
import argparse

from parser import load_config_from_file, parse_ospf_config
from analyzer import analyze_ospf
from reporter import print_console_report, generate_html_report


def analyze_single_file(filepath: str, html: bool = False):
    """Анализирует один файл конфигурации"""
    
    try:
        config_text = load_config_from_file(filepath)
    except FileNotFoundError:
        print(f"❌ Файл не найден: {filepath}")
        return
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        return
    
    # Парсинг (всегда возвращает словарь)
    ospf_data = parse_ospf_config(config_text)
    
    # Проверка, что парсер вернул корректные данные
    if ospf_data is None:
        print(f"⚠️ Не удалось распарсить конфигурацию: {filepath}")
        ospf_data = {
            "processes": [],
            "interfaces": [],
            "passive_interfaces": [],
            "authentication": False,
            "auth_type": None,
            "timers": {"hello": None, "dead": None},
            "router_id": None
        }
    
    # Анализ
    critical, warnings, recommendations = analyze_ospf(ospf_data)
    
    # Вывод отчета в консоль
    print_console_report(filepath, ospf_data, critical, warnings, recommendations)
    
    # Генерация HTML-отчета если нужно
    if html:
        try:
            output_file = generate_html_report(filepath, ospf_data, critical, warnings, recommendations)
            print(f"📄 HTML-отчет сохранен: {output_file}")
        except Exception as e:
            print(f"⚠️ Ошибка при генерации HTML: {e}")


def analyze_directory(dirpath: str, html: bool = False):
    """Анализирует все .cfg файлы в директории"""
    
    if not os.path.isdir(dirpath):
        print(f"❌ Директория не найдена: {dirpath}")
        return
    
    cfg_files = [f for f in os.listdir(dirpath) if f.endswith('.cfg')]
    
    if not cfg_files:
        print(f"⚠️ В директории {dirpath} нет файлов .cfg")
        return
    
    print(f"\n🔍 Найдено {len(cfg_files)} конфигурационных файлов\n")
    
    for filename in cfg_files:
        filepath = os.path.join(dirpath, filename)
        analyze_single_file(filepath, html)


def main():
    """Точка входа"""
    
    parser = argparse.ArgumentParser(description='Анализ уязвимостей OSPF конфигураций')
    parser.add_argument('path', help='Путь к файлу или директории')
    parser.add_argument('--html', action='store_true', help='Генерировать HTML-отчет')
    
    args = parser.parse_args()
    
    if os.path.isfile(args.path):
        analyze_single_file(args.path, args.html)
    elif os.path.isdir(args.path):
        analyze_directory(args.path, args.html)
    else:
        print(f"❌ Путь не существует: {args.path}")
        sys.exit(1)


if __name__ == "__main__":
    main()