import asyncio
import logging
from kafka import KafkaConsumer 
from src.schemas.notifications import AddNotificationsToDb
from src.repositories.notifications import NotificationsRepository
from src.services.notifications import NotificationsService
from src.email.send_email import send_email_about_password_reset
from src.config import settings
import src.logger
import json 
import sys


class KafkaConsumerClient: 
    def __init__(self, topic: str): 
        self.topic = topic
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=f"{settings.BOOTSTRAP_SERVER_HOST}:{settings.BOOTSTRAP_PORT}", 
            auto_offset_reset="latest", 
            enable_auto_commit=True, 
            value_deserializer=self.json_deserializer
        )

        self.notification_service: NotificationsService = NotificationsService(NotificationsRepository)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def json_deserializer(value: bytes) -> dict: 
        if not value: 
            return {} 
        return json.loads(value.decode("utf-8"))
    
    async def consume_message(self): 
        for message in self.consumer:
            self.logger.info("kafka start consuming...") 
            match self.topic: 
                case settings.EMAIL_TOPIC:
                    self.logger.info(f"Receive email({message.value['user_email']}) for password change with pin code({str(message.value['pin_code'])[:3]}***)...")
                    
                    send_email_about_password_reset(message.value["user_email"], message.value["support_email"], message.value["pin_code"], 
                                                    message.value["ip"], message.value["device"], message.value["browser"])
                case settings.NOTIFICATION_TOPIC: 
                    self.logger.info(f"Receive Notification('{message.value['message']}') for User({message.value['entity_id']})")
                    
                    await self.notification_service.add(
                        AddNotificationsToDb(
                            user_id=message.value["entity_id"], 
                            status=message.value["status"], 
                            message=message.value["message"]
                        )
                    )


    def close(self): 
        self.consumer.close() 

    async def __aenter__(self) -> "KafkaConsumerClient": 
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: 
        self.close() 


async def run_consumer() -> None: 
    topic_name = sys.argv[1:][0]
    async with KafkaConsumerClient(topic_name) as consumer: 
        await consumer.consume_message() 


if __name__ == "__main__": 
    asyncio.run(run_consumer())
