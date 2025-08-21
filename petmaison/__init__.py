from .app import app, create_app
from .seed import run_seed as seed_command

# Flask CLI command registration
from flask import Flask
from flask.cli import AppGroup


def register_cli(app: Flask) -> None:
    import click

    @app.cli.command("seed")
    def seed():
        """Crea datos de ejemplo"""
        seed_command()


register_cli(app)
