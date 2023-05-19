from pytest_schema import Regex, Or


user = {
    "id": int,
    "username": str,
    "email": Or(None, Regex(r".*?@.*?\.[A-Za-z]{2,6}")),
    "fio": Or(None, str),
    "created_at": str,
    "updated_at": str,
    "role": {"name": str, "description": str},
    "summaries": [
        {
            "id": int,
            "title": str,
            "description": str,
            "created_at": str,
            "updated_at": str,
        }
    ],
    "comments": [{"id": int, "text": str, "created_at": str, "updated_at": str}],
}

users: list[user] = [user]
