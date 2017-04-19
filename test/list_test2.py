import random,time
count=1000
maze=[ [random.randrange(100) for i in range(count)] for j in range(count)]
#print (maze)

stream=0
timer=time.time()
for x in range(1,count-1):
	for y in range(1,count-1):
		stream+=maze[y][x]
print(time.time()-timer)
print(stream)

stream=0
timer=time.time()
for y in range(1,count-1):
	for x in range(1,count-1):
		stream+=maze[y][x]
print(time.time()-timer)
print(stream)