from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
import json
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

USERNAME = "admin"
PASSWORD = "1234"

# DB conf
DATABASE_URI='postgresql://team4:0000@localhost:5432/flask_task'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)

# jwt conf
app.config['JWT_SECRET_KEY'] = "secrt1246"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True ,autoincrement = True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"Category ('{self.name}')"



class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title = db.Column(db.String, nullable=False)
    details = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id  = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship("Category", foreign_keys = [category_id])


    def __repr__(self):
        return f'Task("{self.title}", "{self.created_at}")'

@app.route('/category', methods=['GET', 'POST'])
def category():
    if request.method == 'GET':
        all_categories = Category.query.all() #>> Queryset
        result = []
        for category in all_categories:
            dict = {}
            dict['id'] = category.id
            dict['name'] = category.name
            result.append(dict)

        return jsonify({
            "categories":result
        })

    elif request.method == 'POST':

        name = request.json.get('name')        
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()

        return jsonify({
            "status":"success",
            "data": f"{name} catigory added successfully"
        })

@app.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == 'GET':
        all_tasks = Task.query.all()
        result = []
        for task in all_tasks:
            dict = {}
            cat = Category.query.filter_by(id=task.category_id).first()

            dict['id'] = task.id
            dict['title'] = task.title
            dict['details'] = task.details
            dict['created_at'] = task.created_at
            dict['catigory'] = cat.name

            result.append(dict)
        
        return jsonify({
            "status":"success",
            "data": result
        })

    if request.method == 'POST':

        title = request.json.get('title')
        details = request.json.get('details')
        category_id = request.json.get('category_id')

        newTask = Task(title=title, details=details,category_id=category_id)
        db.session.add(newTask)
        db.session.commit()

        return jsonify({
            "status":"success",
            "data": f"task {title} added successfully"
        })

@app.route('/task/<int:id>', methods=['GET', 'DELETE', 'PUT'])
@jwt_required()
def edit_task(id):
    username = get_jwt_identity()
    print(username)
    task= Task.query.filter_by(id=id).first()
    if request.method == 'GET':
        dict = {}
        cat = Category.query.filter_by(id=task.category_id).first()

        dict['id'] = task.id
        dict['title'] = task.title
        dict['details'] = task.details
        dict['created_at'] = task.created_at
        dict['catigory'] = cat.name

        return jsonify({
            "data":dict
        })

    if request.method == 'PUT':
        if request.json.get('title'):
            task.title = request.json.get('title')
        if request.json.get('details'):
            task.details = request.json.get('details')
        if request.json.get('category_id'):
            task.category_id = request.json.get('category_id')

        db.session.commit()

        return jsonify({
            "status":"success",
            "data": "user upadted successfully"
        })
    
    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            "status":"success",
            "data": "user deleted successfully"
        })

# auth endpoints
@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    if data['username'] == USERNAME and data['password'] == PASSWORD:
        access_token = create_access_token(identity=data["username"]) 

        return jsonify({
            "status" : "success",
            "data" : {'access_token': access_token}
        })

    else:
        return jsonify({
            "status" : "failure ",
            'msg': 'wrong username or password' 
        })

@app.route('/protected', methods=['Get'])
@jwt_required()
def protected():
        username=get_jwt_identity()
        return jsonify({
            "status" : "success",
            "msg" : f"welcome {username}"
        })

    


@app.route('/')
def home():

    return "<h1> The final task isa is flassk </h1>"

app.run(host='127.0.0.1', port=5000, debug=True)
db.create_all()