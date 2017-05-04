#https://xakep.ru/2017/01/11/python-3-asyncio/
#https://www.blazemeter.com/blog/how-load-test-tcp-protocol-services-jmeter
#C:\WORK\software\apache-jmeter-3.2\bin
import asyncio
# https://docs.python.org/3/library/asyncio-stream.html?highlight=asyncio.start_server#asyncio.start_server
# Streams (coroutine based API)
async def handle_tcp_echo(reader, writer):
    print('Connection from {}'.format(writer.get_extra_info('peername')))

    while True:
        data = await reader.read(100)
        #data = await reader.readuntil(separator=b'\n')
        if data:
            message = data.decode()
            print("Echoing back: {!r}".format(message))
            writer.write(data)
            await writer.drain()
        else:
            print("Terminating connection")
            writer.close()
            break

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.run_until_complete(
        asyncio.ensure_future(
            asyncio.start_server(handle_tcp_echo, '127.0.0.1', 7777),
            loop=loop
        )
    )
    loop.run_until_complete(
        asyncio.ensure_future(
            asyncio.start_server(handle_tcp_echo, '127.0.0.1', 7778),
            loop=loop
        )
    )
    loop.run_forever()