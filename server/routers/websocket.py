import redis
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.websocket("/ws/auctions/{auction_id}")
async def auction_ws(websocket: WebSocket, auction_id: int):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    pubsub.subscribe(f"auction_{auction_id}_bids")

    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message:
                await websocket.send_text(message['data'].decode())
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pubsub.unsubscribe()
        return