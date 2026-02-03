from datetime import datetime
from typing import Any, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Text
from sqlmodel import Column, Field, Relationship, SQLModel


# --- Associations ---
class UserKnowledgeBaseLink(SQLModel, table=True):
    __tablename__ = "user_knowledge_base_links"
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)
    knowledge_base_id: int | None = Field(default=None, foreign_key="knowledge_bases.id", primary_key=True)


# --- Knowledge (RAG) ---
class KnowledgeBase(SQLModel, table=True):
    __tablename__ = "knowledge_bases"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str | None = None
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    users: list["User"] = Relationship(back_populates="knowledge_bases", link_model=UserKnowledgeBaseLink)
    documents: list["Document"] = Relationship(back_populates="knowledge_base")


# --- Auth ---
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    status: str = Field(default="active")
    role: str = Field(default="user")  # 'admin' or 'user'
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    verification_code: str | None = None
    reset_token: str | None = None
    reset_token_expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    folders: list["Folder"] = Relationship(back_populates="user")
    documents: list["Document"] = Relationship(back_populates="user")
    chat_sessions: list["ChatSession"] = Relationship(back_populates="user")
    knowledge_bases: list["KnowledgeBase"] = Relationship(back_populates="users", link_model=UserKnowledgeBaseLink)


class Folder(SQLModel, table=True):
    __tablename__ = "folders"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    parent_folder_id: int | None = Field(default=None, foreign_key="folders.id")
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="folders")
    parent_folder: Optional["Folder"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Folder.id"}, back_populates="subfolders"
    )
    subfolders: list["Folder"] = Relationship(back_populates="parent_folder")
    documents: list["Document"] = Relationship(back_populates="folder")


class Document(SQLModel, table=True):
    __tablename__ = "documents"
    id: int | None = Field(default=None, primary_key=True)
    title: str
    type: str | None = None
    path_url: str | None = None
    folder_id: int | None = Field(default=None, foreign_key="folders.id")
    user_id: int = Field(foreign_key="users.id")  # Uploader
    knowledge_base_id: int | None = Field(default=None, foreign_key="knowledge_bases.id")  # RAG Group
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="documents")
    folder: Folder | None = Relationship(back_populates="documents")
    knowledge_base: KnowledgeBase | None = Relationship(back_populates="documents")
    chunks: list["DocumentChunk"] = Relationship(back_populates="document")


class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"
    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id")
    content: str
    # Vector Column: Dimension 1024 for Voyage AI models (voyage-2, etc)
    embedding: list[float] = Field(sa_column=Column(Vector(1024)))
    chunk_index: int | None = None
    chunk_metadata: dict[str, Any] = Field(default={}, sa_column=Column("metadata", JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    document: Document = Relationship(back_populates="chunks")


# --- Chat (History) ---
class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str = Field(default="New Chat")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="chat_sessions")
    messages: list["ChatMessage"] = Relationship(back_populates="session")


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id")
    role: str  # user / ai
    content: str
    used_sources: list[dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    reasoning_data: dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # For Deep Agent steps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    session: ChatSession = Relationship(back_populates="messages")


# --- Token Usage Tracking ---
class TokenUsage(SQLModel, table=True):
    __tablename__ = "token_usage"
    id: int | None = Field(default=None, primary_key=True)
    hour: datetime = Field(index=True)  # Truncated to hour
    source: str  # 'retriever' or 'groq'
    tokens: int = Field(default=0)
    user_id: int | None = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserLog(SQLModel, table=True):
    __tablename__ = "user_logs"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    event: str  # 'LOGIN', 'LOGOUT', 'TOKEN_USAGE', 'ERROR'
    details: dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    ip_address: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship()


class ErrorLog(SQLModel, table=True):
    __tablename__ = "error_logs"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id")
    path: str | None = None
    method: str | None = None
    error_message: str
    stack_trace: str | None = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User | None = Relationship()
