from src.repositories.users import UsersRepository 
from src.services.users import UsersService 

from src.services.ip_defender import IpDefenderService 
from src.repositories.ip_defender import IpDefenderRepository

from src.services.posts import PostsService 
from src.repositories.posts import PostsRepository

from src.services.liked_posts import LikedPostsService 
from src.repositories.liked_posts import LikedPostsRepository

from src.services.comments import CommentsService
from src.repositories.comments import CommentsRepository

from src.services.followers import FollowersService 
from src.repositories.followers import FollowersRepository

from src.services.password_reset import PasswordResetService 
from src.repositories.password_reset import PasswordResetRepository

from src.services.bookmarks import BookmarksService 
from src.repositories.bookmarks import BookmarksRepository

from src.services.liked_comments import LikedCommentsService 
from src.repositories.liked_comments import LikedCommentsRepository

from src.services.notifications import NotificationsService 
from src.repositories.notifications import NotificationsRepository

from src.services.reported_user import ReportedUserService 
from src.repositories.reported_user import ReportedUserRepository


def users_service(): 
    return UsersService(UsersRepository)


def ip_defender_service(): 
    return IpDefenderService(IpDefenderRepository)


def posts_service(): 
    return PostsService(PostsRepository)


def liked_post_service(): 
    return LikedPostsService(LikedPostsRepository)


def comments_service(): 
    return CommentsService(CommentsRepository)


def followers_service(): 
    return FollowersService(FollowersRepository)


def password_reset_service(): 
    return PasswordResetService(PasswordResetRepository)


def bookmarks_service(): 
    return BookmarksService(BookmarksRepository)


def liked_comments_service(): 
    return LikedCommentsService(LikedCommentsRepository)


def notifications_service(): 
    return NotificationsService(NotificationsRepository)


def reported_user_service(): 
    return ReportedUserService(ReportedUserRepository)
