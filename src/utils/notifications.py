from src.models.enums import NotificationStatus
from src.broker.send import send_message


class SendNotifications: 
    @staticmethod
    async def send_new_post_notification(follower_ids: list[int], username: str) -> None: 
        message = f"{username} has uploaded a new post!"
        for follower_id in follower_ids:
            await send_message(f"{follower_id}:{NotificationStatus.NewPost.value}:{message}", "notification")

    @staticmethod
    async def send_liked_post_notification(username: str, post_user_id: int) -> None:
        message = f"{username} liked your post!"
        await send_message(f"{post_user_id}:{NotificationStatus.LikedPost.value}:{message}", "notification")
    
    @staticmethod 
    async def send_comment_added_notification(username: str, post_user_id: int) -> None: 
        message = f"{username} write a comment!"
        await send_message(f"{post_user_id}:{NotificationStatus.NewComment.value}:{message}", "notification") 

    @staticmethod 
    async def send_comment_liked_notification(username: str, comment: str , comment_user_id: int) -> None: 
        message = f"{username} liked your comment({comment})!"
        await send_message(f"{comment_user_id}:{NotificationStatus.LikedComment.value}:{message}", "notification")

    @staticmethod 
    async def send_following_notification(username: str, followed_id: int) -> None: 
        message = f"{username} start following on you!"
        await send_message(f"{followed_id}:{NotificationStatus.Followed.value}:{message}", "notification")
