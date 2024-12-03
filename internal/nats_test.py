import nats
import time


async def NatsTest(natshost:str, portnumber:str, subkey:str, message:str) -> dict:
    '''
        Publishes a message to the Nats server and gets the message.
            Parameters:
                    natshost (str): IP address of nats host.
                    portnumber (int): Nats server port number.
                    subkey (str): Subscription key.
                    message (str): Message as `str`.

            Returns:
                    cpuTimespent (dict): The time used by cpu
    '''
    # Simple example provided by nats documents and i've just copy/pasted it here. 
    # https://nats-io.github.io/nats.py/
    startTime=time.perf_counter()
    
    server = "nats://" + natshost + ":" + portnumber

    nc = await nats.connect(server, connect_timeout=1, max_reconnect_attempts=1)
    endConnectTime=time.perf_counter()
    sub = await nc.subscribe(subkey)

    await nc.publish(subkey, bytes(message,'utf-8'))

    msg = await sub.next_msg()

    await nc.flush()
    await nc.close()
    endTime=time.perf_counter()

    if msg.subject != subkey and msg.data != bytes(message,'utf-8'):
        return -1
    return {"totalTime": endTime-startTime, "connTime": endConnectTime-startTime}


if __name__ == '__main__':
    pass
