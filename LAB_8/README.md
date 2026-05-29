# LAB_8 - Проектирование системы уровня Яндекс Такси

## Быстрая навигация

- [Цель](#цель)
- [Функциональные требования](#функциональные-требования)
- [Логическая архитектура](#логическая-архитектура)
- [Поток заказа](#поток-заказа)
- [Оценка нагрузки](#оценка-нагрузки)
- [Оценка хранения](#оценка-хранения)
- [Отказоустойчивость](#отказоустойчивость)

## Цель

Спроектировать высоконагруженную систему такси: сервисы, потоки данных, оценка нагрузки и хранения, отказоустойчивость.

## Функциональные требования

- Заказ такси.
- Выход/уход водителя с линии.
- Поиск ближайшего водителя.
- Подтверждение/отклонение поездки.
- Трекинг поездки.
- История поездок.

## Логическая архитектура

```mermaid
flowchart LR
  U[Passenger App] --> G[API Gateway]
  D[Driver App] --> G
  G --> O[Order Service]
  G --> M[Matching Service]
  G --> T[Trip Service]
  G --> H[History Service]
  G --> P[Pricing Service]

  D --> L[Location Ingest]
  L --> R[(Geo Store Redis/GeoHash)]
  M --> R

  O --> K[(Kafka)]
  M --> K
  T --> K
  K --> N[Notification Service]
  K --> A[Analytics/ETL]

  O --> DB1[(Orders DB)]
  T --> DB2[(Trips DB)]
  H --> DB3[(History Read DB)]
```

## Поток заказа

```mermaid
sequenceDiagram
  participant P as Passenger App
  participant G as API Gateway
  participant O as Order Service
  participant M as Matching Service
  participant D as Driver App
  participant T as Trip Service

  P->>G: Create order
  G->>O: POST /orders
  O->>M: Find nearest driver
  M->>D: Offer ride
  D-->>M: Accept/Reject
  M-->>O: Driver selected
  O-->>P: Order confirmed
  T->>P: Trip status stream
```

## Оценка нагрузки

- 100 млн пассажиров * 1 поездка/день = 100 млн поездок/день.
- Средний RPS создания заказов: `~1157`.
- Пиковый RPS (x5): `~5800`.
- Геообновления дают значительно больший поток событий (сотни тысяч событий/сек в пике).

## Оценка хранения

- При ~1 KB на поездку: около 100 GB/день по trip-данным.
- Порядка десятков TB в год без учета реплик.
- Геопозиции хранятся в hot-storage короткое время, затем в архив.

## Отказоустойчивость

- Критичные сервисы в multi-AZ.
- Репликация БД и автопереключение.
- Kafka как буфер пиков и decoupling между сервисами.


