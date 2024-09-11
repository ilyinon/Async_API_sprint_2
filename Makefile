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

all_first:
	docker-compose -f docker-compose.yml -f app/docker-compose.yml -f tests/functional/docker-compose.yml -f docker-compose-override.yml up -d --build
	curl -X DELETE "localhost:9200/movies?pretty"
	curl -X DELETE "localhost:9200/genres?pretty"
	curl -X DELETE "localhost:9200/persons?pretty"
	curl -X PUT -H "Content-Type: application/json" -d @./data/movies_index.json "localhost:9200/movies?pretty"
	curl -X PUT -H "Content-Type: application/json" -d @./data/genres_index.json "localhost:9200/genres?pretty"
	curl -X PUT -H "Content-Type: application/json" -d @./data/persons_index.json "localhost:9200/persons?pretty"
	docker run -ti -v ./data/:/data --network=async_api_sprint_2_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/movies_data.json --output=http://elastic:9200/movies
	docker run -ti -v ./data/:/data --network=async_api_sprint_2_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/genres_data.json --output=http://elastic:9200/genres
	docker run -ti -v ./data/:/data --network=async_api_sprint_2_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/persons_data.json --output=http://elastic:9200/persons

stop:
	docker-compose -f docker-compose.yml -f app/docker-compose.yml -f tests/functional/docker-compose.yml down

status:
	docker-compose ps

logs:
	docker-compose logs -f
