import uuid

movies_data = [
    {
        "id": str(uuid.uuid4()),
        "imdb_rating": 8.5,
        "genres": ["Action", "Sci-Fi"],
        "title": "The Star",
        "description": "New World",
        "directors_names": ["Kris", "Stew"],
        "actors_names": ["Ann", "Bob"],
        "writers_names": ["Ben", "Howard"],
        "directors": [
            {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f91", "name": "Kris"},
            {"id": "fb111f22-121e-44a7-b78f-b19191810fb2", "name": "Stew"},
        ],
        "actors": [
            {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"},
            {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "name": "Bob"},
        ],
        "writers": [
            {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
            {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "name": "Howard"},
        ],
    }
    for _ in range(60)
]
persons_data = [
    {
        "id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f91",
        "full_name": "Kris",
    },
    {
        "id": "fb111f22-121e-44a7-b78f-b19191810fb2",
        "full_name": "Stew",
    },
    {
        "id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95",
        "full_name": "Ann",
    },
    {
        "id": "fb111f22-121e-44a7-b78f-b19191810fbf",
        "full_name": "Bob",
    },
    {
        "id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5",
        "full_name": "Ben",
    },
    {
        "id": "b45bd7bc-2e16-46d5-b125-983d356768c6",
        "full_name": "Howard",
    },
]
