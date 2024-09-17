import random
import uuid

from faker import Faker
from faker.providers import company
from genres import GENRES_DATA

fake = Faker()
fake.add_provider(company)


def get_genres(count: int):
    list_genres = []
    for i in range(count):
        list_genres.append(GENRES_DATA[random.randrange(len(GENRES_DATA))]["name"])
    return list_genres


def generate_person():
    return {"id": str(uuid.uuid4()), "name": fake.name()}


def generate_persons(count: int):
    tmp_list = []
    for _ in range(count):
        tmp_list.append(generate_person())
    return tmp_list


GENERATED_PERSONS_DATA = generate_persons(50)


def get_person_from_data(count: int):
    tmp_list = []
    for _ in range(count):
        tmp_list.append(
            GENERATED_PERSONS_DATA[random.randrange(len(GENERATED_PERSONS_DATA))]
        )
    return tmp_list


def generate_movie(id: str):
    generated_actors_list = get_person_from_data(random.randrange(1, 3))
    generated_writers_list = get_person_from_data(random.randrange(1, 3))
    generated_directors_list = get_person_from_data(random.randrange(1, 3))
    return [
        {
            "id": id,
            "imdb_rating": round(random.uniform(1, 10), 1),
            "genres": get_genres(random.randrange(1, 3)),
            "title": fake.company(),
            "description": fake.text(),
            "directors_names": [x["name"] for x in generated_directors_list],
            "actors_names": [x["name"] for x in generated_actors_list],
            "writers_names": [x["name"] for x in generated_writers_list],
            "directors": generated_directors_list,
            "actors": generated_actors_list,
            "writers": generated_writers_list,
        }
    ]


def generate_movies(count: int):
    tmp_list = []
    for _ in range(count):
        tmp_list.append(generate_movie(str(uuid.uuid4())))
    return tmp_list
