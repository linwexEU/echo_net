Alembic: 
alembic upgrade head 

Project run: 
uvicorn src.main:app --reload

Kafka email_topic run: 
python -m src.broker.kafka.consumer email_topic 

kafka notification_topic run: 
python -m src.broker.kafka.consumer notification_topic
