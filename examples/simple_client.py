from XSocket import *
from XSocket.protocol.inet import *
import asyncio
import traceback


async def main():
    await client.run()
    while True:
        msg = await asyncio.get_running_loop().run_in_executor(
            None, func=lambda: input(">>> "))
        await client.send_string(msg)


client = Client(XTCPListener(IPAddressInfo("127.0.0.1", 8000)))
client.event.on_open += lambda sender, e: print("Client open")
client.event.on_message += lambda sender, e: print(e.data.decode("utf-8"))
client.event.on_close += lambda sender, e: print("Client closed")
client.event.on_error += lambda sender, e: print(traceback.format_exc())


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.run_forever()
