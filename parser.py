"""
Модуль парсинга конфигурации OSPF (Cisco IOS)
"""

import re
from typing import Dict, List


def parse_ospf_config(config_text: str) -> Dict:
    """
    Парсит текстовую конфигурацию и извлекает параметры OSPF
    """
    # Инициализация результата
    result = {
        "processes": [],
        "interfaces": [],
        "passive_interfaces": [],
        "authentication": False,
        "auth_type": None,
        "timers": {"hello": None, "dead": None},
        "router_id": None
    }
    
    if not config_text:
        return result
    
    # Разбиваем на строки
    lines = config_text.split('\n')
    
    # ========== 1. Парсим секцию router ospf ==========
    in_ospf = False
    ospf_lines = []
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Начало секции OSPF
        if 'router ospf' in line_lower:
            in_ospf = True
            # Извлекаем process id
            match = re.search(r'router ospf (\d+)', line_lower)
            if match:
                result["processes"].append(match.group(1))
            continue
        
        # Конец секции OSPF (новая секция router или interface)
        if in_ospf and (line_lower.startswith('router ') or 
                        line_lower.startswith('interface ') or
                        line_lower == '!'):
            in_ospf = False
        
        # Собираем строки внутри секции OSPF
        if in_ospf and line.strip():
            ospf_lines.append(line.strip())
    
    # Анализируем строки OSPF
    for line in ospf_lines:
        line_lower = line.lower()
        
        # Router ID
        if 'router-id' in line_lower:
            match = re.search(r'router-id\s+([\d\.]+)', line_lower)
            if match:
                result["router_id"] = match.group(1)
        
        # Аутентификация
        if 'authentication' in line_lower:
            result["authentication"] = True
            if 'message-digest' in line_lower:
                result["auth_type"] = "md5"
            elif not result["auth_type"]:
                result["auth_type"] = "plain"
        
        # Таймеры
        if 'timers' in line_lower and 'hello' in line_lower:
            match = re.search(r'timers\s+hello\s+(\d+)', line_lower)
            if match:
                result["timers"]["hello"] = int(match.group(1))
        if 'timers' in line_lower and 'dead' in line_lower:
            match = re.search(r'timers\s+dead\s+(\d+)', line_lower)
            if match:
                result["timers"]["dead"] = int(match.group(1))
        
        # Passive interfaces
        if 'passive-interface' in line_lower:
            match = re.search(r'passive-interface\s+(\S+)', line_lower)
            if match:
                result["passive_interfaces"].append(match.group(1))
    
    # ========== 2. Парсим интерфейсы ==========
    in_interface = False
    current_interface = None
    
    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Начало интерфейса
        if line_lower.startswith('interface '):
            in_interface = True
            # Извлекаем имя интерфейса
            parts = line_stripped.split()
            if len(parts) >= 2:
                current_interface = parts[1]
            continue
        
        # Если внутри интерфейса и есть ip ospf
        if in_interface and 'ip ospf' in line_lower:
            # Пропускаем строки с ip ospf authentication (это не про сам OSPF процесс)
            if 'authentication' in line_lower or 'message-digest' in line_lower:
                continue
            
            # Ищем ip ospf <process-id> area <area-id>
            match = re.search(r'ip ospf (\d+)(?:\s+area\s+(\S+))?', line_lower)
            if match:
                result["interfaces"].append({
                    "name": current_interface,
                    "process_id": match.group(1),
                    "area": match.group(2) if match.group(2) else "из network"
                })
            
            # Проверяем аутентификацию на интерфейсе
            if 'authentication' in line_lower:
                result["authentication"] = True
                if 'message-digest' in line_lower:
                    result["auth_type"] = "md5"
                elif not result["auth_type"]:
                    result["auth_type"] = "plain"
        
        # Конец интерфейса
        if in_interface and (line_lower == '!' or line_lower.startswith('interface')):
            in_interface = False
            current_interface = None
    
    return result


def load_config_from_file(filepath: str) -> str:
    """Загружает конфигурацию из файла"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


# Тестирование
if __name__ == "__main__":
    test_config = """
hostname R1
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 ip ospf 1 area 0
!
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.0
 ip ospf 1 area 0
!
router ospf 1
 router-id 1.1.1.1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.255 area 0
!
"""
    result = parse_ospf_config(test_config)
    print("Результат парсинга:")
    for key, value in result.items():
        print(f"  {key}: {value}")