# Автоматизация обработки support-тикетов — PoC

Локальный Proof-of-Concept принимает англоязычный тикет, классифицирует категорию и риск, ищет похожие исторические обращения, получает структурированную рекомендацию LLM и применяет независимую детерминированную Decision Policy. Результат — `AUTO_REPLY`, `ASK_CLARIFICATION` или безопасный `ESCALATE` с тикетом для оператора и трассировкой решения.

## Зачем это бизнесу

Система сокращает стоимость и время обработки простых обращений, сохраняя участие оператора в рискованных и неуверенных случаях. Автоматический первый ответ помогает соблюдать SLA 15 минут при росте потока. Retrieval и трассировка делают ответы проверяемыми, а эскалация ограничивает риск ухудшения CSAT и reopen rate. Перед пилотом пороги и список разрешённых сценариев должны быть подтверждены на бизнес-метриках.

## Быстрый запуск

Нужен CSV `dataset-tickets-multi-lang-4-20k.csv` в корне проекта. Для режима llama.cpp положите `Qwen3.5-4B-Q8_0.gguf` в `models/`; веса не скачиваются и не хранятся в Git.

Самый быстрый запуск без модели:

```bash
LLM_MODE=mock docker compose up -d --build app
curl http://127.0.0.1:8003/health
docker compose exec app python -m app.cli demo-happy
docker compose exec app python -m app.cli demo-risky
```

Запуск Qwen3.5-4B-Q8 на GPU:

```bash
LLM_MODE=llama_cpp \
LLAMA_BASE_URL=http://llama-gpu:8080 \
docker compose --profile gpu up -d --build --force-recreate app llama-gpu

curl http://127.0.0.1:8003/health
docker compose exec app python -m app.cli interactive
```

Для GPU нужен NVIDIA Container Toolkit. Приложение доступно на `8003`, llama.cpp — на `8004`. Проверить фактический inference:

```bash
docker compose logs -f llama-gpu
```

CPU-режим:

```bash
LLM_MODE=llama_cpp \
LLAMA_BASE_URL=http://llama-cpu:8080 \
docker compose --profile cpu up -d --build --force-recreate app llama-cpu
```

CPU- и GPU-профили одновременно не запускаются: оба используют порт `8004`.

## API и проверки

```bash
curl -X POST http://127.0.0.1:8003/tickets/process \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket_id": "demo-001",
    "subject": "Unauthorized payment from stolen account",
    "message": "I did not approve this payment. Please secure my account.",
    "history": []
  }'
```

Локальные тесты не требуют llama.cpp и намеренно используют mock/stub:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m app.cli smoke
```

## Демонстрируемые сценарии

- Happy path: уверенный low-risk запрос с похожими случаями получает `AUTO_REPLY`.
- Risky path: `unauthorized payment` повышается rule override до high risk и получает `ESCALATE`.
- Fallback: timeout, HTTP error или невалидный JSON LLM приводит к `ESCALATE`.
- Решение LLM рекомендательное; окончательное действие всегда выбирает код policy.

## Что реализовано

- sklearn `TF-IDF + LogisticRegression` для категории и proxy-риска;
- английский subset CSV, сохранение моделей через joblib и повторное использование артефактов;
- TF-IDF retrieval top-20 → не более top-5 примеров;
- Pydantic-контракты, mock LLM и HTTP `LlamaCppAdapter`;
- FastAPI `/health`, `/tickets/process`, CLI, structured trace и pytest;
- Docker Compose: mock, llama.cpp CPU и CUDA GPU.
