# turyev.roman@gmail.com
# generate 2D mazes
import pygame
import random
import time
import sys
import os

print('default recursion limit: '+str(sys.getrecursionlimit()))
sys.setrecursionlimit(1000000) #увеличить глубину возможной рекурсии для генерации больших либиринтов
print('new recursion limit:	 '+str(sys.getrecursionlimit()))

#константы цветов:
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
bright_red = (128,0,0)
bright_green = (0,128,0)
bright_blue = (0,0,128)

display_x=1500 #размер игрового поля по горизонтали
display_y=1000 #размер игрового поля по вертикали
info_height=100 #размер поля с инофрмацией по вертикали
display_y-=info_height #уменьшить размер игрового поля по вертикали на высоту поля с информацией
cellsize=100 #size of cell
zoomsize=[20,30,50,60,80,100] #разные размеры cellsize на разных режимах масштабирования, картинки образуют массивы с каждым размером
display_wall_tick=0 #мерцание (пока не используется)
font_def='timesnewroman'
#deep=1 #deep of blocks
#maze size:
grid_x=75 #min=75
if grid_x%2==0: grid_x-=1
grid_y=45 #min=45
if grid_y%2==0: grid_y-=1

maze_randomcicles=200 #value of random empty blocks
maze=[[]]
# 0 - empty
# 1 - block
# 2 - empty (removed block with random cicles) - не используется, теперь рандомные тоже 0
maze_fog=[[]]
FLAG_FOG=False #False for fog and True for always visible
FLAG_SCANNER=False #True for on, False - off
# 0 - not visible
# 1 - visible
maze_objects=[[]]
objects_oxygen=10
objects_energy=50
objects_movingblock=100
objects_health=5
objects_hole=100
# 0 - no objects
# 1 - block
# 2 - energy +50%
# 3 - oxygen +50%
# 4 - moving block
# 5 - enemy
# 6 - health +50%
# 7 - hole (яма, дыра, засасывающая кислород)
#На карте появляются враги(монстры), которые перемещаются, у них есть скорость, уровень агрессии, урон, здоровье.
objects_enemy=50
enemy_maxlevel=0
#убрать генерацию в функцию startobjects()
#enemy=[[] for i in range(objects_enemy)]
enemy_type=[
[0,0,10,0,0,0,5,2,False], #heal=5 damage=2 cooldown=10
[0,0,5 ,0,0,1,2,10,False], #heal=2 damage=10 cooldown=5
[0,0,20,0,0,2,4,10,False], #heal=4 damage=10 cooldown=20
[0,0,30,0,0,3,6,15,False] #heal=6 damage=15 cooldown=30
]
#0 - x
#1 - y
#2 - speed(10 act)
#3 - act(счетчик хода)
#4 - state(0 - случайное блуждание, 1 - от края до края, 2 - нападение, 3 - убегает, 4 - стоит)
#5 - type(тип врага)
#6 - здоровье
#7 - урон от столкновения
#8 - killed (False, True)
print ('cell size: '+str(cellsize))
print ('grid_x:	'+str(grid_x))
print ('grid_y:	'+str(grid_y))
print ('maze random cicles: '+str(maze_randomcicles))
print ('energy: '+str(objects_energy))
print ('oxygen: '+str(objects_oxygen))
print ('moving blocks: '+str(objects_movingblock))
print ('enemies: '+str(objects_enemy))
print ('enemies max level: '+str(enemy_maxlevel))
#print (len(enemy))
mazenumber=0 #count of maze generation
mazelevels=[
[21, 21, 10  ,0, 3 , 0   ,0  ,0,0 ,0,0], #0 easy test level, +energy
[51, 45, 100 ,5 ,20, 0   ,0  ,0,0 ,0,0], #1 medium test level, +oxygen
[75, 45, 200 ,10,40, 0   ,0  ,0,0 ,0,0], #2 medium level, energy+oxygen
[75, 45, 100 ,10,40, 100 ,0  ,0,0 ,0,0], #3 moving blocks
[75, 45, 200 ,10,50, 150 ,30 ,0,2 ,0,0], #4 enemie level 0
[75, 45, 150 ,10,50, 300 ,60 ,0,8 ,0,0], #5 more enemie level 0
[75, 75, 300 ,15,80, 200 ,90 ,1,8 ,0,0], #6 enemie level 1 75*75
[75, 75, 200 ,15,80, 400 ,120,1,8 ,0,0], #7 more enemie level 1 75*75
[101,101,500 ,0, 100,300 ,150,2,12,100,50],  #8 big level enemie level 1 101*101 holes and env_oxygen
[201,201,2000,50,400,2000,300,3,20,0,0]  #9 very big level enemie level 1 201*201 (после этого апгрейды 2 уровня можно сделать)
]
print(mazelevels)
#лабиринты задают параметры при увеличении mazenumber
#grid_x,grid_y,maze_randomcicles,objects_oxygen,objects_energy,objects_movingblock,objects_enemy,enemy_maxlevel,objects_health,objects_hole,concentration_oxygen
#пока нет, но надо:  oxygen env flag on/off (просчитывать ли вообще кислород или он в нуле), oxygen generator

#среды:
maze_oxygen=[[]] #кислород, концентрация
concentration_oxygen=100 #максимальная концентрация, используется для генерации в start_env(concentration)
env_speed={'OXYGEN':[50,0]} #шаги, через которые произойдет изменение концентрации и распространение среды в next_env(env_maze), первое значение - константа, второе - шаг

#player:
player_x=0
player_y=1
#массив для разных направлений игрока и врагов
directions={
'RIGHT': [1 , 0],
'LEFT' : [-1, 0],
'UP'   : [0 ,-1],
'DOWN' : [0 , 1]
}
player_direction='RIGHT' #направление взгляда игрока по умолчанию
#player statistics:
player_action={'MOVE':0,'FIRE':0,'FOG':0, 'PICK':0,'KILL':0} #player action counts. statistics
print('player x:',player_x,' player y:',player_y,' move:',player_action['MOVE'])
starttime=time.clock()
pausegame=False
player_expirience=0

#cooldown: для врагов смотреть в enemy_types
cooldown={'TICK':50,'MOVE':10,'MOVE BLOCK':15,'MOVE ON ENEMY':15}#default cooldown={'TICK':50,'MOVE':10,'MOVE BLOCK':15,'MOVE ON ENEMY':15}
#upgrades:
upgrades={
	'EXP':          [0,  4000,8000,16000], #сколько опыта уходит на апгрейд по каждому уровню, 0 уровень - значения характеристик по умолчанию
	'ENERGY_MAX':   [100,125, 150, 175],
	'OXYGEN_MAX':   [100,120, 140, 160],
	'HEALTH_MAX':   [100,125, 150, 175],
	'SPEED_TICK':   [0,  1,   2,   3], #на сколько сокращается cooldown по способностям игрока
	'FOG_RADIUS':   [2,  3,   4,   5],
	'MELEE_DAMAGE': [1,  2,   3,   4],
	'OXYGEN_TIME':  [0.6,0.5, 0.4, 0.3],
	'OXYGEN_ENERGY':[0.3,0.2, 0.1, 0.05] #затраты энергии при сборе внешнего кислорода
}
#player upgrades загружается при loadplayer() и сохраняется при saveplayer(), а так же gameover()
player_upgrades={
	'EXP':       0,
	'ENERGY_MAX':0,
	'OXYGEN_MAX':0,
	'HEALTH_MAX':0,
	'SPEED_TICK':0,
	'FOG_RADIUS':0,
	'MELEE_DAMAGE':0,
	'OXYGEN_TIME':0,
	'OXYGEN_ENERGY':0
} #первый - сумма сделанных апгрейдов, дальше как в upgrades 0,1,2
upgrade_name='' #нужно  для меню апгрейдов
player_energy=upgrades['ENERGY_MAX'][player_upgrades['ENERGY_MAX']]
player_oxygen=upgrades['OXYGEN_MAX'][player_upgrades['OXYGEN_MAX']]
player_heal  =upgrades['HEALTH_MAX'][player_upgrades['HEALTH_MAX']]
player_damage=upgrades['MELEE_DAMAGE'][player_upgrades['MELEE_DAMAGE']]
fog_radius   =upgrades['FOG_RADIUS'][player_upgrades['FOG_RADIUS']]
player_speed =upgrades['SPEED_TICK'][player_upgrades['SPEED_TICK']]
player_oxygen_time=upgrades['OXYGEN_TIME'][player_upgrades['OXYGEN_TIME']]
player_oxygen_energy=upgrades['OXYGEN_ENERGY'][player_upgrades['OXYGEN_ENERGY']]
print('upgraded player: ',player_energy, player_oxygen, player_heal, player_damage, fog_radius, player_speed, player_oxygen_time, player_oxygen_energy)


