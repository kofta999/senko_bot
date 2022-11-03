import asyncio
import motor.motor_asyncio

async def get_server_info():

    # replace this with your MongoDB connection string
    conn_str = "mongodb+srv://kofta:kokoko555@senko-cluster.6prehi1.mongodb.net/?retryWrites=true&w=majority"

    # set a 5-second connection timeout
    client = motor.motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)

    print(await client.server_info())

loop = asyncio.get_event_loop()
loop.run_until_complete(get_server_info())