# Database


## Migrations

```
poetry run flask db init
poetry run flask db migrate
poetry run flask db upgrade
```

flask db migrate -m "Add custom update function"


poetry run flask db migrate -m "Initial migration"
poetry run flask db upgrade


SELECT * FROM pg_tables WHERE tablename = 'users';
