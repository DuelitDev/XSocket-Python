from XSocket import *
from XSocket.protocol.inet import *
import asyncio
import traceback


async def main():
    await server.run()
    while True:
        msg = await asyncio.get_running_loop().run_in_executor(
            None, func=lambda: input(">>> "))
        await server.broadcast_string(msg)


server = Server(XTCPListener(IPAddressInfo("127.0.0.1", 8000)))
server.event.on_open += lambda sender, e: print("Server open")
@server.event.on_accept.register
async def on_accept(sender, e):
    print("Client connected")
    e.client.event.on_message += lambda sender, e: print(e.data.decode("utf-8"))
    e.client.event.on_close += lambda sender, e: print("Client closed")
    e.client.event.on_error += lambda sender, e: print(traceback.format_exc())
server.event.on_close += lambda sender, e: print("Server closed")
server.event.on_error += lambda sender, e: print(traceback.format_exc())


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.run_forever()
