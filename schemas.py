"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Core app schemas for the trading community

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    username: str = Field(..., min_length=3, max_length=32, description="Unique username")
    password_hash: str = Field(..., description="Hashed password (bcrypt)")
    role: str = Field("member", description="Role: member | admin")
    is_active: bool = Field(True, description="Whether user is active")

class Article(BaseModel):
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = []
    published_at: Optional[datetime] = None

class Indicator(BaseModel):
    name: str
    description: Optional[str] = None
    settings: dict = {}

class Message(BaseModel):
    user: str
    text: str
    room: str = "general"

class LibraryItem(BaseModel):
    title: str
    type: str = Field(..., description="ebook | pdf | video | course | link")
    url: Optional[str] = None
    description: Optional[str] = None

class CalendarEvent(BaseModel):
    title: str
    start: datetime
    end: Optional[datetime] = None
    source: Optional[str] = None

class Earning(BaseModel):
    symbol: str
    date: datetime
    est_eps: Optional[float] = None
    act_eps: Optional[float] = None

class SupportTicket(BaseModel):
    user: str
    subject: str
    message: str
    status: str = "open"

# Example schemas kept for reference (not used by app UI)
class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
