```bash
https://github.com/ilyinon/Async_API_sprint_2
```


0. При настройке интеграции с остальными компонентами нужно корректно заполнить .env, для дев проекта можно скопировать из .env_example
```bash
cp .env_example .env
```

1. Для запуска проекта нужно выполнить команду

```bash
make all
```

Для запуска elastic и redis
```bash
make infra
```

Для запуска только приложения
```bash
make api
```

Для запуска только тестов
```bash
make test
```
