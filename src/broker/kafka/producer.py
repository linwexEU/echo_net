from kafka import KafkaProducer
from src.config import settings
import json 


class KafkaProducerClient: 
    def __init__(self, topic: str): 
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=f"{settings.BOOTSTRAP_SERVER_HOST}:{settings.BOOTSTRAP_PORT}",
            value_serializer=self.value_serializer
        )

    @staticmethod 
    def value_serializer(value: dict | None) -> bytes: 
        if not value: 
            return json.dumps({}).encode("utf-8")
        return json.dumps(value).encode("utf-8")

    def send_message(self, message: dict) -> None: 
        self.producer.send(self.topic, message) 
        self.producer.flush() 

    def close(self) -> None: 
        self.producer.close() 

    def __enter__(self) -> "KafkaProducerClient": 
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None: 
        return self.close()

