import json
import os
from datetime import datetime

from .app import app
from .models import db

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FANTASY_DATABASE_FILENAME = os.path.join(
    PROJECT_ROOT,
    'node_modules',
    'fantasy-database',
    'data.json'
)

with app.app_context():
    db.drop_all()
    db.create_all()

    with open(FANTASY_DATABASE_FILENAME, 'r') as f:
        data = json.loads(f.read())

    connection = db.engine.connect()
    for table in db.metadata.sorted_tables:
        rows = data[table.name]

        for row in rows:
            for column, value in row.items():
                if isinstance(table.columns[column].type, db.Date) and value:
                    row[column] = datetime.strptime(value, '%Y-%m-%d').date()

        connection.execute(table.insert(), rows)

        if table.name != 'books_stores':
            connection.execute(
                'ALTER SEQUENCE {table}_id_seq RESTART WITH {num_rows}'.format(
                    table=table.name,
                    num_rows=len(rows) + 1
                )
            )
