import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from psycopg2 import Error

app = Flask(__name__)
app.secret_key = 'abcxyz'

try:
    mydb = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="Deepika@2004",
        database="library1",
        port=5432,
    )
    mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            password VARCHAR(255)
        )
    """)
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS book (
            bid VARCHAR(255) PRIMARY KEY,
            bname VARCHAR(255),
            bcategory VARCHAR(255),
            language VARCHAR(255),
            byear VARCHAR(255)
        )
    """)
    
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS author (
            author_name VARCHAR(300),
            title VARCHAR(300),
            bid VARCHAR(255) PRIMARY KEY,
            description VARCHAR(500),
            FOREIGN KEY (bid) REFERENCES book (bid) ON DELETE CASCADE
        )
    """)
    
    mydb.commit()
    print("Connected to database and ensured tables exist.")
except Exception as e:
    print(f"Error: {e}")

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/student1', methods=['POST', 'GET'])
def student1():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        mycursor = None
        try:
            mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
            mycursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = mycursor.fetchone()
            if user:
                return render_template('index1.html')
            else:
                message = 'Please enter correct username / password!'
                flash(message)
                return render_template('student.html'), 401
        except Error as e:
            print(f"Error: {e}")
        finally:
            if mycursor:
                mycursor.close()
    return render_template('student.html')

@app.route('/admin1', methods=['POST', 'GET'])
def admin1():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        mycursor = None
        try:
            mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
            mycursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = mycursor.fetchone()
            if user:
                return render_template('index.html')
            else:
                message = 'Please enter correct username / password!'
                flash(message)
                return render_template('admin.html'), 401
        except Error as e:
            print(f"Error: {e}")
        finally:
            if mycursor:
                mycursor.close()
    return render_template('admin.html')

@app.route('/home', methods=['GET', 'POST'])
def admin_home():
    return render_template('home.html')

@app.route('/table1', methods=['GET', 'POST'])
def table1():
    mycursor = None
    book_dicts = []  
    try:
        mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
        mycursor.execute("""
            SELECT b.bid, b.bname, b.bcategory, b.language, b.byear, a.author_name, a.description
            FROM book b
            LEFT JOIN author a ON b.bid = a.bid
        """)
        books = mycursor.fetchall()
        for book in books:
            book_dict = {
                'bid': book['bid'],
                'bname': book['bname'],
                'bcategory': book['bcategory'],
                'language': book['language'],
                'byear': book['byear'],
                'author_name': book['author_name'],
                'description': book['description'],
            }
            book_dicts.append(book_dict)
    except Error as e:
        print(f"Error: {e}")
    finally:
        if mycursor:
            mycursor.close()
    return render_template('table1.html', books=book_dicts)

@app.route('/get', methods=['POST'])
def get():
    bname = request.form.get('bname')
    bcategory = request.form.get('bcategory')
    language = request.form.get('language')
    byear = request.form.get('byear')
    bid = request.form.get('bid')
    author_name = request.form.get('author_name')
    description = request.form.get('description')

    book_values = (bid, bname, bcategory, language, byear)
    author_values = (author_name, bname, bid, description)  # Include bid here

    mycursor = None
    try:
        mycursor = mydb.cursor()

        # Insert into book table
        mycursor.execute("""
            INSERT INTO book (bid, bname, bcategory, language, byear)
            VALUES (%s, %s, %s, %s, %s)
        """, book_values)

        # Insert into author table
        mycursor.execute("""
            INSERT INTO author (author_name, title, bid, description)
            VALUES (%s, %s, %s, %s)
        """, author_values)

        mydb.commit()
        print("Record added to 'book' and 'author' tables")
        text = "0"  # Success indicator
    except Exception as e:
        text = "1"  # Failure indicator
        print("Error:", e)
    finally:
        if mycursor:
            mycursor.close()

    return render_template('home.html', success=text)



@app.route('/table', methods=['GET', 'POST'])
def table():
    mycursor = None
    book_dicts = []  
    try:
        mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
        mycursor.execute("SELECT bid, bname, bcategory, language, byear FROM book")
        books = mycursor.fetchall()
        for book in books:
            book_dict = {
                'bid': book['bid'],
                'bname': book['bname'],
                'bcategory': book['bcategory'],
                'language': book['language'],
                'byear': book['byear'],
            }
            book_dicts.append(book_dict)
    except Error as e:
        print(f"Error: {e}")
    finally:
        if mycursor:
            mycursor.close()
    return render_template('table.html', books=book_dicts)

@app.route('/edit/<string:bid>', methods=['GET', 'POST'])
def edit(bid):
    if request.method == 'GET':
        mycursor = None
        try:
            mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
            mycursor.execute("SELECT * FROM book b LEFT JOIN author a ON b.bid = a.bid WHERE b.bid = %s", (bid,))
            book = mycursor.fetchone()
            if book:
                book_dict = {
                    'bid': book['bid'],
                    'bname': book['bname'],
                    'bcategory': book['bcategory'],
                    'language': book['language'],
                    'byear': book['byear'],
                    'author_name': book['author_name'],
                    'description': book['description'],
                }
                return render_template('edit.html', book=book_dict)
            else:
                return "Book not found", 404
        except Error as e:
            print(f"Error: {e}")
        finally:
            if mycursor:
                mycursor.close()
    elif request.method == 'POST':
        bname = request.form.get('bname')
        bcategory = request.form.get('bcategory')
        language = request.form.get('language')
        byear = request.form.get('byear')
        author_name = request.form.get('author_name')
        description = request.form.get('description')
        
        mycursor = None
        try:
            mycursor = mydb.cursor()
            # Update book table
            update_book_query = """
                UPDATE book
                SET bname = %s, bcategory = %s, language = %s, byear = %s
                WHERE bid = %s
            """
            mycursor.execute(update_book_query, (bname, bcategory, language, byear, bid))
            
            # Update author table
            update_author_query = """
                UPDATE author
                SET author_name = %s, description = %s
                WHERE bid = %s
            """
            mycursor.execute(update_author_query, (author_name, description, bid))
            
            mydb.commit()
            return redirect('/table')  # Redirect to the book listing page after update
        except Error as e:
            print(f"Error: {e}")
        finally:
            if mycursor:
                mycursor.close()
        
        return redirect('/table')  # Ensure you have a fallback redirect in case of any error





@app.route('/delete/<string:bid>', methods=['GET', 'POST'])
def delete(bid):
    mycursor = None
    try:
        mycursor = mydb.cursor()
        mycursor.execute("DELETE FROM book WHERE bid = %s", (bid,))
        mydb.commit()
        print(f"Record with ID {bid} deleted from 'book' table")
    except Error as e:
        print("Error:", e)
    finally:
        if mycursor:
            mycursor.close()
    return redirect('/table')

if __name__ == '__main__':
    app.run(debug=True)
