import redis
import time


def RedisTest(redishost:str, portnumber:int, keyname:str , keyvalue:str) -> dict:
    '''
        Sets a key in redis and gets it's value then returns the time spent for this operation.
            Parameters:
                    redishost (str): IP address of redis host.
                    portnumber (int): Redis server port number.
                    keyname (str): The key's name to created.
                    keyvalue (str): The value of the key.

            Returns:
                    cpuTimespent (dict): The time used by cpu
    '''
    startTime=time.perf_counter()
    r = redis.Redis(host=redishost, port=portnumber, socket_connect_timeout=1)
    r.set("networklatency:"+keyname, keyvalue)
    endConnectTime=time.perf_counter()
    rvalue = r.get("networklatency:"+keyname)
    r.delete("networklatency:"+keyname)
    r.close()
    endTime=time.perf_counter()

    if rvalue != bytes(keyvalue,'utf-8'):
        return -1
    return {"totalTime": endTime-startTime, "connTime": endConnectTime-startTime}
    

if __name__ == '__main__':
    pass
