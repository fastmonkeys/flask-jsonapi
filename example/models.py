from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

book_store = db.Table(
    'books_stores',
    db.Column(
        'book_id',
        db.Integer,
        db.ForeignKey('books.id', ondelete='CASCADE'),
        nullable=False
    ),
    db.Column(
        'store_id',
        db.Integer,
        db.ForeignKey('stores.id', ondelete='CASCADE'),
        nullable=False
    ),
)


class Series(db.Model):
    __tablename__ = 'series'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False, unique=True)


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(
        db.Integer,
        db.ForeignKey(Author.id),
        nullable=False
    )
    author = db.relationship(Author, backref='books')
    series_id = db.Column(db.Integer, db.ForeignKey(Series.id))
    series = db.relationship(Series, backref='books')
    date_published = db.Column(db.Date, nullable=False)
    title = db.Column(db.Text)


class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(
        db.Integer,
        db.ForeignKey(Book.id, ondelete='CASCADE'),
        nullable=False,
    )
    title = db.Column(db.Text, nullable=False)
    ordering = db.Column(db.Integer, nullable=False)
    book = db.relationship(
        Book,
        backref=db.backref(
            'chapters',
            order_by=ordering,
            passive_deletes=True
        )
    )


class Store(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    books = db.relationship(Book, secondary=book_store, backref='stores')
