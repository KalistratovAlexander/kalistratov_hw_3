# ML Service — Blue/Green + Canary Deployment (HW3)

ML‑сервис на FastAPI с моделью (pickle/заглушка), упакованный в Docker и развертываемый по стратегиям Blue‑Green / Canary с помощью docker‑compose и Nginx. 

## Структура проекта

- `app/` — код сервиса:
  - `app/main.py` — FastAPI‑приложение, эндпоинты `/health` и `/predict`;
  - `app/model.py` — загрузка модели из `model.pkl` или заглушка (сумма входного вектора).
- `Dockerfile` — сборка образа `python:3.11-slim` с FastAPI‑сервисом.
- `requirements.txt` — зависимости.
- `docker-compose.blue.yml` — старое окружение (blue), модель `v1.0.0`.
- `docker-compose.green.yml` — новое окружение (green), модель `v1.1.0`.
- `docker-compose.nginx.yml` — Nginx‑балансировщик.
- `nginx.conf` — конфигурация балансировки трафика (Canary/Blue‑Green).
- `.github/workflows/deploy.yml` — CI/CD‑pipeline для сборки и публикации Docker‑образа.

## Запуск (одна версия)

1. Сборка образа:
   ```bash
   docker build -t ml-service:local .
   ```
2. Запуск blue‑версии (по умолчанию `MODEL_VERSION=v1.0.0`):
   ```bash
   docker run -p 8080:8080 -e MODEL_VERSION=v1.0.0 ml-service:local
   ```
3. Проверка эндпоинтов:
   ```bash
   curl http://localhost:8080/health
   curl -X POST http://localhost:8080/predict \
     -H "Content-Type: application/json" \
     -d '{"x": [1, 2, 3]}'
   ```

## Запуск Blue/Green + Nginx (Canary 90/10)

Две версии сервиса и Nginx‑балансировщик:

```bash
docker compose \
  -f docker-compose.blue.yml \
  -f docker-compose.green.yml \
  -f docker-compose.nginx.yml \
  up --build
```

- Blue‑версия (`MODEL_VERSION=v1.0.0`) доступна напрямую на `http://localhost:8080`.
- Green‑версия (`MODEL_VERSION=v1.1.0`) доступна напрямую на `http://localhost:8081`.
- Через Nginx доступна Canary‑раздача трафика:
  - `http://localhost:8090` — 90% запросов идут на blue, 10% — на green.

Проверка:

```bash
curl http://localhost:8080/health      # blue
curl http://localhost:8081/health      # green
curl http://localhost:8090/health      # canary через nginx

curl -X POST http://localhost:8090/predict \
  -H "Content-Type: application/json" \
  -d '{"x": [1, 2, 3]}'
```

В ответах видно:
- поле `version` — версия модели из переменной окружения `MODEL_VERSION`;
- поле `model_version` в `/predict` — версия модели, которая обслужила запрос.

## Стратегия деплоя и rollback

### Canary Deployment

В `nginx.conf` определён upstream:

```nginx
upstream ml_backend {
    server mlservice_blue:8080 weight=9;
    server mlservice_green:8080 weight=1;
}
```

- `mlservice_blue` (`MODEL_VERSION=v1.0.0`) получает 90% трафика.
- `mlservice_green` (`MODEL_VERSION=v1.1.0`) получает 10% трафика.

### Blue‑Green

Основа Blue‑Green:
- Blue — запущена версия `v1.0.0` (`docker-compose.blue.yml`);
- Green — параллельно запускается версия `v1.1.0` (`docker-compose.green.yml`);
- Nginx переключает трафик между ними.

## Мониторинг и логи

- Эндпоинт `/health` используется для проверки готовности и версии модели.
- Эндпоинт `/predict` пишет в stdout контейнера лог вида:
  `[PREDICT] version=<MODEL_VERSION>, input_len=<len>, prediction=<value>`.
- Логи доступны через:
  ```bash
  docker logs <container_id>
  ```

## Скриншоты

- `images/requests.png` — серия из 20 запросов к общему сервису через Nginx (`http://localhost:8090/predict`), демонстрирующая, что ответы приходят от разных версий модели (Canary 90/10).
- `images/docker_logs.png` — логи контейнера с сообщениями о предсказаниях, где видно `model_version`, длину входного вектора и значение предсказаний.
