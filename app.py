import sqlite3

from flask import Flask, render_template, request, flash, redirect, url_for, session


app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

def get_db_connection():
 conn = sqlite3.connect('visitka.db')

 cursor = conn.cursor()

# cursor.execute('insert into admin (login, password) values ("admin", "admin"')
 conn.commit()
 return conn

@app.route('/', methods=('GET', 'POST'))
def index():
 zaps = ''
 suc = ''
 zap = ''
 zap_error = ''
 if 'zap' in session:
  zap = session['zap']
  del session['zap']
 if 'zap_error' in session:
  zap_error = session['zap_error']
  del session['zap_error']
 if request.method == 'POST':
  fio = request.form['name']
  phone = request.form['phone']
  email = request.form['email']
  service = request.form['service']
  message = request.form['message']
  print(fio, phone, email, service, message)
  conn = get_db_connection()
  cursor = conn.cursor()

  cursor.execute('insert into zayavki (fio, email, phone, service, message) values (?,?,?,?,?)',
                 (fio, email, phone, service, message))
  conn.commit()
  conn.close()
  suc = 'Заявка успешно отправлена'
 return render_template('index.html', data={'suc':suc, 'zap':zap, 'zaps': zaps, 'zap_error':zap_error})

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

@app.route('/zap', methods=('POST', 'GET'))
def zap():
 session['zap_error'] = ''
 fio = request.form['fio']
 datetime = request.form['datetime']
 conn = get_db_connection()
 cursor = conn.cursor()
 datetimel = cursor.execute('select * from freedatetime where status = 0').fetchall()
 dd = []
 for i in datetimel:
  dd.append(i[1])

 if datetime in dd:
  cursor.execute('update freedatetime set status = 1 where datetime = ?', (datetime, ))
  conn.commit()
  cursor.execute('insert into zap (fio, datetime) values (?,?)',
                (fio, datetime))
  session['zap'] = 'Вы успешно записались на консультацию!'
  conn.commit()
  conn.close()
 else:
  session['zap_error'] = 'Выберете другую дату и время!'

 return redirect('/')

@app.route('/check', methods=('POST', 'GET'))
def check():
 fio = request.form['fio']

 conn = get_db_connection()
 cursor = conn.cursor()
 cursor.execute('select * from zap where fio=?',
                (fio,))
 session['zap'] = ''
 data = cursor.fetchall()

 if data:
  dd = data
 else:
  dd = ''
 conn.commit()
 conn.close()
 suc = ''
 zap = ''
 print(dd)

 return render_template('index.html', data={'suc':suc, 'zap':zap, 'zaps': dd})

@app.route('/logoutadmin', methods=('POST', 'GET'))
def logoutadmin():
 if 'login' in session:
  del session['login']
 return redirect('/')
@app.route('/admin', methods=('POST', 'GET'))
def admin():
 conn = get_db_connection()
 cursor = conn.cursor()
 zayavki = cursor.execute('select * from zayavki').fetchall()
 conn.commit()
 zap = cursor.execute('select * from zap').fetchall()
 conn.commit()
 if request.method == 'POST':

  login = request.form['login']
  password = request.form['password']
  #cursor.execute('insert into admin (login, password) values ("admin", "admin")')
  suser = cursor.execute('select * from admin where login=? and password=?', (login, password)).fetchone()
  conn.commit()
  if len(suser) > 0:
   session['login'] = login


  return render_template('admin/login.html', data={'zayavki':zayavki, 'zap':zap})
 else:
  return render_template('admin/login.html', data={'zayavki': zayavki, 'zap':zap})


@app.route('/clearzayavki', methods=('POST', 'GET'))
def clearzayavki():
 if 'login' in session:
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute('delete from zayavki')
  conn.commit()
 return redirect('/admin')


@app.route('/clearzap', methods=('POST', 'GET'))
def clearzap():
 if 'login' in session:
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute('delete from zap')
  conn.commit()
 return redirect('/admin')

@app.route('/freedatetime', methods=('POST', 'GET'))
def freedatetime():
 conn = get_db_connection()
 cursor = conn.cursor()

 if 'login' in session:
  if request.method == 'POST':

   datetime = request.form['datetime']
   cursor.execute('insert into freedatetime (datetime, status) values (?, ?)', (datetime, '0'))
   conn.commit()
 freedatetimeall = cursor.execute('select * from freedatetime').fetchall()
 conn.commit()
 return render_template('admin/freetimedate.html', data={'freedatetimeall': freedatetimeall})


@app.route('/deletedatetime', methods=('POST', 'GET'))
def deletedatetime():
 conn = get_db_connection()
 cursor = conn.cursor()
 if 'login' in session:
  if request.method == 'POST':
   id = request.form['id']
   datetime = cursor.execute('select * from freedatetime where id=?', (id,)).fetchone()[1]
   conn.commit()

   cursor.execute('delete from freedatetime where id=?', (id,))
   conn.commit()

   cursor.execute('delete from zap where datetime=?', (datetime,))
   conn.commit()
 return redirect('freedatetime')
