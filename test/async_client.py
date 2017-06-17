import asyncio
import time
#from base64 import b64decode

port=7777
port2=7778 #7778 for 2 simultanious servers

def run_in_foreground(task, *, loop=None):
    """Runs event loop in current thread until the given task completes

    Returns the result of the task.
    For more complex conditions, combine with asyncio.wait()
    To include a timeout, combine with asyncio.wait_for()
    """
    if loop is None:
        loop = asyncio.get_event_loop()
    return loop.run_until_complete(asyncio.ensure_future(task, loop=loop))

async def tcp_echo_client(message, port, loop=None):
    reader, writer = await asyncio.open_connection('127.0.0.1', port,
                                                        loop=loop)
    #newmessage=message+'port:'+str(port)
    print('-> Client sending: %r' % message)
    writer.write(str(message).encode())
    writer.write_eof()
    data = (await reader.read()).decode()
    print('<- Client received: %r' % data)
    print('-- Terminating connection on client')
    writer.close()
    return eval(data)

async def tcp_echo_client2(message, port, loop=None):
    reader, writer = await asyncio.open_connection('127.0.0.1', port,
                                                        loop=loop)
    #newmessage=message+'port:'+str(port)
    i=message['data']
    while i>0:
	    print('-> Client sending: %r' % message)
	    writer.write(str(message).encode())
	    writer.write_eof()
	    data = (await reader.read()).decode()
	    print('<- Client received: %r' % data)
	    i-=1
	    message['data']=i
	    time.sleep(1)
    print('-- Terminating connection on client')
    writer.close()
    return eval(data)


#run client
#1. sign in/ sign up - take session digest
while True:
	while True:
		name = input('Input you name: ')
		pwd =  input('Input you password: ')
		if name!='' and pwd!='': break
		print('incorrect name or password')
	message_to_server={}
	message_to_server['name']=name
	message_to_server['pwd']=pwd

	result=run_in_foreground(tcp_echo_client(message_to_server, port))
	print(type(result), result)
	if result['result']!='error':
		digest=result['digest']
		print(digest)
		break

timer=time.time()
while True:
	message_to_server={'command':'tick','data':10,'digest':digest}
	result=run_in_foreground(tcp_echo_client(message_to_server, port))
	delta=result['result']-timer
	timer=result['result']
	print(timer,delta)
	#print(type(result), result, 'tick:', result['result'])


#print(run_in_foreground(tcp_echo_client('Hello World2!', port2)))

#two clients in parallel
'''
def schedule_coroutine(target, *, loop=None):
    """Schedules target coroutine in the given event loop

    If not given, *loop* defaults to the current thread's event loop

    Returns the scheduled task.
    """
    if asyncio.iscoroutine(target):
        return asyncio.ensure_future(target, loop=loop)
    raise TypeError("target must be a coroutine, "
                    "not {!r}".format(type(target)))
'''
'''
count=10
messages=[]
for i in range(count):
	messages.append(schedule_coroutine(tcp_echo_client(str(i), port)))
	messages.append(schedule_coroutine(tcp_echo_client(str(i), port2)))
run_in_foreground(asyncio.wait(messages))
'''

'''
echo1 = schedule_coroutine(tcp_echo_client('Hello World3!', port))
echo2 = schedule_coroutine(tcp_echo_client('Hello World4!', port2))
run_in_foreground(asyncio.wait([echo1, echo2]))
print(echo1.result())
print(echo2.result())
'''