# hospital_shift_scheduler
An intelligent shift scheduler designed for hospitals. 

## Project Structure
```
hospital_shift_scheduler/
├── app/
│   ├── __init__.py
│   ├── core/               # Scheduling logic lives here
│   │   ├── __init__.py
│   │   └── scheduler.py
│   ├── api/                # API routes (for when you build FastAPI later)
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── models/             # Data models (pydantic models etc.)
│   │   ├── __init__.py
│   │   └── shift_models.py
│   └── services/           # Services interfacing between API and core logic
│       ├── __init__.py
│       └── schedule_service.py
├── tests/
│   └── test_scheduler.py
├── .gitignore
├── requirements.txt
├── README.md
└── main.py
```

