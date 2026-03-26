"""
Модуль формирования отчета
"""

import os
from datetime import datetime
from typing import Dict, List, Tuple


def print_console_report(
    filename: str, 
    ospf_data: Dict, 
    critical: List[str], 
    warnings: List[str], 
    recommendations: List[str]
):
    """Выводит отчет в консоль с цветовой подсветкой"""
    
    # Попробуем импортировать colorama для цветов, если нет — обойдемся
    try:
        from colorama import init, Fore, Style
        init()
        colors_available = True
    except ImportError:
        colors_available = False
    
    def colored(text, color):
        if colors_available:
            return f"{color}{text}{Style.RESET_ALL}"
        return text
    
    print("\n" + "=" * 60)
    print(f"📁 Файл: {filename}")
    print(f"📅 Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Вывод параметров конфигурации
    print("\n📋 ПАРАМЕТРЫ КОНФИГУРАЦИИ:")
    print(f"   Router ID: {ospf_data.get('router_id') or 'не задан'}")
    print(f"   Аутентификация: {'да' if ospf_data.get('authentication') else 'нет'}")
    if ospf_data.get('auth_type'):
        print(f"   Тип аутентификации: {ospf_data['auth_type']}")
    print(f"   Passive-интерфейсы: {ospf_data.get('passive_interfaces') or 'нет'}")
    hello = ospf_data.get('timers', {}).get('hello')
    dead = ospf_data.get('timers', {}).get('dead')
    print(f"   Таймеры: hello={hello or 'по умолчанию'}, dead={dead or 'по умолчанию'}")
    print(f"   Интерфейсов с OSPF: {len(ospf_data.get('interfaces', []))}")
    
    # Критические уязвимости
    if critical:
        print("\n🔴 КРИТИЧЕСКИЕ УЯЗВИМОСТИ:")
        for item in critical:
            print(f"   ❌ {item}")
    
    # Предупреждения
    if warnings:
        print("\n🟡 ПРЕДУПРЕЖДЕНИЯ:")
        for item in warnings:
            print(f"   ⚠️ {item}")
    
    # Рекомендации
    if recommendations:
        print("\n💡 РЕКОМЕНДАЦИИ ПО УСТРАНЕНИЮ:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    # Итоговая оценка
    print("\n" + "=" * 60)
    if critical:
        print(colored(f"🔴 ОЦЕНКА: КОНФИГУРАЦИЯ НЕБЕЗОПАСНА", Fore.RED))
    elif warnings:
        print(colored(f"🟡 ОЦЕНКА: ТРЕБУЕТ ДОРАБОТКИ", Fore.YELLOW))
    else:
        print(colored(f"🟢 ОЦЕНКА: КОНФИГУРАЦИЯ БЕЗОПАСНА", Fore.GREEN))
    print("=" * 60 + "\n")


def generate_html_report(
    filename: str,
    ospf_data: Dict,
    critical: List[str],
    warnings: List[str],
    recommendations: List[str],
    output_dir: str = "reports"
) -> str:
    """Генерирует HTML-отчет"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(
        output_dir, 
        f"report_{os.path.basename(filename).replace('.cfg', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )
    
    # Статус и цвет
    if critical:
        status = "НЕБЕЗОПАСНА"
        status_color = "#dc3545"
    elif warnings:
        status = "ТРЕБУЕТ ДОРАБОТКИ"
        status_color = "#ffc107"
    else:
        status = "БЕЗОПАСНА"
        status_color = "#28a745"
    
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Анализ OSPF конфигурации</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .status {{
            background-color: {status_color};
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            margin: 20px 0;
        }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
        }}
        .section h3 {{
            margin-top: 0;
            color: #007bff;
        }}
        .critical {{
            color: #dc3545;
        }}
        .warning {{
            color: #ffc107;
        }}
        .recommendation {{
            color: #28a745;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        td, th {{
            padding: 8px;
            border: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Анализ OSPF конфигурации</h1>
        <p><strong>Файл:</strong> {filename}</p>
        <p><strong>Дата анализа:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="status">
            🏷️ ОЦЕНКА БЕЗОПАСНОСТИ: {status}
        </div>
        
        <div class="section">
            <h3>📋 Параметры конфигурации</h3>
            <table>
                <tr><th>Параметр</th><th>Значение</th></tr>
                <tr><td>Router ID</td><td>{ospf_data.get('router_id') or 'не задан'}</td></tr>
                <tr><td>Аутентификация</td><td>{'✅ да' if ospf_data.get('authentication') else '❌ нет'}</td></tr>
                <tr><td>Тип аутентификации</td><td>{ospf_data.get('auth_type') or '—'}</td></tr>
                <tr><td>Passive-интерфейсы</td><td>{ospf_data.get('passive_interfaces') or 'нет'}</td></tr>
                <tr><td>Таймеры hello/dead</td><td>{ospf_data.get('timers', {}).get('hello') or 'по умолч.'} / {ospf_data.get('timers', {}).get('dead') or 'по умолч.'}</td></tr>
                <tr><td>Интерфейсов с OSPF</td><td>{len(ospf_data.get('interfaces', []))}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h3>🔴 Критические уязвимости</h3>
            {'<ul>' + ''.join(f'<li class="critical">❌ {item}</li>' for item in critical) + '</ul>' if critical else '<p>✅ Критических уязвимостей не обнаружено</p>'}
        </div>
        
        <div class="section">
            <h3>🟡 Предупреждения</h3>
            {'<ul>' + ''.join(f'<li class="warning">⚠️ {item}</li>' for item in warnings) + '</ul>' if warnings else '<p>✅ Предупреждений нет</p>'}
        </div>
        
        <div class="section">
            <h3>💡 Рекомендации по устранению</h3>
            {'<ul>' + ''.join(f'<li class="recommendation">🔧 {item}</li>' for item in recommendations) + '</ul>' if recommendations else '<p>✅ Конфигурация соответствует рекомендациям</p>'}
        </div>
        
        <div class="footer">
            <p>Сгенерировано утилитой анализа OSPF конфигураций</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file