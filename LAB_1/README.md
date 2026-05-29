# LAB_1 - Балансировка, Reverse Proxy и кэширование

## Цель

Показать работу трех механизмов:
- балансировка нагрузки (Round Robin);
- reverse proxy;
- кэширование ответов.

## Архитектура

- `service-1` и `service-2` - два экземпляра одного API.
- `nginx` - единая точка входа и балансировщик.
- `redis` - общий кэш для endpoint `/data?id=`.

## Что реализовано

- `GET /info` - возвращает имя сервиса и время.
- `GET /data?id=` - при первом запросе генерирует значение, при повторном отдает из кэша.
- Nginx распределяет запросы между `service-1` и `service-2`.

## Запуск

```powershell
cd C:\Users\Vika\Documents\STRIS\LAB_1
docker compose up --build -d
docker compose ps
```

## Проверка

1. Проверка двух инстансов:
- `http://localhost:8081/info`
- `http://localhost:8082/info`

2. Проверка Round Robin через proxy:
```powershell
1..6 | ForEach-Object { (Invoke-RestMethod http://localhost:8080/info).service }
```

3. Проверка кэша:
- `http://localhost:8080/data?id=1` -> `source: generated`
- повторно `http://localhost:8080/data?id=1` -> `source: cache`

## Остановка

```powershell
docker compose down
```
