# OSPF Security Analyzer

Утилита для автоматического анализа уязвимостей конфигураций OSPF (Cisco IOS).

## Возможности

- ✅ Проверка наличия аутентификации OSPF (plain text, MD5)
- ✅ Проверка настройки passive-интерфейсов
- ✅ Проверка наличия router-id
- ✅ Проверка оптимизации таймеров (hello/dead)
- ✅ Генерация цветных отчетов в консоль
- ✅ Экспорт отчетов в HTML

## Установка и запуск

### Требования
- Python 3.6 или выше

### Запуск
```bash
# Анализ одного файла
python main.py configs/insecure.cfg

# Анализ всех .cfg файлов в папке
python main.py configs

# С генерацией HTML-отчета
python main.py configs/insecure.cfg --html