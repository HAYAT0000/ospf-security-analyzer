"""
Модуль анализа уязвимостей OSPF
"""

from typing import Dict, List, Tuple


# Критерии безопасной конфигурации
SECURITY_CRITERIA = {
    "authentication": {
        "required": True,
        "recommended_types": ["md5", "sha"],
        "message": "Отсутствует аутентификация OSPF"
    },
    "passive_interfaces": {
        "required": True,
        "message": "Не настроены passive-интерфейсы (рекомендуется passive-interface default)"
    },
    "timers": {
        "hello_recommended": 1,
        "dead_recommended": 3,
        "message": "Таймеры OSPF не оптимизированы (рекомендуется hello=1, dead=3)"
    },
    "router_id": {
        "required": True,
        "message": "Не задан router-id (может привести к нестабильности)"
    }
}


def analyze_ospf(ospf_data: Dict) -> Tuple[List[str], List[str], List[str]]:
    """
    Анализирует конфигурацию OSPF на наличие уязвимостей
    
    Args:
        ospf_data: словарь с параметрами OSPF из парсера
    
    Returns:
        кортеж (critical, warnings, recommendations)
    """
    critical = []   # критические уязвимости
    warnings = []   # предупреждения
    recommendations = []  # рекомендации по исправлению
    
    # 1. Проверка аутентификации
    if not ospf_data.get("authentication"):
        critical.append(SECURITY_CRITERIA["authentication"]["message"])
        recommendations.append("Настройте аутентификацию OSPF (например, area 0 authentication message-digest)")
    
    # 2. Проверка passive-интерфейсов
    if not ospf_data.get("passive_interfaces"):
        warnings.append(SECURITY_CRITERIA["passive_interfaces"]["message"])
        recommendations.append("Используйте passive-interface default, затем явно включайте OSPF на нужных интерфейсах")
    
    # 3. Проверка router-id
    if not ospf_data.get("router_id"):
        warnings.append(SECURITY_CRITERIA["router_id"]["message"])
        recommendations.append("Задайте router-id командой router-id X.X.X.X в секции router ospf")
    
    # 4. Проверка таймеров
    hello = ospf_data.get("timers", {}).get("hello")
    dead = ospf_data.get("timers", {}).get("dead")
    
    if hello is None or dead is None:
        warnings.append(SECURITY_CRITERIA["timers"]["message"])
        recommendations.append(f"Настройте таймеры: timers hello {SECURITY_CRITERIA['timers']['hello_recommended']} dead {SECURITY_CRITERIA['timers']['dead_recommended']}")
    elif hello != SECURITY_CRITERIA["timers"]["hello_recommended"] or dead != SECURITY_CRITERIA["timers"]["dead_recommended"]:
        warnings.append(SECURITY_CRITERIA["timers"]["message"])
        recommendations.append(f"Измените таймеры на рекомендуемые: timers hello {SECURITY_CRITERIA['timers']['hello_recommended']} dead {SECURITY_CRITERIA['timers']['dead_recommended']}")
    
    return critical, warnings, recommendations


def get_summary(critical: List[str], warnings: List[str]) -> str:
    """Возвращает краткую сводку по результатам анализа"""
    if critical:
        return f"🔴 КРИТИЧЕСКИЕ УЯЗВИМОСТИ ({len(critical)}) - требуется немедленное исправление"
    elif warnings:
        return f"🟡 ЕСТЬ ПРЕДУПРЕЖДЕНИЯ ({len(warnings)}) - рекомендуется исправить"
    else:
        return "🟢 КОНФИГУРАЦИЯ СООТВЕТСТВУЕТ КРИТЕРИЯМ БЕЗОПАСНОСТИ"


# Пример использования
if __name__ == "__main__":
    # Тестовые данные
    test_data = {
        "authentication": False,
        "passive_interfaces": [],
        "router_id": None,
        "timers": {"hello": None, "dead": None}
    }
    
    critical, warnings, recommendations = analyze_ospf(test_data)
    
    print("Критические:", critical)
    print("Предупреждения:", warnings)
    print("Рекомендации:", recommendations)
    print("Сводка:", get_summary(critical, warnings))