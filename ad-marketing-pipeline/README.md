ad-marketing-pipeline/
├── pyproject.toml
├── README.md
├── src/
│   └───
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py
│       ├── processors/
│       │   ├── __init__.py
│       │   ├── bronze_processor.py
│       │   ├── silver_processor.py
│       │   └── gold_processor.py
│       ├── streaming/
│       │   ├── __init__.py
│       │   └── event_hub_streamer.py
│       └── utils/
│           ├── __init__.py
│           └── database_manager.py
├── notebooks/
│   ├── orchestration/
│   │   ├── run_bronze_to_silver.py
│   │   ├── run_silver_to_gold.py
│   │   └── setup_streaming.py
│   └── setup/
│       └── provision_tables.py
└── tests/
    ├── __init__.py
    └── test_processors.py