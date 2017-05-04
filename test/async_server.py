import asyncio

def run_in_foreground(task, *, loop=None):
	"""Runs event loop in current thread until the given task completes

	Returns the result of the task.
	For more complex conditions, combine with asyncio.wait()
	To include a timeout, combine with asyncio.wait_for()
	"""
	if loop is None:
		loop = asyncio.get_event_loop()
	s = loop.run_until_complete(asyncio.ensure_future(task, loop=loop))
	
	return s

async def handle_tcp_echo(reader, writer):
	data = await reader.read(100)
	message = data.decode()
	addr = writer.get_extra_info('peername')
	print("-> Server received %r from %r" % (message, addr))
	print("<- Server sending: %r" % message)
	writer.write(data)
	await writer.drain()
	print("-- Terminating connection on server")
	writer.close()

'''
if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.run_until_complete(
        asyncio.ensure_future(
            asyncio.start_server(handle_tcp_echo, '127.0.0.1', 7777),
            loop=loop
        )
    )
    loop.run_forever()
'''

#commands:
#first server
make_server = asyncio.start_server(handle_tcp_echo, '127.0.0.1',7777)
server = run_in_foreground(make_server)

print(server.sockets[0])
port = server.sockets[0].getsockname()[1]
print(port)

#second server
make_server2 = asyncio.start_server(handle_tcp_echo, '127.0.0.1',7778)
server2 = run_in_foreground(make_server2)

print(server2.sockets[0])
port2 = server2.sockets[0].getsockname()[1]
print(port2)

#loop.run_forever()