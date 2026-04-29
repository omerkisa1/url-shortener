import asyncio
import aio_pika
from app.config import settings


rabbitmq_connection = None
rabbitmq_channel = None


async def init_rabbitmq():
    global rabbitmq_connection, rabbitmq_channel
    rabbitmq_connection = await aio_pika.robust_connection(settings.RABBITMQ_URL)
    rabbitmq_channel = await rabbitmq_connection.channel()
    await rabbitmq_channel.declare_queue("click_events", durable=True)

async def close_rabbitmq():
    global rabbitmq_connection
    if rabbitmq_connection:
        await rabbitmq_connection.close()

async def publish_click_events(short_code: str):
    await rabbitmq_channel.defaul_exchange.publish(
        
        aio_pika.Message(short_code.encode()),
        routing_key="click_events"

    )