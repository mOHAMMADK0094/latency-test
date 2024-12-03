import time
import http.client
import json
from prometheus_client import Gauge, CONTENT_TYPE_LATEST, generate_latest
from fastapi import FastAPI ,Response
import uvicorn
import websockets
import json
from icmplib import ping
import os
import socket
import logging


DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK','/api/webhooks/ABCD1234') 
M_INSTANCE = os.environ.get('M_INSTANCE','LOCAL')
TEST_HOST = os.environ.get('TEST_HOST','127.0.0.1')
TEST_HOST_PORT = os.environ.get('TEST_HOST_PORT',8000)

logging.basicConfig(filename='./logs/app.log', level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

# Create Prometheus metrics
redis_metric = Gauge('redis_metric', 'Redis metric description', ['type'])
nats_metric = Gauge('nats_metric', 'Nats metric description', ['type'])
postgres_metric = Gauge('postgres_metric', 'Postgres metric description', ['type'])
connection_time = Gauge('connection_time', 'Total connection time')
ping_time = Gauge('ping_time', 'Ping time', ['type'])
tcp_time = Gauge('tcp_time', 'TCP connection time')


def send_discord_message(discordMessage):
    message = {
    "content": discordMessage
    }
    payload = json.dumps(message)
    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(len(payload))
    }

    conn = http.client.HTTPSConnection("discord.com")
    conn.request("POST", DISCORD_WEBHOOK, body=payload, headers=headers)

    response = conn.getresponse()
    if response.status == 204:
        return 0
    else:
        print("Failed to send message. Status code:", response.status)
        time.sleep(10)
        send_discord_message(discordMessage,DISCORD_WEBHOOK)


def host_up(hostName:str) -> int:
    start_time = time.perf_counter()
    #FIXME: Change count & interval as you like but pay attention
    #the more time you spend on ping the more time you must set for prometheus scrape_timeout
    host = ping(hostName, count=3, interval=0.1, privileged=False)
    end_time = time.perf_counter()
    return {"time": end_time - start_time, "packetLoss": host.packet_loss, "maxRTT": host.max_rtt ,"jitter": host.jitter}


def test_tcp_connection(host, port):
    start_time = time.perf_counter()    
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            end_time = time.perf_counter()
            return end_time - start_time
    except ConnectionRefusedError:
        logging.error("TCP Connection refused, server not available")
        send_discord_message(M_INSTANCE + ": TCP Connection refused, server not available")
        return -1
    except socket.timeout:
        logging.error("TCP Connection timed out")
        send_discord_message(M_INSTANCE + ": TCP Connection timed out")
        return -1
    except OSError as e:
        logging.error("TCP Connection error:" + str(e))
        send_discord_message(M_INSTANCE + ": TCP Connection error:" + str(e))
        return -1


@app.get("/")
async def read_root():
    return {"healthy": 1}


@app.get("/metrics")
async def metrics():

    pingTime=host_up(TEST_HOST)
    ping_time.labels('total').set(pingTime['time'])
    ping_time.labels('packetloss').set(pingTime['packetLoss'])
    ping_time.labels('maxrtt').set(pingTime['maxRTT'])
    ping_time.labels('jitter').set(pingTime['jitter'])

    tcpTime = test_tcp_connection(TEST_HOST, TEST_HOST_PORT)
    if tcpTime < 0:
        return -1

    tcp_time.set(tcpTime)

    # Starting websocket connection
    try:
        startTime = time.perf_counter()
        async with websockets.connect("ws://" + TEST_HOST + ":" + str(TEST_HOST_PORT) + "/latency-test") as websocket:
            endTime = time.perf_counter()
            await websocket.send("8d5c8261-07b1-49b3-96e3-1d8bdfb98234")
            response = await websocket.recv()
            await websocket.close()

        data = json.loads(response)

        connection_time.set(endTime - startTime)
        postgres_metric.labels('total').set(data['postgrestime']['totalTime'])
        postgres_metric.labels('insert').set(data['postgrestime']['insertTime'])
        postgres_metric.labels('select').set(data['postgrestime']['selectTime'])
        postgres_metric.labels('delete').set(data['postgrestime']['deleteTime'])
        redis_metric.labels('total').set(data['redistime']['totalTime'])
        redis_metric.labels('conn').set(data['redistime']['connTime'])
        nats_metric.labels('total').set(data['natstime']['totalTime'])
        nats_metric.labels('conn').set(data['natstime']['connTime'])

        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logging.error("Websocket or fetching metrics err: " + str(e))
        send_discord_message(M_INSTANCE + ": ERROR RUNNING TEST: " + str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8900)
