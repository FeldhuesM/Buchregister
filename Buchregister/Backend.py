from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Konfiguration für die SQLite-Datenbank
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Buch-Modell für die Datenbank
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(255), nullable=False)
    available = db.Column(db.Boolean, default=True)
    reserved = db.Column(db.Boolean, default=False)
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn



# Suchfunktion für Bücher
@app.route('/books', methods=['GET'])
def search_books():
    author = request.args.get('author')
    title = request.args.get('title')
    isbn = request.args.get('isbn')

    # Durchsuche die Bücher nach den Suchkriterien
    matched_books = Book.query.filter(
        (Book.author == author) if author else True,
        (Book.title == title) if title else True,
        (Book.isbn == isbn) if isbn else True
    ).all()

    books_data = [{'title': book.title, 'author': book.author, 'isbn': book.isbn} for book in matched_books]
    return jsonify(books_data)

# Hinzufügen eines neuen Buches
@app.route('/books/add', methods=['POST'])
def add_book():
    data = request.get_json()

    # Validiere die erforderlichen Informationen
    if 'title' not in data or 'author' not in data or 'isbn' not in data:
        return jsonify({'error': 'Ungültige Buchinformationen'}), 400

    # Füge das Buch zur Datenbank hinzu
    new_book = Book(title=data['title'], author=data['author'], isbn=data['isbn'])
    db.session.add(new_book)
    db.session.commit()

    return jsonify({'message': 'Buch wurde hinzugefügt'}), 201

# Ausleihen eines Buches
@app.route('/books/<isbn>/borrow', methods=['POST'])
def borrow_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        if book.available and not book.reserved:
            book.available = False
            
            db.session.commit()
            return jsonify({'message': 'Buch wurde ausgeliehen'}), 200
        elif book.available and book.reserved:
            book.available = False
            book.reserved = False
            db.session.commit()
            return jsonify({'message': 'Buch war reserviert und wurde ausgeliehen'}), 200
        else:
            return jsonify({'error': 'Buch ist nicht verfügbar'}), 400
    else:
        return jsonify({'error': 'Buch nicht gefunden'}), 404

# Rückgabe eines Buches
@app.route('/books/<isbn>/return', methods=['POST'])
def return_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        if not book.available:
            book.available = True
            book.reserved = False
            db.session.commit()

            return jsonify({'message': 'Buch wurde zurückgegeben'}), 200
        else:
            return jsonify({'error': 'Ungültige Rückgabe'}), 400
    else:
        return jsonify({'error': 'Buch nicht gefunden'}), 404

# Buchreservierung
@app.route('/books/<isbn>/reserve', methods=['POST'])
def reserve_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        if book.available and not book.reserved:
            
            book.reserved = True
            db.session.commit()
            return jsonify({'message': 'Buch wurde Ausgeliehen'}), 200
        elif book.reserved:
            return jsonify({'error':'Buch ist bereits Reserviert'}),401
        else:
            return jsonify({'error': 'Buch ist bereits ausgeliehen'}), 400
    else:
        return jsonify({'error': 'Buch nicht gefunden'}), 404

# Bearbeiten von Buchinformationen
@app.route('/books/<isbn>', methods=['PUT']) 
def edit_book(isbn):
    data = request.get_json()

    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        if 'genre' in data:
            book.genre = data['genre']
        db.session.commit()
        return jsonify({'message': 'Buch wurde aktualisiert'}), 200
    else:
        return jsonify({'error': 'Buch nicht gefunden'}), 404

if __name__ == '__main__':
    # Erstelle die Datenbanktabellen (falls nicht vorhanden)
    with app.app_context():
        db.create_all()
    app.run()