infra:
	docker-compose -f docker-compose.yml up -d --build

api:
	$(MAKE) infra
	docker-compose -f docker-compose.yml -f app/docker-compose.yml up -d --build

test:
	docker-compose -f docker-compose.yml -f tests/functional/docker-compose.yml stop test
	docker-compose -f docker-compose.yml -f tests/functional/docker-compose.yml rm --force test
	docker-compose -f docker-compose.yml -f tests/functional/docker-compose.yml up -d --build

test_info:
	docker-compose -f docker-compose.yml -f tests/functional/docker-compose.yml logs -f test

all:
	$(MAKE) infra
	$(MAKE) api
	$(MAKE) test

stop:
	docker-compose -f docker-compose.yml -f app/docker-compose.yml -f tests/functional/docker-compose.yml down

status:
	docker-compose ps

logs:
	docker-compose logs -f
