import uuid


def generate_genre(genre_id: str):
    return [
        {
            "id": genre_id,
            "name": "Action",
            "description": "Any description",
        }
    ]


def generate_genres(count: int, name: str, description: str):
    return [
        {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
        }
        for _ in range(count)
    ]
