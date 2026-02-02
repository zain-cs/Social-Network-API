from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class UserWithStats(UserResponse):
    followers_count: int
    following_count: int
    posts_count: int


# Post Schemas
class PostBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    published: bool = True


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    published: Optional[bool] = None


class PostResponse(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    author_id: int
    author: UserResponse
    likes_count: int
    comments_count: int
    
    class Config:
        from_attributes = True


# Comment Schemas
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    post_id: int


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    author_id: int
    post_id: int
    author: UserResponse
    likes_count: int
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# Feed Schema
class FeedPost(PostResponse):
    is_liked_by_user: bool
    
    class Config:
        from_attributes = True