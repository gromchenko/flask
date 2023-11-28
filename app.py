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
 error_auth = ''
 if 'zap' in session:
  zap = session['zap']
  del session['zap']
 if 'error_auth' in session:
  error_auth = session['error_auth']
  del session['error_auth']
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
 return render_template('index.html', data={'suc':suc, 'zap':zap, 'zaps': zaps, 'zap_error':zap_error, 'error_auth': error_auth})

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
   session['user'] = suser[2]
   suc = 'Вы успешно авторизировались!'
   return redirect('panel')
  else:
   suc = 'Ошибка авторизации'''
 data = dict(suc=suc)
 return render_template('auth.html', data=data)


@app.route('/panel', methods=('GET', 'POST'))
def panel():
 if 'user' in session:
  login = session['user']
  conn = get_db_connection()
  cursor = conn.cursor()
  suser = cursor.execute('select * from users where login=?', (login,)).fetchone()
  conn.commit()
  datetimes = cursor.execute('select * from freedatetime where status=0 order by datetime').fetchall()
  conn.commit()
  cons = cursor.execute('select * from zap where fio=?', (login,)).fetchall()
  #cons = cursor.execute('select * from zap').fetchall()
  print(cons)
  conn.commit()
  data = dict(fio=suser[1],login=suser[2], email=suser[4],phone=suser[5], cons=cons, datetimes=datetimes)
  return render_template('panel.html', data=data)
 else:
  return redirect('auth')

@app.route('/zap', methods=('POST', 'GET'))
def zap():
 if 'user' in session:
  session['zap_error'] = ''
  #fio = request.form['fio']
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
                 (session['user'], datetime))
   session['zap'] = 'Вы успешно записались на консультацию!'
   conn.commit()
   conn.close()
  else:
   session['zap_error'] = 'Выберете другую дату и время!'
 else:
  session['error_auth'] = 'Для того, чтобы записаться, необходимо пройти авторизацию'
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

 zap = cursor.execute('select * from zap order by id desc').fetchall()

 conn.commit()
 users = cursor.execute('select * from users').fetchall()
 conn.commit()
 users_fio = []
 for i in zap:
  fio = cursor.execute('select * from users where login=?', (i[1], )).fetchone()
  conn.commit()
  if fio == None:
   users_fio.append((i[0], i[1], i[2], 0))
  else:
   users_fio.append((i[0], fio[1], i[2], fio[0]))

 if request.method == 'POST':

  login = request.form['login']
  password = request.form['password']
  #cursor.execute('insert into admin (login, password) values ("admin", "admin")')
  suser = cursor.execute('select * from admin where login=? and password=?', (login, password)).fetchone()
  conn.commit()
  if len(suser) > 0:
   session['login'] = login


  return render_template('admin/login.html', data={'zayavki':zayavki, 'zap':users_fio, 'user':users})
 else:
  return render_template('admin/login.html', data={'zayavki': zayavki, 'zap':users_fio, 'users':users})


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
 freedatetimeall = cursor.execute('select * from freedatetime order by datetime').fetchall()
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



@app.route('/price', methods=['GET'])
def price():
 return render_template('price.html')


@app.route('/logoutuser', methods=('POST', 'GET'))
def logoutuser():
 if 'user' in session:
  del session['user']
 return redirect('/')

@app.route('/userdetail/<id>', methods=('POST', 'GET'))
def userdetail(id):
 conn = get_db_connection()
 cursor = conn.cursor()
 user = cursor.execute('select * from users where id=? ', (id,)).fetchone()
 conn.commit()
 return render_template('admin/dateiluser.html', data={'user': user})

@app.route('/clearusers', methods=('POST', 'GET'))
def clearusers():
 if 'login' in session:
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute('delete from users')
     conn.commit()
 return redirect('/admin')

@app.route('/datetimezap/<id>', methods=('POST', 'GET'))
def datetimezap(id):
 if 'login' in session:
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute('update freedatetime set status = 1 where id = ?', (int(id),))
     conn.commit()
     datetime = cursor.execute('select * from freedatetime where id=?', (id,)).fetchone()
     conn.commit()

     cursor.execute('insert into zap (fio, datetime) values (?,?)',
                    (session['user'], datetime[1]))
     conn.commit()
 return redirect('/panel')

