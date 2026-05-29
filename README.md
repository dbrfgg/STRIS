# STRIS - Лабораторные работы

Этот репозиторий содержит выполненные лабораторные по STRIS. Формат во всех папках одинаковый: цель, реализация, проверка и тезисы для сдачи.

## Список лабораторных

1. [LAB_0](./LAB_0/README.md) - Проектирование REST API (OpenAPI)
2. [LAB_1](./LAB_1/README.md) - Балансировка, reverse proxy, кэширование
3. [LAB_2](./LAB_2/README.md) - Репликация `master + 2 replicas`
4. [LAB_3](./LAB_3/README.md) - Репликация и восстановление после сбоя
5. [LAB_4](./LAB_4/README.md) - Проектирование БД: partitioning/sharding/replication
6. [LAB_5](./LAB_5/README.md) - Kafka: партиции, ключи, consumer group
7. [LAB_6](./LAB_6/README.md) - Архитектурные паттерны веб-системы
8. [LAB_7](./LAB_7/README.md) - Transactional Outbox
9. [LAB_8](./LAB_8/README.md) - Проектирование системы уровня Яндекс Такси

## Лабы с запуском в Docker

- `LAB_1`, `LAB_2`, `LAB_3`, `LAB_5`, `LAB_7`

## Порты

- `LAB_1`: `8080`, `8081`, `8082`
- `LAB_2`: `8102`, `8103`, `8104`
- `LAB_3`: `8202`, `8203`, `8204`
- `LAB_5`: `8311`, `8312`
- `LAB_7`: `8400`, `8401`

## Быстрый шаблон запуска

```powershell
cd .\LAB_5
docker compose up --build -d
docker compose ps
```

Остановка:

```powershell
docker compose down
```

