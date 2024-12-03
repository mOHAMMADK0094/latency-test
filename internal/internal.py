import os
import uvicorn
from fastapi import FastAPI, WebSocket
import pg_test
import redis_test as rtest
import nats_test as ntest
import json


async def redis_test(redishost:str, portnumber:int, keyname:str , keyvalue:str) -> dict:
    return rtest.RedisTest(redishost,portnumber,keyname,keyvalue)


async def nats_test(natshost:str, portnumber:str, subkey:str, message:str) -> dict:
    return await ntest.NatsTest(natshost,portnumber,subkey,message)


async def postgres_test() -> dict:
    return pg_test.run()


app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

@app.get("/")
def read_root():
    return {"healthy": 1}


@app.websocket("/latency-test")
async def latency_test(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    if data == "8d5c8261-07b1-49b3-96e3-1d8bdfb98234":
        redis_time = await redis_test(os.environ.get('REDIS_HOST','127.0.0.1'), int(os.environ.get('REDIS_PORT',6379)), "LATENCYTEST", "testRedis")
        nats_time = await nats_test(os.environ.get('NATS_HOST','127.0.0.1'), os.environ.get('NATS_PORT','4222'), "LATENCYTEST", "testNats")
        portgres_time = await postgres_test()
        _rDict = {"redistime": redis_time, "natstime": nats_time, "postgrestime": portgres_time}
        responseDict = json.dumps(_rDict)
        await websocket.send_text(responseDict)
    else:
        await websocket.close()


try:
    pg_test.create_tables()
except:
    pass
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
