# app.models.py
# Import declarative_base and other necessary classes and functions from SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta

# Use declarative_base() to define your Base
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_username = Column(String(30), primary_key=True)
    user_email = Column(String(50), nullable=False)
    user_firstName = Column(String(30))
    user_lastName = Column(String(30))
    user_password = Column(String(50), nullable=False)
    user_lastActivity = Column(DateTime)
    user_status = Column(String(30))
    user_college = Column(String(100))
    user_major = Column(String(100))
    user_graduation = Column(String(30))
    user_classification = Column(String(30))

    # Define a one-to-many relationship with Task
    tasks = relationship("Task", back_populates="user")

is_searchable = Column(Boolean, default=True)  # Default to True, meaning profiles are searchable by default

class Task(Base):
    __tablename__ = 'Task'

    task_ID = Column(Integer, primary_key=True)
    task_description = Column(String(255))
    task_Notes = Column(String(8000))
    task_startDate = Column(Date)
    task_dueDate = Column(Date)
    task_timeEstimate = Column(Integer)
    task_Course = Column(String(50))

    # Define a many-to-one relationship with User
    user_username = Column(String(30), ForeignKey('users.user_username'))
    user = relationship("User", back_populates="tasks")

    # Define a property to calculate task priority based on due date
    @property
    def task_priority(self):
        if self.task_dueDate:
            today = datetime.now().date()
            days_until_due = (self.task_dueDate - today).days

            if days_until_due <= 1:  # Changed from 2 to 1 for "Critical" priority
                return "Critical"
            elif days_until_due <= 3:  # Changed from 7 to 3 for "High Priority"
                return "High Priority"
            elif days_until_due <= 7:
                return "Medium Priority"
        
        return "Low Priority"

class UserXTask(Base):
    __tablename__ = 'user_x_task'

    userxtask_ID = Column(Integer, primary_key=True)
    user_username = Column(String(30), ForeignKey('users.user_username'), nullable=False)
    task_ID = Column(Integer, ForeignKey('Task.task_ID'), nullable=False)

    # Define relationships with User and Task
    user = relationship("User", backref="user_x_task")
    task = relationship("Task", backref="user_x_task")

class TaskStatus(Base):
    __tablename__ = 'Task_Status'

    taskstatus_ID = Column(Integer, primary_key=True)
    taskstatus_description = Column(String(255))

class TaskPriority(Base):
    __tablename__ = 'Task_Priority'

    taskpriority_ID = Column(Integer, primary_key=True)
    taskpriority_description = Column(String(255))

