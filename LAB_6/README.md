# LAB_6 - Паттерны проектирования в Web-системе

## Цель

Спроектировать современную веб-систему и покрыть требования: архитектура, взаимодействие сервисов, надежность, кэширование, асинхронность, способы получения данных и деплой.

## Выбранная система

Финтех-платформа (личные финансы и платежи).

## Архитектурная диаграмма

```mermaid
graph LR
  C[Thin Client<br/>Web/Mobile] -- "Streaming (WebSockets)" --> G[API Gateway]
  SD[Service Discovery<br/>(Consul/Eureka)]
  R[(Redis Cache)]

  subgraph CMD[CQRS - Command Side]
    P[Payments Service<br/>(Command Side)]
    WDB[(Write DB)]
    K[(Kafka)]
    W[Workers / Async Jobs<br/>(MapReduce Aggregation)]
  end

  subgraph QRY[CQRS - Query Side]
    RS[Reporting Service<br/>(Query Side)]
    RDB[(Read DB)]
  end

  G -- "Command Routing + Circuit Breaker" --> P
  G -- "Query Routing" --> RS
  G --> R

  P -- "Idempotency Check" --> R
  P --> WDB
  P --> K
  K -- "Backpressure" --> W
  W -- "Retries + Backoff" --> RDB
  RS --> RDB

  G -- "Fallback / Graceful Degradation" --> R

  G <--> |"Heartbeat / Registration"| SD
  P <--> |"Heartbeat / Registration"| SD
  RS <--> |"Heartbeat / Registration"| SD
```

## Соответствие требованиям задания

1. Архитектура: трехзвенная (`Client -> Backend -> Database`), клиент тонкий.
2. Взаимодействие сервисов: Pub/Sub через Kafka, Service Discovery, Heartbeat.
3. Работа с данными: CQRS + MapReduce в фоновых воркерах.
4. Надежность: retries/backoff, idempotency, circuit breaker, backpressure.
5. Кэширование: версионирование ключей и тегирование для инвалидации.
6. Асинхронность: отложенные задачи и очередь сообщений.
7. Получение данных: polling, long polling, streaming.
8. Деплой: rolling, blue/green, canary.

