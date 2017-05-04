#async game server
#port1 - for registration and authorization
#port2 - tick support
import asyncio
players=[]

def signin(user_pwd):
	global players
	name=user_pwd['name']
	pwd=user_pwd['pwd']
	result='new'
	for i in range(len(players)):
		if players[i]['name']==name:
			if players[i]['pwd']==pwd:
				print('player already registered')
				result='old'
				break
			else:
				print('incorrect password')
				result='error'
				break
	if result=='new':
		print('new player registered')
		players.append({'name':name,'pwd':pwd})
	return result



async def handle_tcp_name(reader, writer):
    print('Connection from {}'.format(writer.get_extra_info('peername')))

    while True:
    	#read to EOF
        data = await reader.read() #https://docs.python.org/3/library/asyncio-stream.html
        if data:
            message = data.decode()
            print("Getting data: {!r}".format(message), type(message))
            d=eval(message) #convert message to dictionary
            #print(type(d),d)
            if d['name'] and d['pwd']: #server get player name and password
            	result=signin(d)
            	message_to_client={'result':result}
            	writer.write(str(message_to_client).encode())
            
            writer.write_eof()
            print('sending data')
            print(players)
            await writer.drain()
        else:
            print("Terminating connection")
            writer.close()
            break


# start server cicle
if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.run_until_complete(
        asyncio.ensure_future(
            asyncio.start_server(handle_tcp_name, '127.0.0.1', 7777),
            loop=loop
        )
    )

    loop.run_forever()
