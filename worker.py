import asyncio
import aio_pika
from sqlalchemy import update
from app.config import settings
from app.database import async_session
from app.links.models import Link
import json

async def process_click(message: aio_pika.IncomingMessage):
    async with message.process():
        body = message.body.decode()
        payload = json.loads(body)
        short_code = payload["short_code"]

        async with async_session() as session:
            stmt = update(Link).where(Link.short_code == short_code).values(
                click_count=Link.click_count + 1
            )
            await session.execute(stmt)
            await session.commit()
            print(f"[WORKER] click_count increased: {short_code}")

async def main():
    for attempt in range(15):
        try:
            print(f"[WORKER] RabbitMQ deneme {attempt + 1}/15...")
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            print("[WORKER] RabbitMQ connecttion successful")
            break
        except Exception as e:
            print(f"[WORKER] Başarısız: {e}")
            await asyncio.sleep(5)
    else:
        raise Exception("RabbitMQ connection error")

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue("click_events", durable=True)

    print("[WORKER] Listening queue")
    await queue.consume(process_click)
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())