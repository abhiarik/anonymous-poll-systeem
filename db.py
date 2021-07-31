from flask import g, current_app
import psycopg2


def get_db():
    if 'db' not in g:
        database = current_app.config['DATABASE']
        g.db = psycopg2.connect(f"dbname={database}")
    return g.db
