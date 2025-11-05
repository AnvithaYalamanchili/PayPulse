from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"
    guest = "guest"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    subscriptions = relationship("Subscription", back_populates="user")
    usage = relationship("Usage", back_populates="user")

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    features = Column(String)  # comma-separated features
    quota_limit = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    subscriptions = relationship("Subscription", back_populates="plan")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    status = Column(String)
    payment_id = Column(String, nullable=True)
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")

class Usage(Base):
    __tablename__ = "usage"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_type = Column(String)
    usage_count = Column(Integer, default=0)
    quota_limit = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="usage")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)  # e.g., success, failed, pending
    payment_gateway_id = Column(String)  # Stripe/PayPal ID
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    subscription = relationship("Subscription")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)       # e.g., "email", "SMS"
    message = Column(String)    # content of the notification
    status = Column(String)     # e.g., "sent", "failed", "pending"
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
