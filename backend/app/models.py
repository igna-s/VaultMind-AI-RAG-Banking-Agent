from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, Column
from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Float, JSON

# --- Auth ---
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    status: str = Field(default="active")
    role: str = Field(default="user") # 'admin' or 'user'
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    folders: List["Folder"] = Relationship(back_populates="user")
    documents: List["Document"] = Relationship(back_populates="user")
    chat_sessions: List["ChatSession"] = Relationship(back_populates="user")

# --- Knowledge (RAG) ---
class Folder(SQLModel, table=True):
    __tablename__ = "folders"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    parent_folder_id: Optional[int] = Field(default=None, foreign_key="folders.id")
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="folders")
    parent_folder: Optional["Folder"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Folder.id"}, back_populates="subfolders"
    )
    subfolders: List["Folder"] = Relationship(back_populates="parent_folder")
    documents: List["Document"] = Relationship(back_populates="folder")

class Document(SQLModel, table=True):
    __tablename__ = "documents"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    type: Optional[str] = None
    path_url: Optional[str] = None
    folder_id: Optional[int] = Field(default=None, foreign_key="folders.id")
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="documents")
    folder: Optional[Folder] = Relationship(back_populates="documents")
    chunks: List["DocumentChunk"] = Relationship(back_populates="document")

class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id")
    content: str
    # Vector Column: Dimension 1024 for Voyage AI models (voyage-2, etc)
    embedding: List[float] = Field(sa_column=Column(Vector(1024)))
    chunk_index: Optional[int] = None
    chunk_metadata: Dict[str, Any] = Field(default={}, sa_column=Column("metadata", JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    document: Document = Relationship(back_populates="chunks")

# --- Chat (History) ---
class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str = Field(default="New Chat")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="chat_sessions")
    messages: List["ChatMessage"] = Relationship(back_populates="session")

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id")
    role: str # user / ai
    content: str
    used_sources: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    session: ChatSession = Relationship(back_populates="messages")
