from pytest_schema import Or, Regex

summary = {
    "id": int,
    "title": str,
    "description": Or(str, None),
    "created_at": str,
    "updated_at": str,
    "user": {
        "id": int,
        "username": str,
        "email": Or(Regex(r".*?@.*?\.[A-Za-z]{2,6}"), None),
        "fio": Or(str, None),
    },
    "comments": [
        {
            "id": int,
            "text": str,
            "created_at": str,
            "updated_at": str,
            "user": {
                "id": int,
                "username": str,
                "email": Or(Regex(r".*?@.*?\.[A-Za-z]{2,6}"), None),
                "fio": Or(str, None),
            },
        }
    ],
}

summaries: list[summary] = [summary]

user_summaries = [
    {
        "id": int,
        "title": str,
        "description": Or(str, None),
        "created_at": str,
        "updated_at": str,
    }
]
