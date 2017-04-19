import random,time
enemy=[] #x,y
coord=200
for i in range(1000000):
	enemy.append([random.randrange(coord),random.randrange(coord)])
x=random.randrange(coord)
y=random.randrange(coord)
print('x:'+str(x)+' y:'+str(y))

#fastest!
timer=time.time()
enemy_index4=enemy.index([x,y])
print(time.time()-timer)
print(enemy_index4)

timer=time.time()
enemy_index=[enemy.index(i) for i in enemy if i[0]==x and i[1]==y][0]
print(time.time()-timer)
print(enemy_index)

#fastest!
timer=time.time()
for i in enemy:
	if i[0]==x and i[1]==y:
		enemy_index2=enemy.index(i)
		break
print(time.time()-timer)
print(enemy_index2)

timer=time.time()
for i in range(len(enemy)):
	if enemy[i][0]==x and enemy[i][1]==y:
		enemy_index3=i
		break
print(time.time()-timer)
print(enemy_index3)

#fastest!
timer=time.time()
enemy_index4=next(enemy.index(i) for i in enemy if i[0]==x and i[1]==y)
print(time.time()-timer)
print(enemy_index4)

timer=time.time()
enemy_index5=filter(lambda i: True if i[0]==x and i[1]==y else False,enemy)
print(time.time()-timer)
print(type(enemy_index5))