pygame.init()
# to get the true full-screen size, do this BEFORE pygame.display.set_mode:
fullscreen_sz = pygame.display.Info().current_w, pygame.display.Info().current_h
print( 'screen size =', fullscreen_sz )
#https://www.pygame.org/docs/ref/display.html#pygame.display.Info
#print(pygame.display.Info())
# initially center the pygame window by setting %SDL_VIDEO_WINDOW_POS%
win_pos_left = 1 + ((fullscreen_sz[0] - display_x) // 2)
win_pos_top = 1 + ((fullscreen_sz[1] - (display_y+info_height)) // 2)
#print(win_pos_left, win_pos_top)
os.environ['SDL_VIDEO_WINDOW_POS'] = '{0},{1}'.format(win_pos_left, win_pos_top)
# ----------------------------------------------------------------------------
gameDisplay = pygame.display.set_mode((display_x,display_y+info_height)) #pygame.FULLSCREEN, pygame.HWSURFACE
# ----------------------------------------------------------------------------
os.environ['SDL_VIDEO_WINDOW_POS'] = ''
# if you don't clear the environment variable, the window will reposition
# every time pygame.display.set_mode() gets called due to a VIDEORESIZE event.
# ----------------------------------------------------------------------------
gameDisplay.fill(white)
pygame.display.set_caption('лабиринт: дойди до конца, сброс - пробел')
clock = pygame.time.Clock()

#generate maze backpropagation:
def make_maze(w,h):
	vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
	newmaze=[[1 for x in range(w*2+1)] for y in range(h*2+1)] 
	for i in range(h):
		for j in range(w):
			newmaze[i*2+1][j*2+1]=0

	def walk(x, y):
		vis[y][x] = 1

		d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
		random.shuffle(d)
		for (xx, yy) in d:
			if vis[yy][xx]: continue
			if xx == x: 
				newmaze[max(y,yy)*2][x*2+1]=0
			if yy == y: 
				newmaze[y*2+1][max(x, xx)*2+1]=0
				newmaze[y*2+1][max(x, xx)*2]=0
			walk(xx, yy)

	walk(random.randrange(w), random.randrange(h))
	return newmaze

#generate maze: GLOBAL - maze_randomcicles
def startmaze():
	#randommaze = [[random.randint(0,1) for x in range(grid_x)] for y in range(grid_y)] 
	randommaze=make_maze(int((grid_x-1)/2),int((grid_y-1)/2))
	#add some cicles:
	for i in range(maze_randomcicles):
		x=random.randrange(int((grid_x-1)/2)-1)
		y=random.randrange(int((grid_y-1)/2))
		if randommaze[y*2+1][x*2+2]==1:
			randommaze[y*2+1][x*2+2]=0
	randommaze[1][0]=0 #start walk point 
	randommaze[grid_y-2][grid_x-1]=0 #end walk point
	xsize=grid_x
	ysize=grid_y
	for k in range(xsize-1):
		for l in range(ysize-1):
			if randommaze[l][k]==1 and randommaze[l-1][k]==0 and randommaze[l+1][k]==0 and randommaze[l][k-1]==0 and randommaze[l][k+1]==0:
				randommaze[l][k]=0
	#убрать одиночные блоки
	#print(cicle)
	return randommaze

#generate objects in maze: GLOBAL - maze, objects_energy, objects_oxygen, grid_x, grid_y
def startobjects():
	global maze, enemy
	objectsmaze=[[]]
	print(objectsmaze, grid_x, grid_y)
	objectsmaze=[[maze[y][x] for x in range(grid_x)] for y in range(grid_y)]
	#print (maze_objects)
	count=objects_energy #в коридорах
	while count>0:
		x=random.randrange(int((grid_x-1)/2)-1)
		y=random.randrange(int((grid_y-1)/2))
		if objectsmaze[y*2+1][x*2+2]==0:
			objectsmaze[y*2+1][x*2+2]=2
			count-=1
	count=objects_oxygen #в коридорах
	while count>0:
		x=random.randrange(int((grid_x-1)/2)-1)
		y=random.randrange(int((grid_y-1)/2))
		if objectsmaze[y*2+1][x*2+2]==0:
			objectsmaze[y*2+1][x*2+2]=3
			count-=1
	count=objects_health #в коридорах
	while count>0:
		x=random.randrange(int((grid_x-1)/2)-1)
		y=random.randrange(int((grid_y-1)/2))
		if objectsmaze[y*2+1][x*2+2]==0:
			objectsmaze[y*2+1][x*2+2]=6
			count-=1
	count=objects_hole #вместо стен
	while count>0:
		x=random.randrange(int(grid_x-2))+1
		y=random.randrange(int(grid_y-2))+1
		if maze[y][x]==1:
			objectsmaze[y][x]=7
			maze[y][x]=0
			count-=1
	count=objects_movingblock #вместо стен
	while count>0:
		x=random.randrange(int(grid_x-2))+1
		y=random.randrange(int(grid_y-2))+1
		if maze[y][x]==1:
			objectsmaze[y][x]=4
			maze[y][x]=0
			count-=1
	count=0 # генерация врагов в коридорах
	enemy=[[] for i in range(objects_enemy)]
	while count<objects_enemy:
		x=random.randrange(int((grid_x-1)/2)-1)
		y=random.randrange(int((grid_y-1)/2))
		if objectsmaze[y*2+1][x*2+2]==0:
			objectsmaze[y*2+1][x*2+2]=5
			#print(count)
			i=random.randrange(enemy_maxlevel+1)
			enemy[count]=[x*2+2,y*2+1,10,0,0,0,0,0,False] #enemy x,y,speed(act=10),act,state(random=0),type,heal,damage,killed
			enemy[count][2]=enemy_type[i][2]
			enemy[count][5]=enemy_type[i][5]
			enemy[count][6]=enemy_type[i][6]
			enemy[count][7]=enemy_type[i][7]
			count+=1
	#print(str(objects_enemy)+' '+str(len(enemy)))
	#print(objectsmaze)
	#print(enemy)
	return objectsmaze	

#generate environment: maze_oxygen
def start_env(concentration):
	#for i in range(grid_y):
	#	print (maze_objects[i])
	#print('\n')
	env_maze=[[random.randrange(2)*concentration for x in range(grid_x)] for y in range(grid_y)] #0 - no oxygen, concentration - oxygen
	for x in range(grid_x):
		for y in range(grid_y):
			if maze_objects[y][x]==1:env_maze[y][x]=0#1 - block
			if maze_objects[y][x]==4:env_maze[y][x]=0#4 - moving block
			if maze_objects[y][x]==7:env_maze[y][x]=0#7 - hole

	#for i in range(grid_y):
	#	print (env_maze[i])
	return env_maze

#change concentration: maze_oxygen
def next_env(env_maze): #таблица среды и имя среды
	#print('\n')
	env_change=[[0 for x in range(grid_x)] for y in range(grid_y)]
	for x in range(1,grid_x-1):
		for y in range(1,grid_y-1):
			stream=env_maze[y][x]//4
			if stream>0:
				if maze_objects[y][x-1]!=1 and maze_objects[y][x-1]!=4:
					env_change[y][x-1]+=stream
					env_maze[y][x]-=stream
				if maze_objects[y][x+1]!=1 and maze_objects[y][x+1]!=4:
					env_change[y][x+1]+=stream
					env_maze[y][x]-=stream
				if maze_objects[y-1][x]!=1 and maze_objects[y-1][x]!=4:
					env_change[y-1][x]+=stream
					env_maze[y][x]-=stream
				if maze_objects[y+1][x]!=1 and maze_objects[y+1][x]!=4:
					env_change[y+1][x]+=stream
					env_maze[y][x]-=stream
			else:
				env_maze[y][x]=0 #if concentration<4 -> oxygen=0
	for x in range(1,grid_x-1):
		for y in range(1,grid_y-1):
			if maze_objects[y][x]==7: #яма обнуляет кислород (in hole oxygen=0)
				env_maze[y][x]=0
			else:
				env_maze[y][x]+=env_change[y][x]
	#for i in range(grid_y):
	#	print (env_maze[i])
	return env_maze

#move enemies
def enemy_move():
	global enemy,maze_objects,player_heal
	for i in range(len(enemy)): #для каждого врага расчет отдельно
		enemy_x=enemy[i][0]
		enemy_y=enemy[i][1]
		enemy_speed=enemy[i][2]
		enemy_act=enemy[i][3]
		enemy_state=enemy[i][4]
		if enemy_act>0:
			enemy[i][3]-=1 #враг неподвижен пока не закончит ход
		elif enemy[i][8]==False: #враг живой
			#здесь движение
			direction=random.randrange(4) #random move
			if direction==0:
				enemy_x+=1
			elif direction==1:
				enemy_x-=1
			elif direction==2:
				enemy_y-=1
			elif direction==3:
				enemy_y+=1
			#print(enemy_x,enemy_y,enemy[i][0],enemy[i][1])
			if enemy_x==player_x and enemy_y==player_y:
				print('столкновение',enemy_x,enemy_y,player_x,player_y)
				player_heal=player_heal-enemy[i][7] #урон от врага
				enemy[i][6]=enemy[i][6]-player_damage #урон врагу
				enemy[i][3]=enemy_speed #враг потратил ход act=speed
				if enemy[i][6]<=0:
					enemy[i][8]=True #враг считается убитым
					maze_objects[enemy[i][1]][enemy[i][0]]=0 #враг удаляется из предметов
					player_action['KILL']+=1 #увеличиваем статистику убийств
			elif enemy_x==0 or enemy_x==grid_x or enemy_y==0 or enemy_y==grid_y: #враг не может войти в крайние поля лабиринта
				#print('монстр попытался выйти',enemy_x,enemy_y)
				pass
			elif maze[enemy_y][enemy_x]==0 and maze_objects[enemy_y][enemy_x]==0: #враг ходит только на пустое поле и без предметов
					maze_objects[enemy[i][1]][enemy[i][0]]=0
					enemy[i][0]=enemy_x
					enemy[i][1]=enemy_y
					maze_objects[enemy_y][enemy_x]=5
					enemy[i][3]=enemy_speed #враг потратил ход act=speed


#display maze: GLOBAL - surfaces of images, cellsize, grid_x, grid_y, FLAG_FOG, maze, maze_objects
def displaymaze():
	global display_wall_tick
	display_wall_tick+=1
	#gameDisplay.blit(zoomscreen,(0,0)) #фоновая картинка, если нет проверки поля на 0
	display_x_temp=int(display_x/cellsize) #сколько клеток влезет по горизонтали
	display_y_temp=int(display_y/cellsize) #сколько клеток влезет по вертикали
	center_x_temp=player_x
	center_y_temp=player_y
	diff_x=0
	diff_y=0
	if center_x_temp<display_x_temp//2: 
		diff_x=center_x_temp-display_x_temp//2
	if center_y_temp<display_y_temp//2: 
		diff_y=center_y_temp-display_y_temp//2
	if center_x_temp>(grid_x-display_x_temp//2):
		diff_x=center_x_temp+display_x_temp//2-grid_x
	if center_y_temp>(grid_y-display_y_temp//2):
		diff_y=center_y_temp+display_y_temp//2-grid_y
	image_index=zoomsize.index(cellsize)
	for i in range(center_x_temp-display_x_temp-diff_x,center_x_temp+display_x_temp-diff_x):
		for j in range(center_y_temp-display_y_temp-diff_y,center_y_temp+display_y_temp-diff_y):
			x=cellsize*(i-center_x_temp+diff_x+display_x_temp//2)#+display_x//2
			y=cellsize*(j-center_y_temp+diff_y+display_y_temp//2)#+display_y//2
			inscreen=x<0 or x>=display_x or y<0 or y>=display_y
			if not inscreen:
				if i<0 or i>=grid_x or j<0 or j>=grid_y:
					pygame.draw.rect(gameDisplay, black, (x,y,cellsize,cellsize))
					#print (i,j)
				else:
					#print(i,j)
					if maze_fog[j][i]==1 or FLAG_FOG:
						#display maze array of blocks
						if maze[j][i]==0: #100000 если не надо ничего рисовать, 0 - рисовать пол
							gameDisplay.blit(zoomfloor[image_index],(x,y))
						if maze[j][i]==1:
							#мерцаиие сделать здесь
							if random.randrange(100)==100: #не мерцать
								gameDisplay.blit(zoomwall2[image_index],(x,y))
							else:
								gameDisplay.blit(zoomwall[image_index],(x,y))
										
						#display maze_objects array of objects
						if maze_objects[j][i]==2:
							gameDisplay.blit(zoomenergy[image_index],(x,y))
						if maze_objects[j][i]==3:
							gameDisplay.blit(zoomoxygen[image_index],(x,y))
						if maze_objects[j][i]==4:
							gameDisplay.blit(zoommovingblock[image_index],(x,y))
						if maze_objects[j][i]==6:
							gameDisplay.blit(zoomhealth[image_index],(x,y))
						if maze_objects[j][i]==7:
							#pygame.draw.rect(gameDisplay, red, (x,y,cellsize,cellsize)) #hole
							gameDisplay.blit(zoomhole[image_index],(x,y))
						if maze_objects[j][i]==5:
							enemy_index=[enemy.index(k) for k in enemy if k[0]==i and k[1]==j][0]#найти врага, cool!
							if enemy[enemy_index][5]==0:
								gameDisplay.blit(zoomenemy1[image_index],(x,y))
							if enemy[enemy_index][5]==1:
								gameDisplay.blit(zoomenemy2[image_index],(x,y))
							if enemy[enemy_index][5]==2:
								gameDisplay.blit(zoomenemy3[image_index],(x,y))
							if enemy[enemy_index][5]==3:
								gameDisplay.blit(zoomenemy4[image_index],(x,y))
							enemy_heal=int(enemy[enemy_index][6]*cellsize/enemy_type[enemy[enemy_index][5]][6]) #расчет процента здоровья врага
							pygame.draw.line(gameDisplay, red, (x,y),(x+enemy_heal,y))
						#display env oxygen
						if maze_oxygen[j][i]>0 and FLAG_SCANNER:
							pygame.draw.line(gameDisplay, blue, (x,y+1),(x+int(maze_oxygen[j][i]*cellsize/concentration_oxygen),y+1))
					else:
						pygame.draw.rect(gameDisplay, black, (x,y,cellsize,cellsize)) #fog of war
	if display_wall_tick>250: display_wall_tick=0

#display player on maze: GLOBAL - cellsize, player_x, player_y, zoomplayer1
def displayplayer():
	display_x_temp=int(display_x/cellsize) #сколько клеток влезет по горизонтали
	display_y_temp=int(display_y/cellsize) #сколько клеток влезет по вертикали
	
	if player_x<display_x_temp//2:
		x=cellsize*player_x
	elif player_x>(grid_x-display_x_temp//2):
		x=cellsize*(player_x-grid_x+display_x_temp//2)+cellsize*(display_x_temp//2)
	else: x=cellsize*(display_x_temp//2)
	
	if player_y<display_y_temp//2:
		y=cellsize*player_y
	elif player_y>(grid_y-display_y_temp//2):
		y=cellsize*(player_y-grid_y+display_y_temp//2)+cellsize*(display_y_temp//2)
	else: y=cellsize*(display_y_temp//2)
	#x=display_x//2 #cellsize*player_x
	#y=display_y//2 #cellsize*player_y
	image_index=zoomsize.index(cellsize)
	gameDisplay.blit(zoomplayer1[image_index],(x,y))
	if player_direction=='RIGHT':
		gameDisplay.blit(zoomarrow_right[image_index],(x,y))
	elif player_direction=='LEFT':
		gameDisplay.blit(zoomarrow_left[image_index],(x,y))
	elif player_direction=='UP':
		gameDisplay.blit(zoomarrow_up[image_index],(x,y))
	elif player_direction=='DOWN':
		gameDisplay.blit(zoomarrow_down[image_index],(x,y))
	pygame.draw.line(gameDisplay,red,(x,y),(x+int(player_heal*cellsize/100),y)) #процент здоровья игрока
	#pygame.draw.rect(gameDisplay, green, (x,y,cellsize,cellsize)) #player need image 

#display player info: GLOBAL mazenumber, player_oxygen, player_energy, display_y
def displayinfo(): 
	pygame.draw.rect(gameDisplay, white, (0,display_y,display_x,display_y)) #закрашивает и сканнер тоже
	myfont = pygame.font.SysFont(font_def,10)
	mytext = myfont.render('environment oxygen: '+str(maze_oxygen[player_y][player_x]),True,black)
	gameDisplay.blit(mytext,(0,display_y))
	mytext = myfont.render('maze number: '+str(mazenumber), True, black)
	gameDisplay.blit(mytext,(0,display_y+10))
	mytext = myfont.render('oxygen:'+str(int(player_oxygen))+' %', True, black)
	gameDisplay.blit(mytext,(0,display_y+20))
	mytext = myfont.render('energy:'+str(int(player_energy))+' %', True, black)
	gameDisplay.blit(mytext,(0,display_y+30))
	mytext = myfont.render('player x:'+str(player_x)+' player y:'+str(player_y)+' move:'+str(player_action['MOVE'])+' fog:'+str(player_action['FOG'])+' pick:'+str(player_action['PICK'])+' kill:'+str(player_action['KILL']), True, black)
	gameDisplay.blit(mytext,(0,display_y+40))
	expirience=player_action['PICK']*100+player_action['FOG']+player_action['MOVE']+player_action['KILL']*100+int(player_oxygen)+int(player_energy)+int(player_heal)
	mytext = myfont.render('exp after level complete: '+str(expirience),True,black)
	gameDisplay.blit(mytext,(0,display_y+50))
	mytext = myfont.render('time passed: '+str(int(time.clock()-starttime)),True,black)
	gameDisplay.blit(mytext,(0,display_y+60))
	mytext = myfont.render('player exp: '+str(player_expirience),True,black)
	gameDisplay.blit(mytext,(0,display_y+70))
	mytext = myfont.render('player heal: '+str(player_heal),True,black)
	gameDisplay.blit(mytext,(0,display_y+80))

#display scanner in radius of half of level size. In DEV 
def displayscanner(scanner_mode,tick):
	global zoomscanner
	if tick==0: # на этот тик пересчет, в остальное время статичная картинка
		radarsize=grid_x//2
		scannerimage=pygame.Surface((grid_x,grid_x))
		scanner_pixarray = pygame.PixelArray(scannerimage)
		for i in range(player_x-radarsize,player_x+radarsize):
			for j in range(player_y-radarsize,player_y+radarsize):
				if i>=0 and i<grid_x and j>=0 and j<grid_y:
					if scanner_mode=='OXYGEN' and concentration_oxygen>0 and (i-player_x)*(i-player_x)+(j-player_y)*(j-player_y)<radarsize**2:
						color_oxygen=(0,0,int(255*maze_oxygen[j][i]/concentration_oxygen))
						scanner_pixarray[i][j]=color_oxygen
		#del scanner_pixarray
		zoomscanner=pygame.transform.scale(scannerimage,(100,100))
		#zoomscanner.set_colorkey(((0x000000)))
	gameDisplay.blit(zoomscanner,(display_x-100,display_y))
	


#create surface from text and font
def text_objects(text, font):
	textSurface = font.render(text, True, black)
	return textSurface, textSurface.get_rect()

#button - message, rect coordinate, colors for button, action for button
def display_button(msg,x,y,w,h,ic,ac,action=None):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()
	#print(mouse, click)
	if x+w > mouse[0] > x and y+h > mouse[1] > y:
		pygame.draw.rect(gameDisplay, ac,(x,y,w,h))
		if click[0] == 1 and action != None:
			action()
	else:
		pygame.draw.rect(gameDisplay, ic,(x,y,w,h))
	smallText = pygame.font.SysFont(font_def,20)
	textSurf, textRect = text_objects(msg, smallText)
	textRect.center = ( (x+(w/2)), (y+(h/2)) )
	gameDisplay.blit(textSurf, textRect)

def unpause_game():
	global pausegame
	pausegame=False

def pause_game():
	'''largeText = pygame.font.SysFont("comicsansms",115)
	TextSurf, TextRect = text_objects("Paused", largeText)
	TextRect.center = ((display_x/2),(display_y/2))
	gameDisplay.blit(TextSurf, TextRect)'''
	while pausegame:
		for event in pygame.event.get():
			#print(event)
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		#gameDisplay.fill(white)
		display_button("Continue",display_x//2-75,display_y//2,150,50,green,bright_green,unpause_game)
		#display_button("Start Game",display_x//2-75,display_y//2+60,150,50,green,bright_green,main_menu)
		display_button("Quit",display_x//2-75,display_y//2+120,150,50,red,bright_red,quit_game)
		pygame.display.update()
		clock.tick(10)

def quit_game():
	pygame.quit()
	quit()   

#initialize player
#ALARM global changed
def initplayer():
	global player_x,player_y,player_action,player_oxygen,player_energy,player_heal,player_damage,player_speed,player_oxygen_time,player_oxygen_energy
	global maze_fog,starttime,fog_radius
	global cellsize
	cellsize=zoomsize[-1]
	player_x=0
	player_y=1
	player_energy=upgrades['ENERGY_MAX'][player_upgrades['ENERGY_MAX']]
	player_oxygen=upgrades['OXYGEN_MAX'][player_upgrades['OXYGEN_MAX']]
	player_heal  =upgrades['HEALTH_MAX'][player_upgrades['HEALTH_MAX']]
	player_damage=upgrades['MELEE_DAMAGE'][player_upgrades['MELEE_DAMAGE']]
	fog_radius   =upgrades['FOG_RADIUS'][player_upgrades['FOG_RADIUS']]
	player_speed =upgrades['SPEED_TICK'][player_upgrades['SPEED_TICK']]
	player_oxygen_time=upgrades['OXYGEN_TIME'][player_upgrades['OXYGEN_TIME']]
	player_oxygen_energy=upgrades['OXYGEN_ENERGY'][player_upgrades['OXYGEN_ENERGY']]
	print('upgraded player ENERGY_MAX:',player_energy, 'OXYGEN_MAX:', player_oxygen, 'HEALTH_MAX:', player_heal, 'MELEE_DAMAGE:', player_damage, 'FOG_RADIUS:', fog_radius, 'SPEED_TICK:', player_speed, 'OXYGEN_TIME:', player_oxygen_time)
	print('OXYGEN_ENERGY:',player_oxygen_energy)
	#statistics:
	player_action={'MOVE':0,'FIRE':0,'FOG':0,'PICK':0,'KILL':0}
	print('initialize player x:',player_x,' player y:',player_y,' move:',player_action['MOVE'])
	#fog of war:
	maze_fog=[[0 for x in range(grid_x)] for y in range(grid_y)] #0 for fog and 1 for always visible
	for i in range(0,grid_x):
		maze_fog[0][i]=1
		maze_fog[grid_y-1][i]=1
	for j in range(0,grid_y):
		maze_fog[j][0]=1
		maze_fog[j][grid_x-1]=1
	starttime=time.clock()

#update maze for after moving player GLOBAL - fog_radius, grid_x, grid_y
def maze_fog_update(x,y):
	#первый вариант: просто квадрат вокруг игрока на плюс минус 2 клетки
	visible_radius=fog_radius
	for i in range(x-visible_radius,x+visible_radius+1):
		for j in range(y-visible_radius,y+visible_radius+1):
			if i>=0 and i<grid_x and j>=0 and j<grid_y:
				if maze_fog[j][i]==0:
					player_action['FOG']+=1
				maze_fog[j][i]=1

#update expirience after level complete
def update_expirience():
	global player_expirience
	level_expirience=player_action['PICK']*100+player_action['FOG']+player_action['MOVE']+player_action['KILL']*100+int(player_oxygen)+int(player_energy)+int(player_heal)
	timebonus=int((grid_x*grid_y)/(time.clock()-starttime))
	player_expirience=player_expirience+level_expirience+timebonus

#update level global parameters before start maze and after level complete or game over
def mazelevels_update(level):
	global grid_x,grid_y,maze_randomcicles,objects_oxygen,objects_energy,objects_movingblock,objects_enemy,enemy_maxlevel,objects_health,objects_hole,concentration_oxygen
	i=len(mazelevels) #длина массива уровней
	if level>=i: level=i-1 #уровень не превышает последний
	print('сложность уровня: '+str(level))
	grid_x=mazelevels[level][0]
	grid_y=mazelevels[level][1]
	maze_randomcicles=mazelevels[level][2]
	objects_oxygen=mazelevels[level][3]
	objects_energy=mazelevels[level][4]
	objects_movingblock=mazelevels[level][5]
	objects_enemy=mazelevels[level][6]
	enemy_maxlevel=mazelevels[level][7]
	objects_health=mazelevels[level][8]
	objects_hole=mazelevels[level][9]
	concentration_oxygen=mazelevels[level][10]
	#лабиринты задают параметры при увеличении mazenumber
	#grid_x,grid_y,maze_randomcicles,objects_oxygen,objects_energy,objects_movingblock,objects_enemy,maxlevel of enemy(?)
	print ('cell size: '+str(cellsize))
	print ('grid_x:	'+str(grid_x))
	print ('grid_y:	'+str(grid_y))
	print ('maze random cicles: '+str(maze_randomcicles))
	print ('energy: '+str(objects_energy))
	print ('oxygen: '+str(objects_oxygen))
	print ('health: '+str(objects_health))
	print ('moving blocks: '+str(objects_movingblock))
	print ('enemies: '+str(objects_enemy))
	print ('enemies max level: '+str(enemy_maxlevel))
	print ('holes:'+str(objects_hole))
	print ('oxygen concentration:'+str(concentration_oxygen))


#game over, wait 5 sec
def gameover():
	gameoverimg=pygame.image.load('gameover1.jpg').convert()
	zoomgameoverimg=pygame.transform.smoothscale(gameoverimg,(display_x,display_y+info_height))
	gameDisplay.blit(zoomgameoverimg,(0,0))
	myfont = pygame.font.SysFont(font_def,50)
	mytext = myfont.render('GAME OVER', True, red)
	gameDisplay.blit(mytext,((display_x-mytext.get_width())//2,display_y//2))
	pygame.display.update()
	pygame.time.wait(5000)

#start splash screen
def startover():
	startoverimg=pygame.image.load('startover1.jpg').convert()
	zoomstartoverimg=pygame.transform.smoothscale(startoverimg,(display_x,display_y+info_height))
	gameDisplay.blit(zoomstartoverimg,(0,0))
	pygame.display.update()
	pygame.time.wait(100)

#load player from file in main menu, or from network
def loadplayer():
	global mazenumber, player_expirience, maze, maze_objects, player_upgrades,maze_oxygen
	try:
		file = open('saveplayer.txt')
	except IOError as e:
		print(u'не удалось открыть файл')
	else:
		a=[i for i in open('saveplayer.txt',"r")]
		mazenumber=int(a[0]) #1 строка это номер лабиринта
		player_expirience=int(a[1]) #2 строка это опыт игрока
		player_upgrades=eval(a[2]) #3 строка это dictionary player_upgrades в формате строки, преобразуется обратно в тип dictionary
		print(player_upgrades, type(player_upgrades))
		print('загружен прогресс')
		#init:
		mazelevels_update(mazenumber) #считывание глобальных параметров уровня
		maze=startmaze() #generate maze
		maze_objects=startobjects() #generate array of objects
		initplayer() #init to default player and fog
		maze_fog_update(player_x,player_y) #update fog
		maze_oxygen=start_env(concentration_oxygen) #generate oxygen
		main_menu() #return to main menu

#save player to file in main menu, or from network
def saveplayer():
	a=[mazenumber,player_expirience]
	open('saveplayer.txt','w').write(str(a[0]))
	open('saveplayer.txt','a').write('\n')
	open('saveplayer.txt','a').write(str(a[1]))
	open('saveplayer.txt','a').write('\n')
	open('saveplayer.txt','a').write(str(player_upgrades))
	print('сохранил прогресс в файл')

#screen with upgrades buttons and player parameters
def upgradeplayer():
	global upgrade_name
	startoverimg=pygame.image.load('upgrade2.jpg').convert()
	zoomstartoverimg=pygame.transform.smoothscale(startoverimg,(display_x,display_y+info_height))
	gameDisplay.blit(zoomstartoverimg,(0,0))
	pygame.display.update()
	pygame.time.wait(1000)
	print('upgrades:')
	#print(player_upgrades['ENERGY_MAX'], len(upgrades['ENERGY_MAX'])-1, player_expirience, upgrades['EXP'][player_upgrades['ENERGY_MAX']+1])
	upgrade_name=''
	#print(type(player_expirience))
	while True:
		#pygame.draw.rect(gameDisplay, black, (50,50,250,400))
		gameDisplay.blit(zoomstartoverimg,(0,0))
		pygame.draw.rect(gameDisplay,black,(35,35,550,460))
		pygame.draw.rect(gameDisplay,green,(35,35,550,460),1)
		for event in pygame.event.get():
			#print(event)
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		if player_upgrades['ENERGY_MAX']<len(upgrades['ENERGY_MAX'])-1 and player_expirience>upgrades['EXP'][player_upgrades['ENERGY_MAX']+1]:
			upgrade_name='ENERGY_MAX'
			display_button("ENERGY MAX",40,40,250,39,green,bright_green,upgrade_param)
		if player_upgrades['OXYGEN_MAX']<len(upgrades['OXYGEN_MAX'])-1 and player_expirience>upgrades['EXP'][player_upgrades['OXYGEN_MAX']+1]:
			upgrade_name='OXYGEN_MAX'
			display_button("OXYGEN MAX",40,80,250,39,green,bright_green,upgrade_param)
		if player_upgrades['HEALTH_MAX']<len(upgrades['HEALTH_MAX'])-1 and player_expirience>upgrades['EXP'][player_upgrades['HEALTH_MAX']+1]:
			upgrade_name='HEALTH_MAX'
			display_button("HEALTH MAX",40,120,250,39,green,bright_green,upgrade_param)
		if player_upgrades['MELEE_DAMAGE']<len(upgrades['MELEE_DAMAGE'])-1 and player_expirience>upgrades['EXP'][player_upgrades['MELEE_DAMAGE']+1]:
			upgrade_name='MELEE_DAMAGE'
			display_button("MELEE DAMAGE",40,160,250,39,green,bright_green,upgrade_param)
		if player_upgrades['FOG_RADIUS']<len(upgrades['FOG_RADIUS'])-1 and player_expirience>upgrades['EXP'][player_upgrades['FOG_RADIUS']+1]:
			upgrade_name='FOG_RADIUS'
			display_button("FOG OF WAR",40,200,250,39,green,bright_green,upgrade_param)
		if player_upgrades['SPEED_TICK']<len(upgrades['SPEED_TICK'])-1 and player_expirience>upgrades['EXP'][player_upgrades['SPEED_TICK']+1]:
			upgrade_name='SPEED_TICK'
			display_button("SPEED",40,240,250,39,green,bright_green,upgrade_param)
		if player_upgrades['OXYGEN_TIME']<len(upgrades['OXYGEN_TIME'])-1 and player_expirience>upgrades['EXP'][player_upgrades['OXYGEN_TIME']+1]:
			upgrade_name='OXYGEN_TIME'
			display_button("OXYGEN PER SEC",40,280,250,39,green,bright_green,upgrade_param)
		if player_upgrades['OXYGEN_ENERGY']<len(upgrades['OXYGEN_ENERGY'])-1 and player_expirience>upgrades['EXP'][player_upgrades['OXYGEN_ENERGY']+1]:
			upgrade_name='OXYGEN_ENERGY'
			display_button("ENERGY FOR OXYGEN",40,320,250,39,green,bright_green,upgrade_param)

		display_button("Return",40,440,250,40,green,bright_green,main_menu)
		
		myfont = pygame.font.SysFont(font_def,20)
		mytext = myfont.render('PLAYER ENERGY:    '+str(player_energy), True, white)
		gameDisplay.blit(mytext,(300,45))
		mytext = myfont.render('PLAYER OXYGEN:    '+str(player_oxygen), True, white)
		gameDisplay.blit(mytext,(300,85))
		mytext = myfont.render('PLAYER HEALTH:    '+str(player_heal), True, white)
		gameDisplay.blit(mytext,(300,125))
		mytext = myfont.render('MELEE DAMAGE:     '+str(player_damage), True, white)
		gameDisplay.blit(mytext,(300,165))
		mytext = myfont.render('FOG OF WAR RADIUS:'+str(fog_radius), True, white)
		gameDisplay.blit(mytext,(300,205))
		mytext = myfont.render('SPEED (COOLDOWN): '+str(player_speed), True, white)
		gameDisplay.blit(mytext,(300,245))
		mytext = myfont.render('OXYGEN PER SEC:   '+str(player_oxygen_time), True, white)
		gameDisplay.blit(mytext,(300,285))
		mytext = myfont.render('ENERGY FOR OXYGEN:'+str(player_oxygen_energy), True, white)
		gameDisplay.blit(mytext,(300,325))
		mytext = myfont.render('SUMM OF UPGRADES: '+str(player_upgrades['EXP']), True, white)
		gameDisplay.blit(mytext,(300,365))
		mytext = myfont.render('EXPIRIENCE:       '+str(player_expirience), True, white)
		gameDisplay.blit(mytext,(300,405))
		pygame.display.update()
		clock.tick(10)
	main_menu()

#used in upgradeplayer() to upgrade player parameters and decrease expirience
def upgrade_param():
	global player_upgrades, player_expirience,upgrade_name
	player_upgrades[upgrade_name]+=1 #увеличить уровень апргейда
	player_upgrades['EXP']+=1 #увеличить счетчик апгрейдов
	player_expirience-=upgrades['EXP'][player_upgrades[upgrade_name]] #вычесть опыт
	print(upgrade_name+' upgraded')
	initplayer()

#write on screen text from help.txt and return to main_menu
def helpscreen():
	startoverimg=pygame.image.load('gameover1.jpg').convert()
	zoomstartoverimg=pygame.transform.smoothscale(startoverimg,(display_x,display_y+info_height))
	gameDisplay.blit(zoomstartoverimg,(0,0))
	
	#read help file to text array
	text_array=[i[:-1] for i in open('help.txt',"r")]
	print (text_array)
	#display text array
	myfont = pygame.font.SysFont(font_def,20)
	for i in range(len(text_array)):
		mytext = myfont.render(text_array[i], True, white)
		gameDisplay.blit(mytext,(40,40+i*mytext.get_height()))
	#wait to return to main menu
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		display_button("Return",40,display_y-40,250,40,green,bright_green,main_menu)
		pygame.display.update()
		clock.tick(10)

#menu before start gameloop
def main_menu():
	startover() #нарисовать картинку на весь экран
	#нарисовать уровень лабиринта и количество опыта
	myfont = pygame.font.SysFont(font_def,20)
	mytext = myfont.render('MAZE LEVEL:'+str(mazenumber), True, white)
	pygame.draw.rect(gameDisplay, black, ((display_x-mytext.get_width())//2-5,display_y//2-105,mytext.get_width()+10,55))
	gameDisplay.blit(mytext,((display_x-mytext.get_width())//2,display_y//2-100))
	mytext = myfont.render('EXPIRIENCE:'+str(player_expirience), True, white)
	gameDisplay.blit(mytext,((display_x-mytext.get_width())//2,display_y//2-75))
	pygame.display.update()
	#нарисовать количество опыта
	menu=True
	while menu:
		for event in pygame.event.get():
			#print(event)
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		#gameDisplay.fill(white)
		if mazenumber>0:
			display_button("Continue",display_x//2-75,display_y//2,150,50,green,bright_green,gameloop) #1
			display_button("Save Player",display_x//2-75,display_y//2+180,150,50,green,bright_green,saveplayer) #4
			display_button("Upgrade Player",display_x//2-75,display_y//2+240,150,50,green,bright_green,upgradeplayer) #5
		if mazenumber==0:
			display_button("Start Game",display_x//2-75,display_y//2,150,50,green,bright_green,gameloop) #1
		display_button("Quit",display_x//2-75,display_y//2+60,150,50,red,bright_red,quit_game) #2
		display_button("Load Player",display_x//2-75,display_y//2+120,150,50,green,bright_green,loadplayer) #3
		display_button("Help",display_x//2-75,display_y//2+300,150,50,green,bright_green,helpscreen) #6
		pygame.display.update()
		clock.tick(10)

#import and create pictures:
wall=pygame.image.load('wall15.png').convert()
zoomwall=[pygame.transform.smoothscale(wall,(size,size)) for size in zoomsize]
wall2=pygame.image.load('wall17.png').convert()
zoomwall2=[pygame.transform.smoothscale(wall2,(size,size)) for size in zoomsize]
floor=pygame.image.load('wall5.png').convert()
zoomfloor=[pygame.transform.smoothscale(floor,(size,size)) for size in zoomsize]
energy = pygame.image.load('energy2.png').convert()
zoomenergy=[pygame.transform.scale(energy,(size,size)) for size in zoomsize]
oxygen = pygame.image.load('oxygen4.png').convert()
zoomoxygen=[pygame.transform.scale(oxygen,(size,size)) for size in zoomsize]
movingblock = pygame.image.load('wall2.png').convert()
zoommovingblock=[pygame.transform.smoothscale(movingblock,(size,size)) for size in zoomsize]
enemyimg1 = pygame.image.load('enemy2.png').convert()
zoomenemy1=[pygame.transform.smoothscale(enemyimg1,(size,size)) for size in zoomsize]
enemyimg2 = pygame.image.load('enemy6.png').convert()
zoomenemy2=[pygame.transform.smoothscale(enemyimg2,(size,size)) for size in zoomsize]
enemyimg3 = pygame.image.load('enemy7.png').convert()
zoomenemy3=[pygame.transform.smoothscale(enemyimg3,(size,size)) for size in zoomsize]
enemyimg4 = pygame.image.load('enemy4.png').convert()
zoomenemy4=[pygame.transform.smoothscale(enemyimg4,(size,size)) for size in zoomsize]
health = pygame.image.load('health1.png').convert()
zoomhealth=[pygame.transform.scale(health,(size,size)) for size in zoomsize]
hole = pygame.image.load('hole1.png').convert()
zoomhole=[pygame.transform.scale(hole,(size,size)) for size in zoomsize]
arrow_up = pygame.image.load('arrow_up.png').convert()
zoomarrow_up=[pygame.transform.scale(arrow_up,(size,size)) for size in zoomsize]
arrow_down = pygame.image.load('arrow_down.png').convert()
zoomarrow_down=[pygame.transform.scale(arrow_down,(size,size)) for size in zoomsize]
arrow_left = pygame.image.load('arrow_left.png').convert()
zoomarrow_left=[pygame.transform.scale(arrow_left,(size,size)) for size in zoomsize]
arrow_right = pygame.image.load('arrow_right.png').convert()
zoomarrow_right=[pygame.transform.scale(arrow_right,(size,size)) for size in zoomsize]
for i in range(len(zoomsize)): 
	zoomenemy1[i].set_colorkey((0x000000))
	zoomenemy2[i].set_colorkey((0x000000))
	zoomenemy3[i].set_colorkey((0x000000))
	zoomenemy4[i].set_colorkey((0x000000))
	zoomhealth[i].set_colorkey((4147404))
	zoomenergy[i].set_colorkey((15539236))
	zoomoxygen[i].set_colorkey((16777215))
	zoomhole[i].set_colorkey((16777215))
	zoomarrow_up[i].set_colorkey((16777215))
	zoomarrow_down[i].set_colorkey((16777215))
	zoomarrow_left[i].set_colorkey((16777215))
	zoomarrow_right[i].set_colorkey((16777215))
#zoomoxygen.set_alpha(128)
player1_img = pygame.image.load('player2.png').convert()
zoomplayer1=[pygame.transform.scale(player1_img,(size,size)) for size in zoomsize]
for i in range(len(zoomsize)): zoomplayer1[i].set_colorkey((15539236))
zoomscanner=pygame.Surface((100,100)) #заранее готовая черная картинка сканнера (потом перерисовать)
#zoomplayer1.set_alpha(128)
#screen=pygame.image.load('screen2.png').convert()
#zoomscreen=pygame.transform.smoothscale(screen,(display_x,display_y))


#main loop:
startover() #start splash screen 1 second
#gameDisplay.fill(white) #fill display
mazelevels_update(mazenumber) #update level global parameters
maze=startmaze() #generate maze
maze_objects=startobjects() #generate array of objects
#print(maze_objects)
#mazenumber+=1	#calculate count of maze generation and write count in console and display
initplayer()	#reset player settings to default
maze_fog_update(player_x,player_y)	#update fog of war in player position

maze_oxygen=start_env(concentration_oxygen) #generate oxygen in maze in empty place
#maze_oxygen=next_env(maze_oxygen) #next step oxygen stream
#tests
#print(maze)
#print(maze_objects)


def gameloop():
	#global act
	global player_action,player_x,player_y,player_oxygen,player_energy,player_expirience,player_heal,player_upgrades
	global maze,maze_objects,FLAG_FOG,mazenumber
	global pausegame
	global cellsize
	global enemy
	global env_speed, maze_oxygen
	global player_direction
	global FLAG_SCANNER
	act=['',0] #действие игрока текущее и длительность в тиках
	#act['MOVE',10]
	#act['MOVE BLOCK',15]
	while True:
		#startcicle=time.clock() #timer test
		keypressed=pygame.key.get_pressed()
		if act[1]==0:
			#print(clock.get_time())
			#test RIGHT MOVE
			if (keypressed[pygame.K_RIGHT] or keypressed[pygame.K_d]) and act[1]==0:
				player_direction='RIGHT'
				if maze[player_y][player_x+1]==0 and maze_objects[player_y][player_x+1]!=4 and maze_objects[player_y][player_x+1]!=5 and maze_objects[player_y][player_x+1]!=7:#пустое поле справа и не move block и не враг и не яма(hole)
					act=['MOVE',cooldown['MOVE']-player_speed]
					player_action['MOVE']+=1
					player_x+=1
					maze_fog_update(player_x,player_y)
					continue
				if maze_objects[player_y][player_x+1]==5:#справа враг
					act=['MOVE ON ENEMY',cooldown['MOVE ON ENEMY']-player_speed]
					enemy_index=[enemy.index(i) for i in enemy if i[0]==player_x+1 and i[1]==player_y][0]#найти индекс врага
					print('нападение на врага')
					player_heal=player_heal-enemy[enemy_index][7] #урон от врага
					enemy[enemy_index][6]=enemy[enemy_index][6]-player_damage #урон врагу
					if enemy[enemy_index][6]<=0: #проверка здоровья врага
						enemy[enemy_index][8]=True #враг считается убитым
						maze_objects[player_y][player_x+1]=0 #враг удаляется из предметов
						player_action['KILL']+=1 #увеличиваем статистику убийств
					continue
				if player_x<grid_x-2: #справа есть 2 поля
					if maze_objects[player_y][player_x+1]==4 and maze_objects[player_y][player_x+2]==0 and maze[player_y][player_x+2]==0: #справа move block и за ним нет предметов и пустое поле
						maze_objects[player_y][player_x+1]=0
						maze_objects[player_y][player_x+2]=4
						act=['MOVE BLOCK',cooldown['MOVE BLOCK']-player_speed]
						player_action['MOVE']+=1
						player_x+=1
						maze_fog_update(player_x,player_y)
						continue
			#test LEFT MOVE
			if (keypressed[pygame.K_LEFT] or keypressed[pygame.K_a]) and act[1]==0:
				player_direction='LEFT'
				if maze[player_y][player_x-1]==0 and maze_objects[player_y][player_x-1]!=4 and maze_objects[player_y][player_x-1]!=5 and maze_objects[player_y][player_x-1]!=7:
					act=['MOVE',cooldown['MOVE']-player_speed]
					player_action['MOVE']+=1
					player_x-=1
					maze_fog_update(player_x,player_y)
					continue
				if maze_objects[player_y][player_x-1]==5:#справа враг
					act=['MOVE ON ENEMY',cooldown['MOVE ON ENEMY']-player_speed]
					enemy_index=[enemy.index(i) for i in enemy if i[0]==player_x-1 and i[1]==player_y][0]#найти врага
					print('нападение на врага')
					player_heal=player_heal-enemy[enemy_index][7] #урон от врага
					enemy[enemy_index][6]=enemy[enemy_index][6]-player_damage #урон врагу
					if enemy[enemy_index][6]<=0:
						enemy[enemy_index][8]=True #враг считается убитым
						maze_objects[player_y][player_x-1]=0 #враг удаляется из предметов
						player_action['KILL']+=1 #увеличиваем статистику убийств
					continue
				if player_x>2:
					if maze_objects[player_y][player_x-1]==4 and maze_objects[player_y][player_x-2]==0 and maze[player_y][player_x-2]==0:
						maze_objects[player_y][player_x-1]=0
						maze_objects[player_y][player_x-2]=4
						act=['MOVE BLOCK',cooldown['MOVE BLOCK']-player_speed]
						player_action['MOVE']+=1
						player_x-=1
						maze_fog_update(player_x,player_y)
						continue
			#test UP MOVE
			if (keypressed[pygame.K_UP] or keypressed[pygame.K_w]) and act[1]==0:
				player_direction='UP'
				if maze[player_y-1][player_x]==0 and maze_objects[player_y-1][player_x]!=4 and maze_objects[player_y-1][player_x]!=5 and maze_objects[player_y-1][player_x]!=7:
					act=['MOVE',cooldown['MOVE']-player_speed]
					player_action['MOVE']+=1
					player_y-=1
					maze_fog_update(player_x,player_y)
					continue
				if maze_objects[player_y-1][player_x]==5:#справа враг
					act=['MOVE ON ENEMY',cooldown['MOVE ON ENEMY']-player_speed]
					enemy_index=[enemy.index(i) for i in enemy if i[0]==player_x and i[1]==player_y-1][0]#найти врага
					print('нападение на врага')
					player_heal=player_heal-enemy[enemy_index][7] #урон от врага
					enemy[enemy_index][6]=enemy[enemy_index][6]-player_damage #урон врагу
					if enemy[enemy_index][6]<=0:
						enemy[enemy_index][8]=True #враг считается убитым
						maze_objects[player_y-1][player_x]=0 #враг удаляется из предметов
						player_action['KILL']+=1 #увеличиваем статистику убийств
					continue
				if player_y>2:
					if maze_objects[player_y-1][player_x]==4 and maze_objects[player_y-2][player_x]==0 and maze[player_y-2][player_x]==0:
						maze_objects[player_y-1][player_x]=0
						maze_objects[player_y-2][player_x]=4
						act=['MOVE BLOCK',cooldown['MOVE BLOCK']-player_speed]
						player_action['MOVE']+=1
						player_y-=1
						maze_fog_update(player_x,player_y)
						continue
			#test DOWN MOVE
			if (keypressed[pygame.K_DOWN] or keypressed[pygame.K_s]) and act[1]==0:
				player_direction='DOWN'
				if maze[player_y+1][player_x]==0 and maze_objects[player_y+1][player_x]!=4 and maze_objects[player_y+1][player_x]!=5 and maze_objects[player_y+1][player_x]!=7:
					act=['MOVE',cooldown['MOVE']-player_speed]
					player_action['MOVE']+=1
					player_y+=1
					maze_fog_update(player_x,player_y)
					continue
				if maze_objects[player_y+1][player_x]==5:#справа враг
					act=['MOVE ON ENEMY',cooldown['MOVE ON ENEMY']-player_speed]
					enemy_index=[enemy.index(i) for i in enemy if i[0]==player_x and i[1]==player_y+1][0]#найти врага
					print('нападение на врага')
					player_heal=player_heal-enemy[enemy_index][7] #урон от врага
					enemy[enemy_index][6]=enemy[enemy_index][6]-player_damage #урон врагу
					if enemy[enemy_index][6]<=0:
						enemy[enemy_index][8]=True #враг считается убитым
						maze_objects[player_y+1][player_x]=0 #враг удаляется из предметов
						player_action['KILL']+=1 #увеличиваем статистику убийств
					continue
				if player_y<grid_y-2:
					if maze_objects[player_y+1][player_x]==4 and maze_objects[player_y+2][player_x]==0 and maze[player_y+2][player_x]==0:
						maze_objects[player_y+1][player_x]=0
						maze_objects[player_y+2][player_x]=4
						act=['MOVE BLOCK',cooldown['MOVE BLOCK']-player_speed]
						player_action['MOVE']+=1
						player_y+=1
						maze_fog_update(player_x,player_y)
						continue

		for event in pygame.event.get():
			#print(event)
			#https://www.pygame.org/docs/ref/key.html
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:#генерировать новый лабиринт
						mazenumber+=1	#calculate count of maze generation and write count in console and display
						mazelevels_update(mazenumber)
						maze=startmaze() #generate maze
						maze_objects=startobjects() #generate array of objects
						initplayer()	#reset player settings to default
						maze_fog_update(player_x,player_y)	#update fog of war in player position
						maze_oxygen=start_env(concentration_oxygen) #generate oxygen
						print ('концентрация кислорода: ',concentration_oxygen)
					if event.key == pygame.K_f:#on/off fog of war
						FLAG_FOG=not(FLAG_FOG)
					if event.key == pygame.K_m:#on/off minimap (scanner, radar)
						FLAG_SCANNER=not(FLAG_SCANNER)
					if event.key == pygame.K_p:#pause game
						pausegame = True
						print(pausegame)
						pause_game()
					if event.key == pygame.K_q:#уменьшить масштаб (только не меньше экрана)
						zoomindex=zoomsize.index(cellsize)
						if zoomindex>0: 
							newsize=zoomsize[zoomindex-1]
							print(newsize*grid_x, display_x)
							print(newsize*grid_y, display_y)
							if grid_x*newsize>=display_x and grid_y*newsize>=display_y: #проверка масштаба при котором карта не станет меньше экрана
								cellsize=newsize
					if event.key == pygame.K_e:#увеличить масштаб
						zoomindex=zoomsize.index(cellsize)
						if zoomindex<len(zoomsize)-1:
							cellsize=zoomsize[zoomindex+1]
					
		#gameDisplay.fill(white) #fill display - убрал, так как в displayinfo() заливается нижняя часть белым цветом
		displaymaze() #display maze
		displayplayer() #display player on maze
		displayinfo() #display player info
		if FLAG_SCANNER and concentration_oxygen>0: displayscanner('OXYGEN',env_speed['OXYGEN'][1]) #display scanner in bottom info place. Только если сканер включен, кислород есть и использовать TICK пересчета


		#test pick energy:
		if maze_objects[player_y][player_x]==2:
			player_energy+=50
			if player_energy>upgrades['ENERGY_MAX'][player_upgrades['ENERGY_MAX']]: player_energy=upgrades['ENERGY_MAX'][player_upgrades['ENERGY_MAX']]
			maze_objects[player_y][player_x]=0
			player_action['PICK']+=1
		#test pick oxygen:
		if maze_objects[player_y][player_x]==3:
			player_oxygen+=50
			if player_oxygen>upgrades['OXYGEN_MAX'][player_upgrades['OXYGEN_MAX']]: player_oxygen=upgrades['OXYGEN_MAX'][player_upgrades['OXYGEN_MAX']]
			maze_objects[player_y][player_x]=0
			player_action['PICK']+=1
		#test pick health:
		if maze_objects[player_y][player_x]==6:
			player_heal+=50
			if player_heal>upgrades['HEALTH_MAX'][player_upgrades['HEALTH_MAX']]: player_heal=upgrades['HEALTH_MAX'][player_upgrades['HEALTH_MAX']]
			maze_objects[player_y][player_x]=0
			player_action['PICK']+=1


		#test level complete:
		if player_x==grid_x-1 and player_y==grid_y-2: #game complete, reset game and player
			mazenumber+=1
			update_expirience()
			mazelevels_update(mazenumber) #считывание глобальных параметров уровня
			maze=startmaze()
			maze_objects=startobjects() #generate array of objects
			initplayer()
			maze_fog_update(player_x,player_y)
			maze_oxygen=start_env(concentration_oxygen) #generate oxygen
			main_menu()
		#test game over:
		if player_oxygen<=0 or player_energy<=0 or player_heal<=0:
			gameover() #надпись game over
			player_expirience=0 #сброс накопленного опыта
			mazenumber=0 #сброс на начальный уровень
			mazelevels_update(mazenumber) #считывание глобальных параметров уровня
			#update_expirience()
			maze=startmaze()
			maze_objects=startobjects() #generate array of objects
			player_upgrades={'EXP':0,'ENERGY_MAX':0,'OXYGEN_MAX':0,'HEALTH_MAX':0,'SPEED_TICK':0,'FOG_RADIUS':0,'MELEE_DAMAGE':0,'OXYGEN_TIME':0,'OXYGEN_ENERGY':0}
			initplayer()
			maze_fog_update(player_x,player_y)
			maze_oxygen=start_env(concentration_oxygen) #generate oxygen
			main_menu()
		
		#enemy move cicle
		enemy_move()
		
		#change environment (oxygen) with env_speed tick
		#print(concentration_oxygen, env_speed['OXYGEN'][1])
		if env_speed['OXYGEN'][1]<=0 and concentration_oxygen>0:
			maze_oxygen=next_env(maze_oxygen)
			env_speed['OXYGEN'][1]=env_speed['OXYGEN'][0]
			#for i in range(grid_y):
			#	print (maze_oxygen[i])
		env_speed['OXYGEN'][1]-=1

		pygame.display.update()
		
		#timer test:
		#print ('прошло времени за цикл не считая tick :',time.clock()-startcicle)

		#расход кислорода по времени
		player_oxygen-=player_oxygen_time/cooldown['TICK'] #1sec=-0.5 oxygen
		
		#сбор кислорода из внешней среды
		player_ox_diff=upgrades['OXYGEN_MAX'][player_upgrades['OXYGEN_MAX']]-player_oxygen
		if player_ox_diff>1 and maze_oxygen[player_y][player_x]>0: #если запаса кислорода мало и есть во внешней среде
			player_oxygen+=1 #добавить кислород на 1
			maze_oxygen[player_y][player_x]-=1 #собрать кислород во внешней среде
			player_energy-=player_oxygen_energy #затратить энергию на сбор кислорода

		#расход энергии при движении
		if act[1]>0 and (act[0]=='MOVE' or act[0]=='MOVE BLOCK' or act[0]=='MOVE ON ENEMY'):
			player_energy-=5.0/cooldown['TICK'] #1move=-1 energy
		if act[1]>0:act[1]-=1
		#ticker 1sec=50tick
		clock.tick(cooldown['TICK'])


#start main menu
main_menu()
#start game loop	
#gameloop()
pygame.quit()
quit()