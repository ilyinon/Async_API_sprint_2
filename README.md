```bash
https://github.com/ilyinon/Async_API_sprint_2
```


0. При настройке интеграции с остальными компонентами нужно корректно заполнить .env, для дев проекта можно скопировать из .env_test. 
```bash
cp .env_test .env
```

1. Для запуска тестов необходимы redis и elastic, 

Для запуска elastic и redis
```bash
make infra
```

2. Для запуска тестов нужно выполнить следующую команду

Для запуска тестов
```bash
make test
```

Для просмотра результатов нужно выполнить команду 
```bash
make test_info
```


Во время запуска тестов создаются временные индексы movies_test, genres_test, persons_test.
