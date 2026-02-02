from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, Column
from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Float, JSON, Text

# --- Associations ---
class UserKnowledgeBaseLink(SQLModel, table=True):
    __tablename__ = "user_knowledge_base_links"
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", primary_key=True)
    knowledge_base_id: Optional[int] = Field(default=None, foreign_key="knowledge_bases.id", primary_key=True)

# --- Knowledge (RAG) ---
class KnowledgeBase(SQLModel, table=True):
    __tablename__ = "knowledge_bases"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    users: List["User"] = Relationship(back_populates="knowledge_bases", link_model=UserKnowledgeBaseLink)
    documents: List["Document"] = Relationship(back_populates="knowledge_base")

# --- Auth ---
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    status: str = Field(default="active")
    role: str = Field(default="user") # 'admin' or 'user'
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    verification_code: Optional[str] = None
    reset_token: Optional[str] = None
    reset_token_expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    folders: List["Folder"] = Relationship(back_populates="user")
    documents: List["Document"] = Relationship(back_populates="user")
    chat_sessions: List["ChatSession"] = Relationship(back_populates="user")
    knowledge_bases: List["KnowledgeBase"] = Relationship(back_populates="users", link_model=UserKnowledgeBaseLink)

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
    user_id: int = Field(foreign_key="users.id") # Uploader
    knowledge_base_id: Optional[int] = Field(default=None, foreign_key="knowledge_bases.id") # RAG Group
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="documents")
    folder: Optional[Folder] = Relationship(back_populates="documents")
    knowledge_base: Optional[KnowledgeBase] = Relationship(back_populates="documents")
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
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="chat_sessions")
    messages: List["ChatMessage"] = Relationship(back_populates="session")

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id")
    role: str # user / ai
    content: str
    used_sources: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    reasoning_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON)) # For Deep Agent steps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    session: ChatSession = Relationship(back_populates="messages")

# --- Token Usage Tracking ---
class TokenUsage(SQLModel, table=True):
    __tablename__ = "token_usage"
    id: Optional[int] = Field(default=None, primary_key=True)
    hour: datetime = Field(index=True)  # Truncated to hour 
    source: str  # 'retriever' or 'groq'
    tokens: int = Field(default=0)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserLog(SQLModel, table=True):
    __tablename__ = "user_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    event: str # 'LOGIN', 'LOGOUT', 'TOKEN_USAGE', 'ERROR'
    details: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship()

class ErrorLog(SQLModel, table=True):
    __tablename__ = "error_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    path: Optional[str] = None
    method: Optional[str] = None
    error_message: str
    stack_trace: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship()
