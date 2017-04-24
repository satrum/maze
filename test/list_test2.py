import random,time
count=200
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

######### generator:
mygenerator = (x*x for x in range(10))
for i in mygenerator:
	print(i)

def createGenerator():
	mylist = range(3)
	for i in mylist:
		yield i*i

for i in createGenerator():
	print(i)

#args
def f(a,L=[]):
    L.append(a)
    return L
print(f(1))
print(f(2))
print(f(3))

def cheeseshop(kind, *args, **keywords):
    print("-- Do you have any", kind, "?")
    print("-- I'm sorry, we're all out of", kind)
    for arg in args:
        print(arg)
    print("-" * 40)
    for kw in keywords:
        print(kw, ":", keywords[kw])

cheeseshop("Limburger", "It's very runny, sir.",
           "It's really very, VERY runny, sir.",
           shopkeeper="Michael Palin",
           client="John Cleese",
           sketch="Cheese Shop Sketch")

pairs = [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')]
pairs.sort(key=lambda i: i[1])
print(pairs)

def my_function():
	'''Do nothing, but document it.
No, really, it doesn't do anything.'''
	pass
print(my_function.__doc__)