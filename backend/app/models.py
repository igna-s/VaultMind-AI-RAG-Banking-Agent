from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship, Column
from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Float

# --- Auth ---
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    
    conversations: List["Conversation"] = Relationship(back_populates="user")
    documents: List["Document"] = Relationship(back_populates="user")

# --- Chat ---
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(default="New Chat")
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    role: str # user / assistant
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    conversation: Conversation = Relationship(back_populates="messages")

# --- RAG ---
class Document(SQLModel, table=True):
    __tablename__ = "documents"
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    user_id: int = Field(foreign_key="users.id")
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_type: str = Field(default="temp") # 'group' or 'temp'
    
    user: User = Relationship(back_populates="documents")
    chunks: List["DocumentChunk"] = Relationship(back_populates="document")

class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id")
    content: str
    # Vector Column: Voyage-3-lite uses 512 dimensions (check docs, usually 1024 or 512, let's assume 512 for now or generic).
    # Actual Voyage-3-lite dimension: 512.
    embedding: List[float] = Field(sa_column=Column(Vector(512)))
    
    document: Document = Relationship(back_populates="chunks")
