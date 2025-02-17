from aio_pika import connect, Message, ExchangeType, DeliveryMode 
import logging 
import src.logger

logger = logging.getLogger(__name__) 


async def send_message(message: str, routing_key: str) -> None: 
    connection = await connect("amqp://guest:guest@localhost/")
    async with connection: 
        channel = await connection.channel() 

        # Declare exchange
        echonet_exchange = await channel.declare_exchange(
            "echonet_exchange", ExchangeType.DIRECT
        )

        # Generate message_body
        message_body = Message(message.encode(), delivery_mode=DeliveryMode.PERSISTENT)

        # Send 
        await echonet_exchange.publish(message_body, routing_key=routing_key)

        logger.info("Email was send: %s" % message)
