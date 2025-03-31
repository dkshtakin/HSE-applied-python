## API-сервис для сокращения ссылок

### Запуск

собираем

```
docker compose build
```

запускаем

```
docker compose up
```

Сервис доступен по адресу `http://0.0.0.0:8000/`, api `http://0.0.0.0:8000/api/openapi`

### Примеры запросов

Создание короткой ссылки:
```
curl -X 'POST' \
  'http://0.0.0.0:8000/links/shorten' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://github.com/"
}'
```

Создание короткой ссылки с кастомным alias-ом и временем жизни:
```
curl -X 'POST' \
  'http://0.0.0.0:8000/links/shorten' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://github.com/",
  "alias": "abcdef",
  "expires_at": "2025-03-23 19:00"
}'
```

Поиск сокращенной ссылки по оригинальному url:
```
curl -X 'GET' \
  'http://0.0.0.0:8000/links/search?original_url=https%3A%2F%2Fgithub.com%2F' \
  -H 'accept: application/json'
```

Просмотр статистики по сокращенной ссылке:
```
curl -X 'GET' \
  'http://0.0.0.0:8000/links/abcdef/stats' \
  -H 'accept: application/json'
```

Удаление сокращенной ссылки:

```
curl -X 'DELETE' \
  'http://0.0.0.0:8000/links/abcdef' \
  -H 'accept: application/json'
```

Обновление сокращенной ссылки:
```
curl -X 'PUT' \
  'http://0.0.0.0:8000/links/abcdef' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://www.google.com/"
}'
```

### Тестирование

Unit и функциональные тесты лежат в папке `tests/`, процент прокрытия 93%, подробный отчет лежит по пути `htmlcov/index.html`.

Запуск тестов:
```
PYTHONPATH=src python -m pytest --cov src tests
```

Генерация отчета:
```
PYTHONPATH=src python -m pytest --cov src tests --cov-report=html
```
