### Generic single-database configuration.

Create a database state version:
```commandline
alembic revision --autogenerate -m "init"
```

Update version
```commandline
alembic upgrade head
```

Downgrade version
```commandline
alembic downgrade head-1
```