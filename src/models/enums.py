from enum import Enum 


class NotificationsState(Enum): 
    New = "New"
    Read = "Read"


class NotificationStatus(Enum): 
    Followed = "Followed" 
    LikedPost = "LikedPost"
    NewComment = "NewComment"
    LikedComment = "LikedComment" 
    NewPost = "NewPost"
    Report = "Report" 
