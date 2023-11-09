import sqlite3

from flask import Flask, render_template, request, flash, redirect, url_for, session


app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

def get_db_connection():
 conn = sqlite3.connect('visitka.db')
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
 cursor = conn.cursor()
 services = cursor.execute('SELECT * FROM services').fetchall()
 conn.commit()
 conn.close()
 return render_template('services.html', services=services)

@app.route('/reg', methods=('GET', 'POST'))
def reg():
 if request.method == 'POST':
  fio = request.form['fio']
  login = request.form['login']
  password = request.form['password']
  email = request.form['email']
  phone = request.form['phone']
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute('insert into users (fio, login, password, email, phone) values (?,?,?,?,?)', (fio, login, password, email, phone))
  conn.commit()
  conn.close()
  data = dict(suc='Вы успешно зарегистрированы!')
  return render_template('reg.html', data=data)
 return render_template('reg.html', data={'suc':''})

@app.route('/auth', methods=('GET', 'POST'))
def auth():
 suc = ''
 if request.method == 'POST':
  login = request.form['login']
  password = request.form['password']
  conn = get_db_connection()
  cursor = conn.cursor()
  suser = cursor.execute('select * from users where login=? and password=?', (login, password)).fetchone()
  conn.commit()
  if not suser == None:
   session['login'] = suser[2]
   suc = 'Вы успешно авторизировались!'
  else:
   suc = 'Ошибка авторизации'''
 data = dict(suc=suc)
 return render_template('auth.html', data=data)


@app.route('/panel', methods=('GET', 'POST'))
def panel():
 login = session['login']
 conn = get_db_connection()
 cursor = conn.cursor()
 suser = cursor.execute('select * from users where login=?', (login,)).fetchone()
 conn.commit()
 data = dict(fio=suser[1],login=suser[2], email=suser[4],phone=suser[5])
 return render_template('panel.html', data=data)