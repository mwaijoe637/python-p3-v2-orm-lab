import sqlite3
from lib import CONN, CURSOR

class Employee:
    all = {}

    def __init__(self, name, department):
        self.id = None
        self.name = name
        self.department = department

    def __repr__(self):
        return f"<Employee {self.id}: {self.name} - Department: {self.department.name}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                department_id INTEGER,
                FOREIGN KEY(department_id) REFERENCES departments(id)
            )
        ''')
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute('DROP TABLE IF EXISTS employees')
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO employees (name, department_id) 
                VALUES (?, ?)
            ''', (self.name, self.department.id))
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            CURSOR.execute('''
                UPDATE employees 
                SET name = ?, department_id = ?
                WHERE id = ?
            ''', (self.name, self.department.id, self.id))
        CONN.commit()

    @classmethod
    def create(cls, name, department):
        employee = cls(name, department)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        id, name, department_id = row
        if id in cls.all:
            return cls.all[id]
        from lib.department import Department
        department = Department.find_by_id(department_id)
        employee = cls(name, department)
        employee.id = id
        cls.all[id] = employee
        return employee

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute('SELECT * FROM employees WHERE id = ?', (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self, name=None, department=None):
        if name is not None:
            self.name = name
        if department is not None:
            self.department = department
        self.save()

    def delete(self):
        if self.id is not None:
            CURSOR.execute('DELETE FROM employees WHERE id = ?', (self.id,))
            del Employee.all[self.id]
            self.id = None
            CONN.commit()

    @classmethod
    def get_all(cls):
        CURSOR.execute('SELECT * FROM employees')
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def reviews(self):
        from lib.review import Review
        CURSOR.execute('SELECT * FROM reviews WHERE employee_id = ?', (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]
