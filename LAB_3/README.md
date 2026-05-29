# LAB_3 - Распределенное хранение и восстановление реплик

## Быстрая навигация

- [Цель](#цель)
- [Архитектура](#архитектура)
- [Endpoint'ы](#endpointы)
- [Запуск](#запуск)
- [Проверка обычной работы](#проверка-обычной-работы)
- [Проверка отказа и восстановления](#проверка-отказа-и-восстановления)
- [Остановка](#остановка)

## Цель

Показать репликацию записи, поведение при отказе реплики и ручную досинхронизацию после восстановления.

## Архитектура

- `master` - принимает клиентские записи.
- `replica-1`, `replica-2` - получают репликацию.
- Данные в памяти (`dict`), без внешней БД.

## Endpoint'ы

Master:
- `POST /data?mode=sync` - запись + репликация.
- `GET /data/{key}` - чтение с master.
- `POST /resync` - повторная отправка всего состояния на реплики.

Replica:
- `POST /replica/data` - прием записи от master.
- `GET /data/{key}` - чтение конкретного ключа.

## Запуск

```powershell
cd C:\Users\Vika\Documents\STRIS\LAB_3
docker compose up --build -d
docker compose ps
```

## Проверка обычной работы

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8202/data?mode=sync" -ContentType "application/json" -Body '{"key":"name","value":"Alice"}'
Invoke-RestMethod http://localhost:8202/data/name
Invoke-RestMethod http://localhost:8203/data/name
Invoke-RestMethod http://localhost:8204/data/name
```

## Проверка отказа и восстановления

1. Отключить `replica-1`.
2. Сделать новую запись через master (`city=Moscow`).
3. Проверить, что master и `replica-2` обновились.
4. Включить `replica-1` и убедиться, что у нее может быть рассинхрон.
5. Вызвать `POST /resync` на master и проверить, что данные выровнялись.

## Остановка

```powershell
docker compose down
```

