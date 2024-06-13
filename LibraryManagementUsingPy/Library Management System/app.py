import mysql.connector
import secrets
from flask import Flask, render_template, request, redirect, url_for,session,jsonify
from mysql.connector import Error
app = Flask(__name__)
app.secret_key = 'abcxyz'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="library"
)
mycursor = mydb.cursor()
mycursor.execute("USE library")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE,
        password VARCHAR(255)
    )
""")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS book (
        id INT AUTO_INCREMENT PRIMARY KEY,
        bname VARCHAR(255),
        bcategory VARCHAR(255),
        language VARCHAR(255),
        byear VARCHAR(255),
        bnumber VARCHAR(255)
    )
""")
print("Connected to database and ensured 'users' and 'book' tables exist.")

app = Flask(__name__)
@app.route('/')
def login():
    return render_template('login.html')
@app.route('/admin')
def admin():
    return render_template('admin.html')
@app.route('/student')
def student():
    return render_template('student.html')
@app.route('/student1', methods=['POST','GET'])
def student1():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = mycursor.fetchone()
            if user:
                return render_template('index1.html')
            else:
                message = 'Please enter correct username / password!'
                return render_template('student.html', message=message), 401
        except Error as e:
            print(f"Error: {e}")
        finally:
            mycursor.close()
    return render_template('student.html')  

@app.route('/admin1', methods=['POST'])
def admin1():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = mycursor.fetchone()
            if user:
                return render_template('index.html')
            else:
                message = 'Please enter correct username / password!'
                return render_template('admin.html', message=message), 401
        except Error as e:
            print(f"Error: {e}")
        finally:
            mycursor.close()
    return render_template('admin.html')

@app.route('/home', methods=['GET', 'POST'])
def admin_home():
    return render_template('home.html')
@app.route('/admin1', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
@app.route('/table1', methods=['GET', 'POST'])
def table1():
    mycursor.execute("SELECT id,bname, bcategory, language, byear, bnumber FROM book")
    books = mycursor.fetchall()
    book_dicts = []
    for book in books:
        book_dict = {
            'id': book[0],
            'bname': book[1],
            'bcategory': book[2],
            'language': book[3],
            'byear': book[4],
            'bnumber': book[5]
            
        }
        book_dicts.append(book_dict)

    return render_template('table1.html', books=book_dicts)


@app.route('/get', methods=['GET', 'POST'])
def get():
    bname = request.form.get('bname')
    bcategory = request.form.get('bcategory')
    language = request.form.get('language')
    byear = request.form.get('byear')
    bnumber = request.form.get('bnumber')
    print(bname)
    book = (bname, bcategory, language, byear, bnumber)
    print("Received values:", bname, bcategory, language, byear, bnumber) 

    try:
        mycursor.execute("""
            INSERT INTO book (bname, bcategory, language, byear, bnumber)
            VALUES (%s, %s, %s, %s, %s)
        """, book)
        mydb.commit()
        print("Record added to 'book' table")
        text = "0"
        return render_template('home.html', success=text)
    except Exception as e:
        text = "1"
        print("Error:", e)
        return render_template('home.html', success=text)

@app.route('/table', methods=['GET', 'POST'])
def table():
    mycursor.execute("SELECT id,bname, bcategory, language, byear, bnumber FROM book")
    books = mycursor.fetchall()
    book_dicts = []
    for book in books:
        book_dict = {
            'id': book[0],
            'bname': book[1],
            'bcategory': book[2],
            'language': book[3],
            'byear': book[4],
            'bnumber': book[5]
            
        }
        book_dicts.append(book_dict)
        
    #return render_template('index.html', books=book_dicts)
    #print(book_dict)

    return render_template('table.html', books=book_dicts)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET':
        mycursor.execute("SELECT * FROM book WHERE id = %s", (id,))
        book = mycursor.fetchone()
        if book:
            book_dict = {
                'id': book[0],
                'bname': book[1],
                'bcategory': book[2],
                'language': book[3],
                'byear': book[4],
                'bnumber': book[5]
            }
            return render_template('edit.html', book=book_dict)
        else:
            return "Book not found", 404
    elif request.method == 'POST':
        bname = request.form.get('bname')
        bcategory = request.form.get('bcategory')
        language = request.form.get('language')
        byear = request.form.get('byear')
        bnumber = request.form.get('bnumber')
        update_query = """
            UPDATE book
            SET bname = %s, bcategory = %s, language = %s, byear = %s, bnumber = %s
            WHERE id = %s
        """
        mycursor.execute(update_query, (bname, bcategory, language, byear, bnumber, id))
        mydb.commit()
        return redirect('/table')

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    try:
        mycursor.execute("DELETE FROM book WHERE id = %s", (id,))
        mydb.commit()
        print(f"Record with ID {id} deleted from 'books' table")
    except Exception as e:
        print("Error:", e)
    return redirect('/table')


if __name__ == '__main__':
    app.run(debug=True)
