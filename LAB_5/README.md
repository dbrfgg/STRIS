# LAB_5 - Kafka: топик, партиции, producer/consumer group

## Цель

Показать работу Kafka с партиционированием по ключу (`user_id`) и чтением через `consumer group`.

## Что реализовано

- Подняты `Zookeeper` и `Kafka` в Docker.
- Создан топик `transactions` с 3 партициями.
- Producer отправляет JSON-сообщения формата:
  - `user_id`
  - `amount`
  - `type` (`incoming`/`outgoing`)
- В качестве key используется `user_id`, поэтому одинаковый пользователь стабильно идет в одну партицию.
- Consumer читает сообщения в группе `transaction-group`.

## Файлы

- `docker-compose.yml`
- `app/create_topic.py`
- `app/producer.py`
- `app/consumer.py`

## Запуск

```powershell
cd C:\Users\Vika\Documents\STRIS\LAB_5
docker compose up --build -d
docker compose exec app python create_topic.py
```

Запустить consumer:
```powershell
docker compose exec app python consumer.py
```

В другом окне отправить сообщения:
```powershell
docker compose exec app python producer.py
```

## Проверка

- В выводе producer видно, в какую `partition` ушло сообщение.
- Сообщения с одинаковым `user_id` должны попадать в одну и ту же партицию.
- Сообщения с разными `user_id` распределяются между разными партициями.

## Остановка

```powershell
docker compose down
```
