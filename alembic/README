Generic single-database configuration.


# создать миграцию
alembic revision --autogenerate -m "Add a column tickets.code"
# применить миграции
alembic upgrade head

After creating a migration, either manually or as --autogenerate, you must apply it with alembic upgrade head. If you used db.create_all() from a shell, you can use alembic stamp head to indicate that the current state of the database represents the application of all migrations

в проекте можно подглядеть какие-то вещи по настрйке алембика
https://github.com/alvassin/alembic-quickstart/tree/master

справка по alembica
https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-second-migration