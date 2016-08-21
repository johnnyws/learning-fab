import datetime
from flask import Markup
from flask.ext.appbuilder import Model
from flask.ext.appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from flask.ext.appbuilder.models.decorators import renders
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Text, Table
from sqlalchemy.orm import relationship
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
class ContactGroup(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique = True, nullable=False)

    # customized render: what is the arg for?
    @renders('name')
    def my_name(self):
        return Markup('<b>' + self.name + '</b>')

    def __repr__(self):
        return self.name

class Contact(Model):
    id = Column(Integer, primary_key=True)
    name =  Column(String(150), unique = True, nullable=False)
    address =  Column(String(564), default='Street ')
    birthday = Column(Date)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    contact_group_id = Column(Integer, ForeignKey('contact_group.id'))
    contact_group = relationship("ContactGroup")

    def __repr__(self):
        return self.name

class Department(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class Function(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

def today():
    return datetime.datetime.today().strftime('%Y-%m-%d')

class Benefit(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

# many-to-many
assoc_benefits_employee = Table('benefits_employee', Model.metadata,
                                      Column('id', Integer, primary_key=True),
                                      Column('benefit_id', Integer, ForeignKey('benefit.id')),
                                      Column('employee_id', Integer, ForeignKey('employee.id'))
)

class Employee(Model):
    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    address = Column(Text(250), nullable=False)
    fiscal_number = Column(Integer, nullable=False)
    employee_number = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False)
    department = relationship("Department")
    function_id = Column(Integer, ForeignKey('function.id'), nullable=False)
    function = relationship("Function")
    benefits = relationship('Benefit', secondary=assoc_benefits_employee, backref='employee')

    begin_date = Column(Date, default=today, nullable=False)
    end_date = Column(Date, nullable=True)

    def __repr__(self):
        return self.full_name

# many-to-many association table with properties (begin_date, end_date)
class EmployeeHistory(Model):
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False)
    department = relationship("Department")
    employee_id = Column(Integer, ForeignKey('employee.id'), nullable=False)
    employee = relationship("Employee")
    begin_date = Column(Date, default=today)
    end_date = Column(Date)

"""
    Models for ChartViews
"""
class CountryStats(Model):
    id = Column(Integer, primary_key=True)
    stat_date = Column(Date, nullable=True)
    population = Column(Float)
    unemployed_perc = Column(Float)
    poor_perc = Column(Float)
    college = Column(Float)

    # function can be used in charts as well
    def college_perc(self):
        if self.population != 0:
            return (self.college*100)/self.population
        else:
            return 0.0

