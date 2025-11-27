erDiagram
    USERS {
        int id PK "Primary Key, hidden from front-end"
        varchar name
        varchar username
        varchar email
        varchar password
        varchar status
        int age
        varchar contact_number
    }

    NEWS {
        int id PK "Primary Key"
        varchar title
        varchar category
        text content "Body of news"
        int author_id FK "Foreign Key to USERS.id"
        datetime created_at
        varchar status
    }

    USERS ||--o{ NEWS : "creates"
