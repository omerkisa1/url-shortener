import asyncio
import aio_pika
from app.config import settings


rabbitmq_connection = None
rabbitmq_channel = None


async def init_rabbitmq():
    for attempt in range(10):
        try:
            rabbitmq_connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            rabbitmq_channel = await rabbitmq_connection.channel()
            await rabbitmq_channel.declare_queue("click_events", durable=True)
            return
        except Exception:
            await asyncio.sleep(3)
    raise Exception("Couldn't connect to RabbitMQ")

async def close_rabbitmq():
    global rabbitmq_connection
    if rabbitmq_connection:
        await rabbitmq_connection.close()

async def publish_click_events(short_code: str):
    await rabbitmq_channel.defaul_exchange.publish(
        
        aio_pika.Message(short_code.encode()),
        routing_key="click_events"

    )