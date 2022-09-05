from flask import Flask, jsonify, json, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime

app = Flask(__name__, static_folder='../client/', static_url_path='/') # инициализирует проект
cors = CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.sqlite3' # задает вид базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) # создает базу данных


class New_tasks(db.Model):
  '''инициализируем таблицу с новыми заданиями'''
  id = db.Column(db.Integer, primary_key=True) # номер элемента таблиц
  date = db.Column(db.String(15), nullable=False) # дата
  content = db.Column(db.Text, nullable=False) # текст задания

  def __repr__(self):
    return f'<New_tasks {self.id} {self.content}>'


class Completed_tasks(db.Model):
  '''инициализируем таблицу с новыми заданиями'''
  id = db.Column(db.Integer, primary_key=True) # номер элемента таблиц
  date = db.Column(db.String(15), nullable=False) # дата
  content = db.Column(db.Text, nullable=False) # текст задания

class Failed_tasks(db.Model):
  '''инициализируем таблицу с новыми заданиями'''
  id = db.Column(db.Integer, primary_key=True) # номер элемента таблиц
  date = db.Column(db.String(15), nullable=False) # дата
  content = db.Column(db.Text, nullable=False) # текст задания


def task_serialiser(task):
  return {
    'id': task.id,
    'content': task.content,
    'date': task.date
  }

@app.route('/')
def index():
  return app.send_static_file('index.html')


@app.route('/api/gettasks/')
def api():
   # возвращает базу данных в виде json
  return json.dumps({
    'new_tasks': [*map(task_serialiser, New_tasks.query.all())],
    'completed_tasks': [*map(task_serialiser, Completed_tasks.query.all())],
    'failed_tasks': [*map(task_serialiser, Failed_tasks.query.all())]
  })

@app.route('/api/create/', methods=['POST'])
def create():
  request_data = json.loads(request.data)
  task = New_tasks(content=request_data['content'], date=request_data['date'])

  db.session.add(task)
  db.session.commit()

  return {'201': 'task created successfully'}


@app.route('/api/delete/<task_list>/<int:id>/', methods=['POST'])
def delete(task_list, id):
  if task_list == 'new':
    New_tasks.query.filter_by(id=id).delete()
    db.session.commit()
  elif task_list == 'completed':
    Completed_tasks.query.filter_by(id=id).delete()
    db.session.commit()
  elif task_list == 'failed':
    Failed_tasks.query.filter_by(id=id).delete()
    db.session.commit()

  return {'204': 'task deleted successfully'}


@app.route('/api/move/<source>-<to>/<int:id>/', methods=['POST'])
def move(source, to, id):
  if source == 'new' and to == 'done':
    task = New_tasks.query.get(id)
    db.session.add(Completed_tasks(content=task.content, date=task.date))

    db.session.delete(task)
    db.session.commit()
  
  if source == 'new' and to == 'failed':
    task = New_tasks.query.get(id)
    db.session.add(Failed_tasks(content=task.content, date=task.date))

    db.session.delete(task)
    db.session.commit()
  
  return {'204': 'task moved successfully'}



@app.route('/api/<int:id>/')
def show(id):
  return json.dumps([*map(task_serialiser, New_tasks.query.filter_by(id=id))])



if __name__ == '__main__':
  app.run(debug=True)