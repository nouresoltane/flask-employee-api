from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'employees.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- MODELS ---
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    employees = db.relationship('Employee', backref='department', lazy=True)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)


# --- ROUTES ---

@app.route('/')
def home():
    return "✅ Employee API is running!"


# 📌 GET: list all employees
@app.get('/employees')
def get_employees():
    employees = Employee.query.all()
    results = []
    for emp in employees:
        results.append({
            "id": emp.id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "department": emp.department.name
        })
    return jsonify(results)


# 📌 POST: add a new employee
@app.post('/employees')
def add_employee():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    dept_name = data.get('department')

    # find or create department
    dept = Department.query.filter_by(name=dept_name).first()
    if not dept:
        dept = Department(name=dept_name)
        db.session.add(dept)
        db.session.commit()

    new_emp = Employee(first_name=first_name, last_name=last_name, department_id=dept.id)
    db.session.add(new_emp)
    db.session.commit()

    return jsonify({"message": "Employee added successfully!"}), 201


# 📌 PUT: update an employee
@app.put('/employees/<int:id>')
def update_employee(id):
    emp = Employee.query.get_or_404(id)
    data = request.get_json()

    emp.first_name = data.get('first_name', emp.first_name)
    emp.last_name = data.get('last_name', emp.last_name)

    dept_name = data.get('department')
    if dept_name:
        dept = Department.query.filter_by(name=dept_name).first()
        if not dept:
            dept = Department(name=dept_name)
            db.session.add(dept)
            db.session.commit()
        emp.department_id = dept.id

    db.session.commit()
    return jsonify({"message": "Employee updated successfully!"})


# 📌 DELETE: remove an employee
@app.delete('/employees/<int:id>')
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return jsonify({"message": "Employee deleted successfully!"})


# 📌 INITIAL DATA POPULATION
@app.route('/init', methods=['GET'])
def init_data():
    # Clear old data
    db.drop_all()
    db.create_all()

    hr = Department(name="HR")
    it = Department(name="IT")
    finance = Department(name="Finance")
    db.session.add_all([hr, it, finance])
    db.session.commit()

    employees = [
        Employee(first_name="Flen", last_name="Ben Foulen", department_id=hr.id),
        Employee(first_name="Amira", last_name="Trabelsi", department_id=it.id),
        Employee(first_name="Omar", last_name="Cherif", department_id=finance.id),
        Employee(first_name="Sana", last_name="Haddad", department_id=hr.id),
        Employee(first_name="Ali", last_name="Mansour", department_id=it.id),
    ]

    db.session.add_all(employees)
    db.session.commit()
    return jsonify({"message": "Database initialized with 5 sample employees!"})


# --- MAIN ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
