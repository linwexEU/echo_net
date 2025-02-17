from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, TIMESTAMP, Enum
from datetime import datetime, timezone
from src.models.enums import NotificationStatus, NotificationsState
from src.db.db import Base


class Users(Base): 
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True) 
    username: Mapped[str] = mapped_column(nullable=False) 
    icon: Mapped[bytes] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True) 
    hashed_password: Mapped[str] = mapped_column(nullable=False) 

    bio: Mapped[str] = mapped_column(nullable=True) 
    report_count: Mapped[int] = mapped_column(default=0)

    post = relationship("Posts", back_populates="user")
    followers = relationship("Followers", back_populates="followed_user", foreign_keys="[Followers.followed_id]")
    following = relationship("Followers", back_populates="follower_user", foreign_keys="[Followers.follower_id]")


class ReportedUser(Base): 
    __tablename__ = "reported_user"

    id: Mapped[int] = mapped_column(primary_key=True)

    reporter_id: Mapped[int] = mapped_column(nullable=False) 
    user_id: Mapped[int] = mapped_column(nullable=False)


class PasswordReset(Base): 
    __tablename__ = "password_reset"

    id: Mapped[int] = mapped_column(primary_key=True) 
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    pin_code: Mapped[int] = mapped_column(nullable=False) 

    create_date_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    applied_date_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True) 


class Posts(Base): 
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True) 
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(nullable=False) 
    description: Mapped[str] = mapped_column(nullable=True) 
    file: Mapped[bytes] = mapped_column(nullable=False)
    likes: Mapped[int] = mapped_column(default=0)

    user = relationship("Users", back_populates="post")
    comments = relationship("Comments", back_populates="post")


class Bookmarks(Base): 
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True) 

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False) 
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False) 


class Comments(Base): 
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True) 
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False) 
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False) 

    text: Mapped[str] = mapped_column(nullable=False) 
    likes: Mapped[int] = mapped_column(default=0)

    post = relationship("Posts", back_populates="comments")


class Followers(Base): 
    __tablename__ = "followers"

    id: Mapped[int] = mapped_column(primary_key=True) 

    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False) 
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False) 
    
    followed_user = relationship("Users", foreign_keys=[followed_id], back_populates="followers")
    follower_user = relationship("Users", foreign_keys=[follower_id], back_populates="following")


class LikedPosts(Base): 
    __tablename__ = "liked_posts"

    id: Mapped[int] = mapped_column(primary_key=True) 

    user_id: Mapped[int] = mapped_column(nullable=False) 
    post_id: Mapped[int] = mapped_column(nullable=False)


class LikedComments(Base): 
    __tablename__ = "liked_comments"

    id: Mapped[int] = mapped_column(primary_key=True) 

    user_id: Mapped[int] = mapped_column(nullable=False) 
    comment_id: Mapped[int] = mapped_column(nullable=False) 


class Notifications(Base): 
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True) 
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False) 

    state: Mapped[NotificationsState] = mapped_column(Enum(NotificationsState), default=NotificationsState.New)
    status: Mapped[NotificationStatus] = mapped_column(Enum(NotificationStatus), nullable=False) 

    message: Mapped[str] = mapped_column(nullable=False)

    create_date_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    delete_date_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)



class IpDefender(Base): 
    __tablename__ = "ip_defender"

    id: Mapped[int] = mapped_column(primary_key=True)

    ip: Mapped[str] = mapped_column(nullable=False) 
    attempt: Mapped[int] = mapped_column(default=2) 

    create_date_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    applied_date_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True) 
