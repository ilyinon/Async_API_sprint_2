infra:
	docker-compose -f docker-compose.yml up -d --build

api:
	docker-compose -f docker-compose.yml -f app/docker-compose.yml up -d --build

test:
	docker-compose -f docker-compose.yml -f tests/functional/docker-compose.yml stop test
	docker-compose -f docker-compose.yml -f tests/functional/docker-compose.yml rm --force test
	docker-compose -f docker-compose.yml -f tests/functional/docker-compose.yml up -d --build

all:
	docker-compose -f docker-compose.yml -f app/docker-compose.yml -f tests/functional/docker-compose.yml up -d --build

stop:
	docker-compose -f docker-compose.yml -f app/docker-compose.yml -f tests/functional/docker-compose.yml down

status:
	docker-compose ps

logs:
	docker-compose logs -f