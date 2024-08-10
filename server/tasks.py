from invoke import task


@task
def manage(ctx, cmd):
    ctx.run(f"docker-compose run pearmonie pipenv run python3 manage.py {cmd}")


@task
def install(ctx, cmd):
    ctx.run(f"pipenv install {cmd}")
