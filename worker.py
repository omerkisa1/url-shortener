import asyncio
import aio_pika
from sqlalchemy import update
from app.config import settings
from app.database import async_session
from app.links.models import Link

async def process_click(message: aio_pika.IncomingMessage):
    async with message.process():
        short_code = message.body.decode()
        
        async with async_session() as session:
            stmt = update(Link).where(Link.short_code == short_code).values(
                click_count=Link.click_count + 1
            )
            await session.execute(stmt)
            await session.commit()
            print(f"[WORKER] click_count artırıldı: {short_code}")

async def main():
    for attempt in range(10):
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            break
        except Exception:
            await asyncio.sleep(3)
    else:
        raise Exception("RabbitMQ'ya bağlanılamadı")

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue("click_events", durable=True)

    await queue.consume(process_click)
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())