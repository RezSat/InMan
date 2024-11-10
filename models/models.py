# models/models.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Division Model
class Division(Base):
    __tablename__ = "divisions"
    division_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    # One-to-many relationship with Employee
    employees = relationship("Employee", back_populates="division")

# Employee Model
class Employee(Base):
    __tablename__ = "employees"
    emp_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    division_id = Column(Integer, ForeignKey("divisions.division_id"))
    item_count = Column(Integer, default=0)
    date_joined = Column(DateTime, default=datetime.utcnow)

    # Many-to-one relationship with Division
    division = relationship("Division", back_populates="employees")
    # Many-to-many relationship with Item through EmployeeItem
    items = relationship("EmployeeItem", back_populates="employee")

# Item Model
class Item(Base):
    __tablename__ = "items"
    item_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_common = Column(Boolean, default=False)
    status = Column(Enum("active", "retired", "lost"), default="active")
    last_assigned = Column(DateTime, default=datetime.utcnow)

    # Many-to-many relationship with Employee through EmployeeItem
    employees = relationship("EmployeeItem", back_populates="item")
    # Dynamic attributes for items
    attributes = relationship("ItemAttribute", back_populates="item")

# EmployeeItem Model (Associative Table)
class EmployeeItem(Base):
    __tablename__ = "employee_items"
    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(String, ForeignKey("employees.emp_id"))
    item_id = Column(Integer, ForeignKey("items.item_id"))
    unique_key = Column(String, nullable=True)
    date_assigned = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    # Many-to-one relationships with Employee and Item
    employee = relationship("Employee", back_populates="items")
    item = relationship("Item", back_populates="employees")

#Item Attribut Model for dynamic item properties
class ItemAttribute(Base):
    __tablename__ = "item_attributes"
    attribute_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"))
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)

    # Many-to-one relationship with Item
    item = relationship("Item", back_populates="attributes")

# User Model (System Manager)
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="manager")

# Log Model (For Action Logging)
class Log(Base):
    __tablename__ = "logs"
    log_id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.user_id"))

# ItemTransferHistory Model
class ItemTransferHistory(Base):
    __tablename__ = "item_transfer_history"
    transfer_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"))
    from_emp_id = Column(String, ForeignKey("employees.emp_id"))
    to_emp_id = Column(String, ForeignKey("employees.emp_id"))
    transfer_date = Column(Date, default=datetime.utcnow)
    notes = Column(Text)

    # Relationships to track item and employees
    item = relationship("Item")
    from_employee = relationship("Employee", foreign_keys=[from_emp_id])
    to_employee = relationship("Employee", foreign_keys=[to_emp_id])
