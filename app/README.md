# Django Budget Management Application

## Overview
This application provides a backend API for budget management. Built with Django and Django REST Framework, it offers secure authentication and robust API endpoints for managing budget-related data.

## Tech Stack
- Python 3.8+
- Django 4.2
- Django REST Framework
- JWT Authentication
- Azure EventHub Integration
- MSSQL Database

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Poetry for dependency management

### Installation

1. Navigate to the app directory:
    ```bash
    cd app
    ```
2. Install dependencies using Poetry:
    ```bash
    poetry install
    ```
3. Activate the virtual environment:
    ```bash
    poetry shell
    ```
4. Run migrations:
    ```bash
    python manage.py migrate
    ```
5. Start the development server:
    ```bash
    python manage.py runserver
    ```
## Project Structure
app/ 
├── manage.py 
├── app/ # Main Django project settings 
├── api/ # API endpoints and serializers 
├── core/ # Core application logic 
├── tests/ # Test suite └── pyproject.toml # Poetry dependency configuration

## Key Dependencies
- Django: Web framework
- Django REST Framework: API building toolkit
- djangorestframework-simplejwt: JWT authentication
- djangorestframework-api-key: API key authentication
- drf-spectacular: API documentation
- daphne/uvicorn/gunicorn: ASGI/WSGI servers
- azure-eventhub: Azure EventHub integration
- mssql-django and pyodbc: MS SQL database connectivity
- kafka-python: Kafka integration

## Development Workflow
- Use Poetry for dependency management (`poetry add <package>`)
- Run tests with pytest (`poetry run pytest`)
- Format code with black (`poetry run black .`)
- Sort imports with isort (`poetry run isort .`)
- Check code quality with flake8 (`poetry run flake8`)

```mermaid
    erDiagram
        Advertiser ||--o{ User : "has many"
        Advertiser ||--o{ Ad : "has many"
        Advertiser ||--o{ ClickEvent : "has many"
        Advertiser ||--o{ SpendSummary : "has many"
        Advertiser ||--o{ BudgetEvent : "has many"
        Ad ||--o{ ClickEvent : "has clicks"
    
        User {
            int id PK
            string first_name
            string last_name
            string email UK
            string username
            int advertiser_id FK
            boolean is_active
            boolean is_staff
            datetime created_at
            datetime updated_at
        }
    
        Advertiser {
            int advertiser_id PK
            string name
            string industry
            string country
            datetime created_at
            boolean is_active
        }
    
        Ad {
            int ad_id PK
            int advertiser_id FK
            string ad_title
            string ad_format
            url product_link
            datetime created_at
            boolean is_active
        }
    
        TimeHierarchy {
            date time_key PK
            int hour
            int day
            int week
            int month
            string weekday_name
            datetime created_at
            boolean is_active
        }
    
        ClickEvent {
            uuid click_id PK
            int advertiser_id FK
            int ad_id FK
            datetime click_time
            float amount
            boolean is_valid
            datetime created_at
            datetime updated_at
        }
    
        SpendSummary {
            int id PK
            int advertiser_id FK
            datetime window_start
            datetime window_end
            float gross_spend
            float net_spend
            float budget_at_time
            boolean can_serve
            datetime created_at
            datetime updated_at
        }
    
        BudgetEvent {
            uuid event_id PK
            int advertiser_id FK
            float new_budget_value
            datetime event_time
            string source
            datetime created_at
            datetime updated_at
        }
