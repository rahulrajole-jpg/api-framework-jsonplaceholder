# JSONPlaceholder API Test Automation Framework

A scalable, production-quality API automation framework using Python, Pytest, Requests, and SQLite for validating the JSONPlaceholder public REST APIs.

## Features
- Functional, contract, and cross-API testing
- In-memory SQLite DB for API vs DB validation
- Schema validation
- Retry and reliability mechanisms
- Parallel execution (pytest-xdist)
- Allure/HTML reporting
- Jenkins CI/CD pipeline

## Folder Structure
```
jsonplaceholder_api_framework/
│
├── config/
│   └── config.yaml
├── data/
│   └── schemas/
│       ├── user_schema.json
│       ├── post_schema.json
│       ├── comment_schema.json
│       ├── album_schema.json
│       └── todo_schema.json
├── db/
│   └── sqlite_client.py
├── src/
│   ├── api/
│   │   ├── base_client.py
│   │   ├── users_api.py
│   │   ├── posts_api.py
│   │   ├── comments_api.py
│   │   ├── albums_api.py
│   │   └── todos_api.py
│   ├── utils/
│   │   ├── logger.py
│   │   ├── schema_validator.py
│   │   ├── retry_decorator.py
│   │   └── email_validator.py
│   └── models/
│       ├── user.py
│       ├── post.py
│       ├── comment.py
│       ├── album.py
│       └── todo.py
├── tests/
│   ├── conftest.py
│   ├── test_users.py
│   ├── test_posts.py
│   ├── test_comments.py
│   ├── test_albums.py
│   └── test_todos.py
├── requirements.txt
├── pytest.ini
├── Jenkinsfile
└── README.md
```

---

## Quick Start
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `pytest -n auto --alluredir=allure-results`
4. Generate Allure report: `allure generate allure-results -o allure-report --clean`

---

## See each folder/file for details and code samples.
