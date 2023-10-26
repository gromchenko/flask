import sqlite3

from flask import Flask, render_template
app = Flask(__name__)
def get_db_connection():
 conn = sqlite3.connect('visitka.db')
 conn.row_factory = sqlite3.Row
 return conn

@app.route('/')
def index():
 return render_template('index.html')

@app.route('/about', methods=['GET'])
def about():
 return render_template('about.html')

@app.route('/contacts', methods=['GET'])
def contacts():
 return render_template('contacts.html')

@app.route('/sevices', methods=['GET'])
def sevices():
 conn = get_db_connection()
 services = conn.execute('SELECT * FROM services').fetchall()
 conn.close()
 return render_template('services.html', services=services)