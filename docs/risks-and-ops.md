# Риски и эксплуатация

## Highload и надёжность

- **Синхронный путь:** validation, classification, risk rules и policy остаются быстрыми; retrieval и LLM имеют жёсткие timeout и отдельные latency budgets.
- **Пики:** входящие тикеты принимаются независимо от медленных интеграций, а генерация и helpdesk-операции буферизуются очередью с backpressure, retry и dead-letter queue.
- **Недоступность LLM:** auto-reply запрещается, запрос получает безопасный `ESCALATE`; classification/routing и приём тикетов продолжают работать.
- **Разделение путей:** high-risk и low-confidence сразу уходят по быстрому пути к оператору; медленная генерация используется только когда она может изменить безопасный пользовательский ответ.

## Privacy, safety и risk

- **PII:** email, телефон, платёжные и идентификационные данные маскируются; секреты, полные реквизиты, медицинские и иные специальные категории данных нельзя отправлять во внешний LLM API.
- **Human-in-the-loop:** fraud, stolen account, unauthorized payment, data leak, security breach, legal threat и массовые outages нельзя закрывать автоматически; medium-risk по умолчанию также требует оператора.
- **Prompt injection:** исторические тикеты и пользовательский текст считаются недоверенными данными, отделяются от system instructions; LLM не получает права вызывать действия и не может изменить Decision Policy.
- **Аудит:** сохраняются версии моделей/policy/prompt, структурированные признаки, confidence, retrieval IDs, итоговое действие и override/fallback; скрытые рассуждения и необработанный PII не логируются.
