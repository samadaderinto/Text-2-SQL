from invoke import task


@task
def make_migrations(ctx):
    ctx.run(f"docker-compose run server pipenv run python3 manage.py makemigrations")
    ctx.run(f"docker-compose run server pipenv run python3 manage.py migrate")
