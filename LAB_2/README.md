# LAB_2 - Репликация данных (master + 2 replicas)

## Цель

Смоделировать базовую репликацию без БД: одна master-нода принимает запросы и дублирует данные на реплики.

## Архитектура

- `master` - точка чтения/записи для клиента.
- `replica-1`, `replica-2` - принимают копии данных от master.
- Хранилище в памяти (`dict`) на каждой ноде.

## Что реализовано

- `POST /set` на master:
  - запись локально;
  - попытка репликации на обе реплики.
- `GET /get/{key}` на master:
  - чтение с master;
  - дополнительный опрос реплик для контроля состояния.
- `GET /state` на каждой ноде для просмотра текущего словаря.

## Запуск

```powershell
cd C:\Users\Vika\Documents\STRIS\LAB_2
docker compose up --build -d
docker compose ps
```

## Проверка

Запись:
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8102/set -ContentType "application/json" -Body '{"key":"user:1","value":"Alice"}'
```

Чтение:
```powershell
Invoke-RestMethod http://localhost:8102/get/user:1
```

Состояние нод:
```powershell
Invoke-RestMethod http://localhost:8102/state
Invoke-RestMethod http://localhost:8103/state
Invoke-RestMethod http://localhost:8104/state
```

## Сценарий сбоя

1. Выключить реплику:
```powershell
docker stop lab2-replica-1
```

2. Сделать новую запись через master.

3. Убедиться, что master и активная реплика обновились, а для выключенной вернулась ошибка репликации.

## Остановка

```powershell
docker compose down
```
