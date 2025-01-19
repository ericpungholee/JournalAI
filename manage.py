from flask.cli import FlaskGroup
from app import app, db, init_db

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    init_db()

if __name__ == "__main__":
    cli() 