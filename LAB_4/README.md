# LAB_4 - Проектирование БД: partitioning, sharding, replication

## Цель

Спроектировать БД для системы учета доходов/расходов и обосновать:
- структуру таблиц;
- стратегию партиционирования;
- стратегию шардирования;
- репликацию и поведение при сбоях.

## Архитектурная диаграмма

```mermaid
flowchart TB
  API[API Gateway] --> SVC[Wallet/Transactions Services]
  SVC --> SH{Shard Router by user_id}

  SH --> P1[(Shard-1 Primary\ntransactions: p_2026_01, p_2026_02, ...)]
  SH --> P2[(Shard-2 Primary\ntransactions: p_2026_01, p_2026_02, ...)]
  SH --> P3[(Shard-3 Primary\ntransactions: p_2026_01, p_2026_02, ...)]
  SH --> P4[(Shard-4 Primary\ntransactions: p_2026_01, p_2026_02, ...)]

  P1 --> R11[(Replica 1)]
  P1 --> R12[(Replica 2)]
  P2 --> R21[(Replica 1)]
  P2 --> R22[(Replica 2)]
  P3 --> R31[(Replica 1)]
  P3 --> R32[(Replica 2)]
  P4 --> R41[(Replica 1)]
  P4 --> R42[(Replica 2)]
```

## ER-диаграмма

```mermaid
erDiagram
  USERS ||--o{ ACCOUNTS : owns
  USERS ||--o{ TRANSACTIONS : makes
  USERS ||--o{ DAILY_AGGREGATES : has
  ACCOUNTS ||--o{ TRANSACTIONS : contains
  CATEGORIES ||--o{ TRANSACTIONS : classifies
```

## Ключевые решения

1. Таблица с максимальным ростом: `transactions`.
2. Партиционирование: `RANGE` по времени (`event_time`) помесячно.
3. Шардирование: `hash(user_id) mod N`, старт `N=4`.
4. Репликация: `1 primary + 2 replicas` на каждый шард.

