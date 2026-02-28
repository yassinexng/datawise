from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, Index, text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# User model for authentication and profile management
class User(Base):
    __tablename__ = "users"
    
    username = Column(String(50), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    is_verified = Column(Integer, server_default=text("0"))
    code_verification = Column(String(6), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(username)) > 0", name="username_not_empty"),
        CheckConstraint("LENGTH(TRIM(email)) > 0", name="email_not_empty"),
        CheckConstraint("LENGTH(TRIM(password_hash)) > 0", name="password_not_empty"),
    )
    
    email_verifications = relationship("EmailVerification", back_populates="user", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="user", cascade="all, delete-orphan")

# Email verification tracking for user accounts
class EmailVerification(Base):
    __tablename__ = "email_verifications"
    
    username = Column(String(50), ForeignKey("users.username", ondelete="CASCADE"), primary_key=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    attempts = Column(Integer, server_default=text("0"))
    verified_at = Column(DateTime(timezone=True))
    
    user = relationship("User", back_populates="email_verifications")

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(512), unique=True)
    status = Column(String(50), server_default=text("'pending'"))
    row_count = Column(Integer)
    column_count = Column(Integer)
    file_size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(name)) > 0", name="dataset_name_not_empty"),
        Index("idx_datasets_username", "username"),
        Index("idx_datasets_status", "status"),
    )
    
    user = relationship("User", back_populates="datasets")
