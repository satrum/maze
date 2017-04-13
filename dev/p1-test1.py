# turyev.roman@gmail.com
# generate 2D mazes
import pygame
import random
import time
import sys
import os
from maze_init import *

print('default recursion limit: '+str(sys.getrecursionlimit()))
sys.setrecursionlimit(1000000) #увеличить глубину возможной рекурсии для генерации больших либиринтов
print('new recursion limit:	 '+str(sys.getrecursionlimit()))

#sounds init:
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)#4096)
sound=[]
#звуки взяты на : https://freesound.org/
sound.append(pygame.mixer.Sound('sounds/sound2.ogg')) #sound[0].play() small gun https://freesound.org/people/twisterman/sounds/163584/
sound.append(pygame.mixer.Sound('sounds/sound4.ogg')) #sound[1].play() step https://freesound.org/people/Reitanna/sounds/323737/
#sound[0].play(loops=0,maxtime=400) - 1 time 0.4 sec 


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
pygame.display.set_caption('SPACE STATION DUNGEON')
clock = pygame.time.Clock()

#проиграть звук, номер звука, количество повторов, миллисекунды
#звуки взяты на 
def sound_start(soundnum,loop,msec):
	if FLAG_SOUNDON:
		sound[soundnum].play(loop,msec)

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
	#START and EXIT
	randommaze[START[1]][START[0]]=0
	randommaze[EXIT[1]][EXIT[0]]=0
	'''
	randommaze[1][0]=0 #start walk point 
	randommaze[grid_y-2][grid_x-1]=0 #end walk point
	'''
	xsize=grid_x
	ysize=grid_y
	#убрать одиночные блоки
	for k in range(xsize-1):
		for l in range(ysize-1):
			if randommaze[l][k]==1 and randommaze[l-1][k]==0 and randommaze[l+1][k]==0 and randommaze[l][k-1]==0 and randommaze[l][k+1]==0:
				randommaze[l][k]=0
	
	#print(cicle)
	return randommaze

#generate objects in maze: GLOBAL - maze, objects_energy, objects_oxygen, grid_x, grid_y
def startobjects():
	global maze, enemy, objects_array, pick_array
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
	for i in range(len(objects_ammo)):
		count=objects_ammo[i] #в коридорах
		while count>0:
			x=random.randrange(int((grid_x-1)/2)-1)
			y=random.randrange(int((grid_y-1)/2))
			if objectsmaze[y*2+1][x*2+2]==0:
				if i==0:
					objectsmaze[y*2+1][x*2+2]=8
				if i==1:
					objectsmaze[y*2+1][x*2+2]=9
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
	
	#generate special objects (generators)
	objects_array=[]
	count=objects_energy_gen #вместо стен energy generators
	while count>0:
		x=random.randrange(int(grid_x-2))+1
		y=random.randrange(int(grid_y-2))+1
		if maze[y][x]==1:
			objectsmaze[y][x]=50
			maze[y][x]=0
			count-=1
			objects_array.append([ 50,objects_dict[50]['max'],objects_dict[50]['state'],x,y ])
	count=objects_heal_gen #вместо стен heal generators
	while count>0:
		x=random.randrange(int(grid_x-2))+1
		y=random.randrange(int(grid_y-2))+1
		if maze[y][x]==1:
			objectsmaze[y][x]=51
			maze[y][x]=0
			count-=1
			objects_array.append([ 51,objects_dict[51]['max'],objects_dict[51]['state'],x,y ])
	count=objects_oxygen_gen #вместо стен oxygen generators
	while count>0:
		x=random.randrange(int(grid_x-2))+1
		y=random.randrange(int(grid_y-2))+1
		if maze[y][x]==1:
			objectsmaze[y][x]=52
			maze[y][x]=0
			count-=1
			objects_array.append([ 52,objects_dict[52]['max'],objects_dict[52]['state'],x,y ])
	count=objects_food_gen #вместо стен food generators
	while count>0:
		x=random.randrange(int(grid_x-2))+1
		y=random.randrange(int(grid_y-2))+1
		if maze[y][x]==1:
			objectsmaze[y][x]=53
			maze[y][x]=0
			count-=1
			objects_array.append([ 53,objects_dict[53]['max'],objects_dict[53]['state'],x,y ])
	for i in objects_array: 
		print(objects_dict[ i[0] ]['name'],i) #print special objects

	#generate objects for PICK:
	#test 'PICK':
	current_level=mazenumber
	j=len(mazelevels) #длина массива уровней
	if current_level>=j: current_level=j-1 #уровень не превышает последний
	pick_array=[]
	if type(mazelevels_target[current_level]['PICK'])==list: #если в задании PICK есть список
		for object_pick in mazelevels_target[current_level]['PICK']:
			count=object_pick[1] #количество объектов
			while count>0:
				x=random.randrange(int((grid_x-1)/2)-1)
				y=random.randrange(int((grid_y-1)/2))
				if objectsmaze[y*2+1][x*2+2]==0:
					objectsmaze[y*2+1][x*2+2]=object_pick[0]
					print('generated pick:',object_pick[0],objects_dict[object_pick[0]]['name'],x*2+2,y*2+1)
					pick_array.append([ object_pick[0],object_pick[2],True,x*2+2,y*2+1 ])
					count-=1
	print(pick_array)


	count=0 # генерация врагов в коридорах
	enemy=[[] for i in range(objects_enemy)]
	#test 'BOSS':
	current_level=mazenumber
	j=len(mazelevels) #длина массива уровней
	if current_level>=j: current_level=j-1 #уровень не превышает последний
	boss_level=mazelevels_target[current_level]['BOSS']
	#generate random enemies:
	while count<objects_enemy:
		x=random.randrange(int((grid_x-1)/2)-1)
		y=random.randrange(int((grid_y-1)/2))
		if objectsmaze[y*2+1][x*2+2]==0:
			objectsmaze[y*2+1][x*2+2]=5
			#print(count)
			i=enemy_maxlevel[random.randrange(len(enemy_maxlevel))] #случайный выбор типа врагов из списка доступных типов для данного уровня
			if boss_level>0 and count==0: #test first enemy and BOSS on level
				i=boss_level
			enemy[count]=[x*2+2,y*2+1,10,0,0,0,0,0,False,0,False, time.time()] #enemy x,y,speed(act=10),act,state(random=0),type,heal,damage,killed, direction, FLAG_last_moved, time.time()
			enemy[count][2]=enemy_type[i][2] #speed
			enemy[count][4]=enemy_type[i][4] #state
			enemy[count][5]=enemy_type[i][5] #type
			enemy[count][6]=enemy_type[i][6] #heal
			enemy[count][7]=enemy_type[i][7] #damage
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
def next_env(env_maze,env_name): #таблица среды и имя среды
	global objects_array
	#print('\n')
	#растекание среды:
	env_change=[[0 for x in range(grid_x)] for y in range(grid_y)]
	for x in range(1,grid_x-1):
		for y in range(1,grid_y-1):
			if env_maze[y][x]>3:
				stream=env_maze[y][x]//4
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
				if env_name=='OXYGEN':
					env_maze[y][x]=0 #if concentration<4 -> oxygen=0
	#обмен матриц старой и новой:
	if env_name=='OXYGEN':
		for x in range(1,grid_x-1):
			for y in range(1,grid_y-1):
				if maze_objects[y][x]==7: #яма обнуляет кислород (in hole oxygen=0)
					env_maze[y][x]=0
				else:
					env_maze[y][x]+=env_change[y][x]
	if env_name=='FOOD':
		for x in range(1,grid_x-1):
			for y in range(1,grid_y-1):
				env_maze[y][x]+=env_change[y][x]
	#генераторы:
	if env_name=='OXYGEN':
		for obj in objects_array:
			if obj[0]==52 and obj[1]>=objects_dict[52]['max']: #если объект - генератор кислорода и уровень кислорода на максимуме
				env_maze[ obj[4] ][ obj[3] ]=obj[1] #кислород весь попадает во внешнюю среду
				obj[1]=0 #генератор кислорода опустошается
	if env_name=='FOOD':
		for obj in objects_array:
			if obj[0]==53 and obj[1]>=objects_dict[53]['max']: #если объект - генератор еды и уровень еды на максимуме
				env_maze[ obj[4] ][ obj[3] ]=obj[1] #еда вся попадает во внешнюю среду
				obj[1]=0 #генератор еды опустошается
	#for i in range(grid_y):
	#	print (env_maze[i])
	return env_maze

#move enemies
def enemy_move():
	global enemy,maze_objects,player_heal,player_action
	dirarray={
	0: [1 , 0, 'RIGHT'],
	1: [-1, 0, 'LEFT' ],
	2: [0 ,-1, 'UP'   ],
	3: [0 , 1, 'DOWN' ],
	4: [0 , 0, 'STAY AND FIRE']
	}
	randomdirarray={
	0: [1,2],
	1: [1,3],
	2: [0,3],
	3: [0,2]
	}
	for i in range(len(enemy)): #для каждого врага расчет отдельно
		enemy_x=enemy[i][0]
		enemy_y=enemy[i][1]
		enemy_speed=enemy[i][2]
		enemy_act=enemy[i][3]
		
		enemy_state=enemy[i][4] #4 - state(0 - случайное блуждание, 1 - от края до края, 2 - нападение, 3 - убегает, 4 - стоит)
		enemy_direction=enemy[i][9] #9 - direction 0-RIGHT 1-LEFT 2-UP 3-DOWN

		if enemy_act>0 and enemy[i][8]==False:
			enemy[i][3]-=1 #враг неподвижен пока не закончит ход
		elif enemy[i][8]==False: #враг живой
			#здесь выбор тактики и само движение
			#0 - random direction choose
			if enemy_state==0: 
				newdirection=random.randrange(4) #random move
				enemy[i][9]=newdirection #сохранить новое направление движения врага
				dx=dirarray[newdirection][0] #определяем смещение по x
				dy=dirarray[newdirection][1] #определяем смещение по y
				enemy_x+=dx
				enemy_y+=dy
			#1 - move to block, after random
			elif enemy_state==1:
				dx=dirarray[enemy_direction][0] #определяем смещение по x
				dy=dirarray[enemy_direction][1] #определяем смещение по y
				if maze[enemy_y+dy][enemy_x+dx]==0 and maze_objects[enemy_y+dy][enemy_x+dx]==0: #если можно идти дальше по направлению
					enemy_x+=dx
					enemy_y+=dy
				else: #иначе меняем направление на любое из трех других
					newdirection=random.randrange(4) #random move
					while newdirection==enemy_direction: #пока выбранное направление остается, пытаться сменить
						newdirection=random.randrange(4) #random move
					enemy[i][9]=newdirection #сохранить новое направление движения врага
					dx=dirarray[newdirection][0] #определяем смещение по x
					dy=dirarray[newdirection][1] #определяем смещение по y
					enemy_x+=dx
					enemy_y+=dy
			#2 - agressive mode
			elif enemy_state==2:
				pos_dx=enemy_x-player_x
				pos_dy=enemy_y-player_y
				#newdirection=enemy[i][9]
				#расчет направления, пока только 4
				if pos_dx==0:
					if pos_dy>0: newdirection=2 #up
					else: newdirection=3 #down
				if pos_dy==0:
					if pos_dx>0: newdirection=1 #left
					else: newdirection=0 #right	
				if pos_dx>0 and pos_dy>0: newdirection=randomdirarray[0][random.randrange(2)]
				if pos_dx>0 and pos_dy<0: newdirection=randomdirarray[1][random.randrange(2)]
				if pos_dx<0 and pos_dy<0: newdirection=randomdirarray[2][random.randrange(2)]
				if pos_dx<0 and pos_dy>0: newdirection=randomdirarray[3][random.randrange(2)]
				#print(pos_dx,pos_dy,newdirection)
				dx=dirarray[newdirection][0] #определяем смещение по x
				dy=dirarray[newdirection][1] #определяем смещение по y
				if maze[enemy_y+dy][enemy_x+dx]!=0 or maze_objects[enemy_y+dy][enemy_x+dx]!=0:
					newdirection=random.randrange(4) #random move
					dx=dirarray[newdirection][0] #определяем смещение по x
					dy=dirarray[newdirection][1] #определяем смещение по y
					#print ('enemy '+str(i)+' random direction: '+dirarray[newdirection][2])
				enemy_x+=dx
				enemy_y+=dy
				enemy[i][9]=newdirection

			#3 - affraid mode
			elif enemy_state==3:
				pos_dx=player_x-enemy_x
				pos_dy=player_y-enemy_y
				#newdirection=enemy[i][9]
				#расчет направления, пока только 4
				if pos_dx==0:
					if pos_dy>0: newdirection=2 #up
					else: newdirection=3 #down
				if pos_dy==0:
					if pos_dx>0: newdirection=1 #left
					else: newdirection=0 #right	
				if pos_dx>0 and pos_dy>0: newdirection=randomdirarray[0][random.randrange(2)]
				if pos_dx>0 and pos_dy<0: newdirection=randomdirarray[1][random.randrange(2)]
				if pos_dx<0 and pos_dy<0: newdirection=randomdirarray[2][random.randrange(2)]
				if pos_dx<0 and pos_dy>0: newdirection=randomdirarray[3][random.randrange(2)]
				#print(pos_dx,pos_dy,newdirection)
				dx=dirarray[newdirection][0] #определяем смещение по x
				dy=dirarray[newdirection][1] #определяем смещение по y
				if maze[enemy_y+dy][enemy_x+dx]!=0 or maze_objects[enemy_y+dy][enemy_x+dx]!=0:
					newdirection=random.randrange(4) #random move
					dx=dirarray[newdirection][0] #определяем смещение по x
					dy=dirarray[newdirection][1] #определяем смещение по y
					#print ('enemy '+str(i)+' random direction: '+dirarray[newdirection][2])
				enemy_x+=dx
				enemy_y+=dy
				enemy[i][9]=newdirection
				
			#print(enemy_x,enemy_y,enemy[i][0],enemy[i][1])
			if enemy_x==player_x and enemy_y==player_y: #столкновение с игроком
				print('impact with player',enemy_x,enemy_y,player_x,player_y)
				player_heal=player_heal-enemy[i][7] #урон от врага
				enemy[i][6]=enemy[i][6]-player_damage #урон врагу
				enemy[i][3]=enemy_speed #враг потратил ход act=speed
				enemy[i][10]=False #enemy moved FLAG
				if enemy[i][6]<=0:
					print('enemy destroyed by impact')
					enemy[i][8]=True #враг считается убитым
					enemy[i][11]=time.time() #time of killed
					maze_objects[enemy[i][1]][enemy[i][0]]=0 #враг удаляется из предметов
					player_action['KILL']+=1 #увеличиваем статистику убийств
					if slime_level>0: slime_kill_enemy(enemy_x,enemy_y,enemy[i][5]) #generate food after kill if slime on level
			elif enemy_x==0 or enemy_x==grid_x-1 or enemy_y==0 or enemy_y==grid_y-1: #враг не может войти в крайние поля лабиринта
				#print('монстр попытался выйти',enemy_x,enemy_y)
				newdirection=random.randrange(4) #random move
				enemy[i][9]=newdirection #сохранить новое направление движения врага
				enemy[i][10]=False #enemy moved FLAG
				pass
			elif maze[enemy_y][enemy_x]==0 and maze_objects[enemy_y][enemy_x]==0: #враг ходит только на пустое поле и без предметов
					maze_objects[enemy[i][1]][enemy[i][0]]=0
					enemy[i][0]=enemy_x
					enemy[i][1]=enemy_y
					maze_objects[enemy_y][enemy_x]=5
					enemy[i][3]=enemy_speed #враг потратил ход act=speed
					enemy[i][10]=True #enemy moved FLAG


#display maze: GLOBAL - surfaces of images, cellsize, grid_x, grid_y, FLAG_FOG, maze, maze_objects
def displaymaze(activity):
	global display_wall_tick
	display_wall_tick+=1
	dirarray={
	0: [1 , 0, 'RIGHT'],
	1: [-1, 0, 'LEFT' ],
	2: [0 ,-1, 'UP'   ],
	3: [0 , 1, 'DOWN' ],
	4: [0 , 0, 'STAY AND FIRE']
	}
	#gameDisplay.blit(zoomscreen,(0,0)) #фоновая картинка, если нет проверки поля на 0
	display_x_temp=int(display_x/cellsize) #сколько клеток влезет по горизонтали
	display_y_temp=int(display_y/cellsize) #сколько клеток влезет по вертикали
	center_x_temp=player_x
	center_y_temp=player_y
	diff_x=0
	diff_y=0
	#расчет смещения при простом движении:
	dx=0
	dy=0
	if activity[0]=='MOVE' and activity[1]>0:
		dx=int(cellsize*activity[1]/cooldown['MOVE'])*directions[player_last_move][0]
		dy=int(cellsize*activity[1]/cooldown['MOVE'])*directions[player_last_move][1]

	if center_x_temp<display_x_temp//2+1: 
		diff_x=center_x_temp-display_x_temp//2
		dx=0
	if center_y_temp<display_y_temp//2+1: 
		diff_y=center_y_temp-display_y_temp//2
		dy=0
	if center_x_temp+1>(grid_x-display_x_temp//2):
		diff_x=center_x_temp+display_x_temp//2-grid_x
		dx=0
	if center_y_temp+1>(grid_y-display_y_temp//2):
		diff_y=center_y_temp+display_y_temp//2-grid_y
		dy=0
	image_index=zoomsize.index(cellsize)
	for i in range(center_x_temp-display_x_temp-diff_x-1,center_x_temp+display_x_temp-diff_x+1):
		for j in range(center_y_temp-display_y_temp-diff_y-1,center_y_temp+display_y_temp-diff_y+1):
			x=cellsize*(i-center_x_temp+diff_x+display_x_temp//2)#+display_x//2
			y=cellsize*(j-center_y_temp+diff_y+display_y_temp//2)#+display_y//2
			x+=dx
			y+=dy
			inscreen=x+cellsize<0 or x>=display_x or y+cellsize<0 or y>=display_y
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
							gameDisplay.blit(zoomhole[image_index],(x,y))
						if maze_objects[j][i]==8: #small gun bullets
							gameDisplay.blit(zoomammo1[image_index],(x,y))
						if maze_objects[j][i]==9: #minigun bullets
							gameDisplay.blit(zoomammo2[image_index],(x,y))
						
						#display generators
						if maze_objects[j][i]==50: #energy generator
							gameDisplay.blit(zoom_gen_energy[image_index],(x,y))
							for k in range(len(objects_array)): #найти нужный объект
								if i==objects_array[k][3] and j==objects_array[k][4]: obj_index=k
							if objects_array[obj_index][2]==False:
								gameDisplay.blit(zoomoff[image_index],(x,y))
							#расчет процента ресурса и отрисовка
							pygame.draw.line(gameDisplay, red, (x,y+2),(x+int(objects_array[obj_index][1]*cellsize/objects_dict[50]['max']),y+2))
						if maze_objects[j][i]==51: #health generator
							gameDisplay.blit(zoom_gen_heal[image_index],(x,y))
							for k in range(len(objects_array)): #найти нужный объект
								if i==objects_array[k][3] and j==objects_array[k][4]: obj_index=k
							if objects_array[obj_index][2]==False:
								gameDisplay.blit(zoomoff[image_index],(x,y))
							#расчет процента ресурса и отрисовка
							pygame.draw.line(gameDisplay, red, (x,y+2),(x+int(objects_array[obj_index][1]*cellsize/objects_dict[51]['max']),y+2))
						if maze_objects[j][i]==52: #oxygen generator
							gameDisplay.blit(zoom_gen_oxygen[image_index],(x,y))
							for k in range(len(objects_array)): #найти нужный объект
								if i==objects_array[k][3] and j==objects_array[k][4]: obj_index=k
							if objects_array[obj_index][2]==False:
								gameDisplay.blit(zoomoff[image_index],(x,y))
							#расчет процента ресурса и отрисовка
							pygame.draw.line(gameDisplay, red, (x,y+2),(x+int(objects_array[obj_index][1]*cellsize/objects_dict[52]['max']),y+2))
						if maze_objects[j][i]==53: #food generator
							gameDisplay.blit(zoom_gen_food[image_index],(x,y))
							for k in range(len(objects_array)): #найти нужный объект
								if i==objects_array[k][3] and j==objects_array[k][4]: obj_index=k
							if objects_array[obj_index][2]==False:
								gameDisplay.blit(zoomoff[image_index],(x,y))
							#расчет процента ресурса и отрисовка
							pygame.draw.line(gameDisplay, red, (x,y+2),(x+int(objects_array[obj_index][1]*cellsize/objects_dict[53]['max']),y+2))
						
						# display weapons
						if maze_objects[j][i]==60: #small gun
							gameDisplay.blit(zoomweapon[0][image_index],(x,y))
						if maze_objects[j][i]==61: #minigun
							gameDisplay.blit(zoomweapon[1][image_index],(x,y))
						# display material
						if maze_objects[j][i]==70: #small gun
							gameDisplay.blit(zoommaterial[0][image_index],(x,y))
						if maze_objects[j][i]==71: #minigun
							gameDisplay.blit(zoommaterial[1][image_index],(x,y))
							
						#if maze_objects[j][i]==5:
							#enemy_index=[enemy.index(k) for k in enemy if k[0]==i and k[1]==j and k[8]==False][0]#найти врага, cool!
							
							'''
							if enemy[enemy_index][5]==0:
								gameDisplay.blit(zoomenemy1[image_index],(x,y))
							if enemy[enemy_index][5]==1:
								gameDisplay.blit(zoomenemy2[image_index],(x,y))
							if enemy[enemy_index][5]==2:
								gameDisplay.blit(zoomenemy3[image_index],(x,y))
							if enemy[enemy_index][5]==3:
								gameDisplay.blit(zoomenemy4[image_index],(x,y))
							enemy_heal=int(enemy[enemy_index][6]*cellsize/enemy_type[enemy[enemy_index][5]][6]) #расчет процента здоровья врага
							pygame.draw.line(gameDisplay, red, (x,y),(x+enemy_heal,y))'''

						#display env oxygen
						if maze_oxygen[j][i]>0 and FLAG_SCANNER:
							pygame.draw.line(gameDisplay, blue, (x,y+1),(x+int(maze_oxygen[j][i]*cellsize/concentration_oxygen),y+1))
						#display env food
						if maze_food[j][i]>0 and FLAG_SCANNER:
							pygame.draw.line(gameDisplay, red, (x,y+3),(x+int(maze_food[j][i]*cellsize/concentration_food),y+3))
					else:
						pygame.draw.rect(gameDisplay, black, (x,y,cellsize,cellsize)) #fog of war

	#display dead enemies
	for k in enemy:
		enemy_x=cellsize*(k[0]-center_x_temp+diff_x+display_x_temp//2)#+display_x//2
		enemy_y=cellsize*(k[1]-center_y_temp+diff_y+display_y_temp//2)#+display_y//2
		enemy_x+=dx
		enemy_y+=dy
		outscreen=enemy_x+cellsize<0 or enemy_x>=display_x or enemy_y+cellsize<0 or enemy_y>=display_y
		time_passed=time.time()-k[11]
		if not outscreen and (maze_fog[ k[1] ][ k[0] ]==1 or FLAG_FOG) and k[8]==True and time_passed<enemy_blood_timer:
			enemy_speed=k[2]
			enemy_act=k[3] #<speed - двигается
			enemy_direction=k[9] #9 - direction 0-RIGHT 1-LEFT 2-UP 3-DOWN
			#if enemy_act<enemy_speed: #если враг в движении
			if k[10]:
				enemy_dx=int(dirarray[enemy_direction][0]*cellsize*enemy_act/enemy_speed)
				enemy_dy=int(dirarray[enemy_direction][1]*cellsize*enemy_act/enemy_speed)
				enemy_x-=enemy_dx
				enemy_y-=enemy_dy
			gameDisplay.blit(zoomblood[image_index],(enemy_x,enemy_y))
	
	#display live enemies
	enemy_display_count=0 #calculate displayed enemies
	for k in enemy:
		enemy_x=cellsize*(k[0]-center_x_temp+diff_x+display_x_temp//2)#+display_x//2
		enemy_y=cellsize*(k[1]-center_y_temp+diff_y+display_y_temp//2)#+display_y//2
		enemy_x+=dx
		enemy_y+=dy
		outscreen=enemy_x+cellsize<0 or enemy_x>=display_x or enemy_y+cellsize<0 or enemy_y>=display_y
		if not outscreen and (maze_fog[ k[1] ][ k[0] ]==1 or FLAG_FOG) and k[8]==False:
			enemy_display_count+=1 #this enemy in display
			enemy_speed=k[2]
			enemy_act=k[3] #<speed - двигается
			enemy_direction=k[9] #9 - direction 0-RIGHT 1-LEFT 2-UP 3-DOWN
			#if enemy_act<enemy_speed: #если враг в движении
			if k[10]:
				enemy_dx=int(dirarray[enemy_direction][0]*cellsize*enemy_act/enemy_speed)
				enemy_dy=int(dirarray[enemy_direction][1]*cellsize*enemy_act/enemy_speed)
				enemy_x-=enemy_dx
				enemy_y-=enemy_dy
			if   k[5]==0:
				gameDisplay.blit(zoomenemy1[image_index],(enemy_x,enemy_y))
			elif k[5]==1 or k[5]==4:
				gameDisplay.blit(zoomenemy2[image_index],(enemy_x,enemy_y))
			elif k[5]==2 or k[5]==5:
				gameDisplay.blit(zoomenemy3[image_index],(enemy_x,enemy_y))
			elif k[5]==3 or k[5]==7:
				gameDisplay.blit(zoomenemy4[image_index],(enemy_x,enemy_y))
			elif k[5]==6:
				gameDisplay.blit(zoomenemy5[image_index],(enemy_x,enemy_y))
			elif k[5]==8 or k[5]==9:
				gameDisplay.blit(zoomenemy6[image_index],(enemy_x,enemy_y))
			enemy_heal=int(k[6]*cellsize/enemy_type[ k[5] ][6]) #расчет процента здоровья врага
			pygame.draw.line(gameDisplay, red, (enemy_x,enemy_y),(enemy_x+enemy_heal,enemy_y))
	#print ('count display enemy by tick:'+str(enemy_display_count)) #print count of displayed enemies

	#display exit:
	current_level=mazenumber
	i=len(mazelevels) #длина массива уровней
	if current_level>=i: current_level=i-1 #уровень не превышает последний
	x_complete=EXIT[0]
	y_complete=EXIT[1]
	exit_x=cellsize*(x_complete-center_x_temp+diff_x+display_x_temp//2)+dx
	exit_y=cellsize*(y_complete-center_y_temp+diff_y+display_y_temp//2)+dy
	gameDisplay.blit(zoomexit[image_index],(exit_x,exit_y))

	#display bullets
	for i in range(len(player_bullets)):
		bullet_x=player_bullets[i][6]
		bullet_y=player_bullets[i][7]
		if maze_fog[bullet_y][bullet_x]==1 or FLAG_FOG:
			x=cellsize*(bullet_x-center_x_temp+diff_x+display_x_temp//2)
			y=cellsize*(bullet_y-center_y_temp+diff_y+display_y_temp//2)
			#смещение:
			bullet_direction=player_bullets[i][8]
			bullet_percent=int((player_bullets[i][2]%player_bullets[i][1])/player_bullets[i][1]*cellsize)
			gameDisplay.blit(zoombullet1[ directions[bullet_direction][2] ][image_index] ,(x+directions[bullet_direction][0]*bullet_percent,y+directions[bullet_direction][1]*bullet_percent))
	if display_wall_tick>250: display_wall_tick=0

#display player on maze: GLOBAL - cellsize, player_x, player_y, zoomplayer1
def displayplayer(activity):  # act in mainloop ['MOVE',cooldown tick]
	display_x_temp=int(display_x/cellsize) #сколько клеток влезет по горизонтали
	display_y_temp=int(display_y/cellsize) #сколько клеток влезет по вертикали
	dx=0
	dy=0
	#расчет смещения при простом движении:
	if activity[0]=='MOVE' and activity[1]>0:
		dx=int(cellsize*activity[1]/cooldown['MOVE'])*directions[player_last_move][0]
		dy=int(cellsize*activity[1]/cooldown['MOVE'])*directions[player_last_move][1]

	if player_x<display_x_temp//2:
		x=cellsize*player_x
	elif player_x>(grid_x-display_x_temp//2):
		x=cellsize*(player_x-grid_x+display_x_temp//2)+cellsize*(display_x_temp//2)
	else:
		x=cellsize*(display_x_temp//2)
		dx=0
	
	if player_y<display_y_temp//2:
		y=cellsize*player_y
	elif player_y>(grid_y-display_y_temp//2):
		y=cellsize*(player_y-grid_y+display_y_temp//2)+cellsize*(display_y_temp//2)
	else:
		y=cellsize*(display_y_temp//2)
		dy=0
	#x=display_x//2 #cellsize*player_x
	#y=display_y//2 #cellsize*player_y
	#изображение игрока
	x-=dx
	y-=dy
	image_index=zoomsize.index(cellsize)
	gameDisplay.blit(zoomplayer1[image_index],(x,y))
	'''
	if player_direction=='RIGHT':
		gameDisplay.blit(zoomarrow_right[image_index],(x,y))
	elif player_direction=='LEFT':
		gameDisplay.blit(zoomarrow_left[image_index],(x,y))
	elif player_direction=='UP':
		gameDisplay.blit(zoomarrow_up[image_index],(x,y))
	elif player_direction=='DOWN':
		gameDisplay.blit(zoomarrow_down[image_index],(x,y))
	'''
	pygame.draw.line(gameDisplay,red,(x,y),(x+int(player_heal*cellsize/upgrades['HEALTH_MAX'][player_upgrades['HEALTH_MAX']]),y)) #процент здоровья игрока
	#pygame.draw.rect(gameDisplay, green, (x,y,cellsize,cellsize)) #player need image 
	return x,y

#display player info: GLOBAL mazenumber, player_oxygen, player_energy, display_y
def displayinfo(): 
	pygame.draw.rect(gameDisplay, white, (0,display_y,display_x,info_height)) #закрашивает и сканнер тоже
	pygame.draw.rect(gameDisplay, blue, (2,display_y+2,display_x-4,info_height-5),2)
	myfont = pygame.font.SysFont(font_def,20)
	#left info
	mytext = myfont.render('environment oxygen: '+str(maze_oxygen[player_y][player_x]),True,black)
	gameDisplay.blit(mytext,(10,display_y))
	mytext = myfont.render('maze number: '+str(mazenumber), True, black)
	gameDisplay.blit(mytext,(10,display_y+20))
	mytext = myfont.render('oxygen:'+str(int(player_oxygen))+' %', True, black)
	gameDisplay.blit(mytext,(10,display_y+40))
	mytext = myfont.render('energy:'+str(int(player_energy))+' %', True, black)
	gameDisplay.blit(mytext,(10,display_y+60))
	stats='player x:'+str(player_x)+' player y:'+str(player_y)+' move:'+str(player_action['MOVE'])+' fog:'+str(player_action['FOG'])
	stats=stats+' pick:'+str(player_action['PICK'])+' kill:'+str(player_action['KILL'])+' fire:'+str(player_action['FIRE'])+' hit:'+str(player_action['HIT'])
	mytext = myfont.render(stats, True, black)
	gameDisplay.blit(mytext,(10,display_y+80))
	expirience=player_action['PICK']*100+player_action['FOG']+player_action['MOVE']+player_action['KILL']*100+int(player_oxygen)+int(player_energy)+int(player_heal)
	mytext = myfont.render('exp after level complete: '+str(expirience),True,black)
	gameDisplay.blit(mytext,(10,display_y+100))
	mytext = myfont.render('time passed: '+str(int(time.clock()-starttime)),True,black)
	gameDisplay.blit(mytext,(10,display_y+120))
	mytext = myfont.render('player exp: '+str(player_expirience),True,black)
	gameDisplay.blit(mytext,(10,display_y+140))
	mytext = myfont.render('player heal: '+str(player_heal),True,black)
	gameDisplay.blit(mytext,(10,display_y+160))
	#middle info
	mytext = myfont.render('hit accuracy: '+str( int( 100*(player_action['HIT']+1)/(player_action['FIRE']+1) ) ),True,black)
	gameDisplay.blit(mytext,(300,display_y))
	mytext = myfont.render('env food: '+str(maze_food[player_y][player_x]),True,black)
	gameDisplay.blit(mytext,(300,display_y+20))
	#inventory item
	if player_inventory[ player_inventory[0]][0]=='WEAPON': #if current item - weapon
		weapontype=player_inventory[ player_inventory[0]][1] #type of current weapon
		gameDisplay.blit(zoomweapon[weapontype][len(zoomsize)-1],(600,display_y)) #picture of weapon
		#myfont = pygame.font.SysFont(font_def,20)
		#mytext = myfont.render(str(weapons[weapontype][7]),True,black) #name of weapon
		#gameDisplay.blit(mytext,(600,display_y))
		myfont = pygame.font.SysFont(font_def,50)
		mytext = myfont.render(str(player_inventory[player_inventory[0]][2]),True,black) #bullets
		gameDisplay.blit(mytext,(700,display_y+30))
	if player_inventory[ player_inventory[0]][0]=='MATERIAL': #if current item - material
		materialtype=player_inventory[ player_inventory[0]][1] #type of current material
		gameDisplay.blit(zoommaterial[materialtype][len(zoomsize)-1],(600,display_y)) #picture of material
		myfont = pygame.font.SysFont(font_def,50)
		mytext = myfont.render(str(player_inventory[player_inventory[0]][2]),True,black) #quantity of material
		gameDisplay.blit(mytext,(700,display_y+30))


#display scanner in radius of half of level size. In DEV 
def displayscanner(scanner_mode,tick):
	global zoomscanner
	if tick==0: # на этот тик пересчет, в остальное время статичная картинка
		radarsize=grid_x//2
		scannerimage=pygame.Surface((grid_x,grid_x))
		scanner_pixarray = pygame.PixelArray(scannerimage)
		colorx=255//concentration_oxygen
		for i in range(player_x-radarsize,player_x+radarsize):
			for j in range(player_y-radarsize,player_y+radarsize):
				if i>=0 and i<grid_x and j>=0 and j<grid_y:
					if scanner_mode=='OXYGEN' and concentration_oxygen>0 and (i-player_x)*(i-player_x)+(j-player_y)*(j-player_y)<radarsize**2:
						color_oxygen=(0,0,maze_oxygen[j][i]*colorx)#int(255*maze_oxygen[j][i]/concentration_oxygen))
						#print(concentration_oxygen,color_oxygen)
						try:
							scanner_pixarray[i][j]=color_oxygen
						except:
							print(color_oxygen, concentration_oxygen)

		#del scanner_pixarray
		zoomscanner=pygame.transform.scale(scannerimage,(info_height,info_height))
		#zoomscanner.set_colorkey(((0x000000)))
	gameDisplay.blit(zoomscanner,(display_x-info_height,display_y))
	


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
	display_level_target()
	while pausegame:
		for event in pygame.event.get():
			#print(event)
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		#gameDisplay.fill(white)
		display_button("Continue",display_x//2-75,display_y//2,150,50,green,bright_green,unpause_game)
		display_button("Reset Level",display_x//2-75,display_y//2+60,150,50,green,bright_green,main_menu)
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
	global player_bullets
	cellsize=zoomsize[-1]
	player_x=START[0]
	player_y=START[1]
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
	player_action={'MOVE':0,'FIRE':0,'FOG':0,'PICK':0,'KILL':0,'HIT':0}
	print('initialize player x:',player_x,' player y:',player_y,' move:',player_action['MOVE'])
	player_bullets=[] #сброс всех летящих пуль, иначе возникает проблема при их отрисовке, если у оставшихся координаты будут в новом лабиринте за пределами лабиринта
	#fog of war:
	maze_fog=[[0 for x in range(grid_x)] for y in range(grid_y)] #0 for fog and 1 for always visible
	for i in range(0,grid_x):
		maze_fog[0][i]=1
		maze_fog[grid_y-1][i]=1
	for j in range(0,grid_y):
		maze_fog[j][0]=1
		maze_fog[j][grid_x-1]=1
	starttime=time.clock()
	print('starttime: '+str(starttime))
	print( time.strftime( "%a, %d %b %Y %H:%M:%S +0000", time.gmtime() ) ) #https://docs.python.org/3/library/time.html
	print( time.gmtime(time.time()) ) #time() return seconds from epoch and format by gmtime()
	'''
	starttime: 2.136531946524596
	time.struct_time(tm_year=2017, tm_mon=4, tm_mday=8, tm_hour=15, tm_min=43, tm_sec=16, tm_wday=5, tm_yday=98, tm_isdst=0) Sat, 08 Apr 2017 15:43:16 +0000
	time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=16, tm_sec=40, tm_wday=3, tm_yday=1, tm_isdst=0)
	'''

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
	global grid_x,grid_y,maze_randomcicles,objects_oxygen,objects_energy,objects_movingblock
	global objects_enemy,enemy_maxlevel,objects_health,objects_hole,concentration_oxygen,objects_ammo
	global objects_energy_gen,objects_heal_gen,objects_oxygen_gen,objects_food_gen
	global concentration_food,slime_level
	global START, EXIT
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
	objects_ammo=mazelevels[level][11]
	objects_energy_gen=mazelevels[level][12]
	objects_heal_gen=mazelevels[level][13]
	objects_oxygen_gen=mazelevels[level][14]
	objects_food_gen=mazelevels[level][15]
	concentration_food=mazelevels[level][16]
	slime_level=mazelevels[level][17]
	#лабиринты задают параметры при увеличении mazenumber
	#grid_x,grid_y,maze_randomcicles,objects_oxygen,objects_energy,objects_movingblock,objects_enemy,maxlevel of enemy(?)
	START=[]
	EXIT=[]
	START.append(mazelevels_target[level]['GOTO'][0])
	START.append(mazelevels_target[level]['GOTO'][1])
	if START[0]==0 and START[1]==0: #random START position of player
		START[0]=random.randrange(int((grid_x-1)/2)-1)*2+2
		START[1]=random.randrange(int((grid_y-1)/2))*2+1
	EXIT.append(mazelevels_target[level]['GOTO'][2])
	EXIT.append(mazelevels_target[level]['GOTO'][3])
	if EXIT[0]==0 and EXIT[1]==0: #random START position of player
		EXIT[0]=random.randrange(int((grid_x-1)/2)-1)*2+2
		EXIT[1]=random.randrange(int((grid_y-1)/2))*2+1


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
	print ('ammo:'+str(objects_ammo))
	print ('start:'+str(START)+' exit:'+str(EXIT))
	print ('energy generators:'+str(objects_energy_gen))
	print ('heal   generators:'+str(objects_heal_gen))
	print ('oxygen generators:'+str(objects_oxygen_gen))
	print ('food   generators:'+str(objects_food_gen))
	print ('food concentration:'+str(concentration_food))

#game over, wait 5 sec
def gameover(text):
	gameoverimg=pygame.image.load('gameover1.jpg').convert()
	zoomgameoverimg=pygame.transform.smoothscale(gameoverimg,(display_x,display_y+info_height))
	gameDisplay.blit(zoomgameoverimg,(0,0))
	myfont = pygame.font.SysFont(font_def,50)
	mytext = myfont.render('GAME OVER', True, red)
	gameDisplay.blit(mytext,((display_x-mytext.get_width())//2,display_y//2))
	mytext = myfont.render(text, True, red)
	gameDisplay.blit(mytext,((display_x-mytext.get_width())//2,display_y//2+50))
	pygame.display.update()
	pygame.time.wait(5000)

#start splash screen
def startover():
	startoverimg=pygame.image.load('startover1.jpg').convert()
	zoomstartoverimg=pygame.transform.smoothscale(startoverimg,(display_x,display_y+info_height))
	gameDisplay.blit(zoomstartoverimg,(0,0))
	pygame.display.update()
	pygame.time.wait(100)

#initialize level
def startlevel():
	global maze, maze_objects, maze_oxygen, maze_food, concentration_oxygen, concentration_food
	#init:
	mazelevels_update(mazenumber) #считывание глобальных параметров уровня
	maze=startmaze() #generate maze
	maze_objects=startobjects() #generate array of objects
	initplayer() #init to default player with upgrades and fog
	maze_fog_update(player_x,player_y) #update fog at player position
	maze_oxygen=start_env(concentration_oxygen) #generate oxygen
	maze_food=start_env(concentration_food) #generate food
	if objects_oxygen_gen>0: concentration_oxygen=objects_dict[52]['max'] #если на уровне есть генераторы кислорода, то концентрация не нулевая
	if objects_food_gen>0:   concentration_food  =objects_dict[53]['max'] #если на уровне есть генераторы еды, то концентрация не нулевая
	gameloop() #begin play game on level

#load player from file in main menu, or from network
def loadplayer():
	global mazenumber, player_expirience, maze, maze_objects, player_upgrades,maze_oxygen,player_inventory
	try:
		file = open('saveplayer.txt')
	except IOError as e:
		print(u'не удалось открыть файл')
	else:
		a=[i for i in open('saveplayer.txt',"r")]
		for i in a:
			print(i)
		mazenumber=int(a[0]) #1 строка это номер лабиринта
		player_expirience=int(a[1]) #2 строка это опыт игрока
		player_upgrades=eval(a[2]) #3 строка это dictionary player_upgrades в формате строки, преобразуется обратно в тип dictionary
		player_inventory=eval(a[3]) #4 строка это list player_inventory в формате строки
		print(player_upgrades, type(player_upgrades))
		print(player_inventory,type(player_inventory))
		print('загружен прогресс')
		#init:
		#startlevel()
		'''
		mazelevels_update(mazenumber) #считывание глобальных параметров уровня
		maze=startmaze() #generate maze
		maze_objects=startobjects() #generate array of objects
		initplayer() #init to default player and fog
		maze_fog_update(player_x,player_y) #update fog
		maze_oxygen=start_env(concentration_oxygen) #generate oxygen
		'''
		main_menu() #return to main menu

#save player to file in main menu, or from network
def saveplayer():
	a=[mazenumber,player_expirience]
	open('saveplayer.txt','w').write(str(a[0]))
	open('saveplayer.txt','a').write('\n')
	open('saveplayer.txt','a').write(str(a[1]))
	open('saveplayer.txt','a').write('\n')
	open('saveplayer.txt','a').write(str(player_upgrades))
	open('saveplayer.txt','a').write('\n')
	open('saveplayer.txt','a').write(str(player_inventory))
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
	#reset energy, oxygen, health of player
	initplayer()

	while True:
		#pygame.draw.rect(gameDisplay, black, (50,50,250,400))
		gameDisplay.blit(zoomstartoverimg,(0,0))
		pygame.draw.rect(gameDisplay,black,(35,35,550,500))
		pygame.draw.rect(gameDisplay,green,(35,35,550,500),1)
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
		if player_upgrades['BULLETS_MAX']<len(upgrades['BULLETS_MAX'])-1 and player_expirience>upgrades['EXP'][player_upgrades['BULLETS_MAX']+1]:
			upgrade_name='BULLETS_MAX'
			display_button("BULLETS MAX",40,360,250,39,green,bright_green,upgrade_param)

		display_button("Return",40,480,250,40,green,bright_green,main_menu)
		
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
		mytext = myfont.render('MAX BULLETS:'+str(upgrades['BULLETS_MAX'][player_upgrades['BULLETS_MAX']])+' %', True, white)
		gameDisplay.blit(mytext,(300,365))
		mytext = myfont.render('SUMM OF UPGRADES: '+str(player_upgrades['EXP']), True, white)
		gameDisplay.blit(mytext,(300,405))
		mytext = myfont.render('EXPIRIENCE:       '+str(player_expirience), True, white)
		gameDisplay.blit(mytext,(300,445))
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

#display level discription:
def display_level_target():
	global pick_array
	#параметры и описание уровня:
	pygame.draw.rect(gameDisplay,black,(35,35,600,290))
	pygame.draw.rect(gameDisplay,green,(35,35,600,290),1)
	i=len(mazelevels) #длина массива уровней
	current_level=mazenumber
	if current_level>=i: current_level=i-1 #уровень не превышает последний
	myfont = pygame.font.SysFont(font_def,20)
	mytext = myfont.render('X SIZE:'+str(mazelevels[current_level][0]), True, white)
	gameDisplay.blit(mytext,(40,40))
	mytext = myfont.render('Y SIZE:'+str(mazelevels[current_level][1]), True, white)
	gameDisplay.blit(mytext,(240,40))
	if mazelevels[current_level][6]==0:
		txt_1='NO ENEMIES'
	else: txt_1='ENEMIES ON LEVEL'
	mytext = myfont.render(txt_1, True, white)
	gameDisplay.blit(mytext,(40,80))
	if mazelevels[current_level][10]>0:
		mytext = myfont.render('OXYGEN DENCITY:'+str(mazelevels[current_level][10]), True, white)
		gameDisplay.blit(mytext,(40,120))
	mytext = myfont.render(mazelevels_target[current_level]['TEXT'], True, white)
	gameDisplay.blit(mytext,(40,160))
	if mazelevels_target[current_level]['KILL']>0:
		mytext = myfont.render('NEED TO KILL:'+str(mazelevels_target[current_level]['KILL']), True, white)
		gameDisplay.blit(mytext,(40,200))
	if mazelevels_target[current_level]['BOSS']>0:
		mytext = myfont.render('BOSS ON LEVEL:'+str(enemy_type[ mazelevels_target[current_level]['BOSS'] ][9]), True, white)
		gameDisplay.blit(mytext,(40,240))
	
	if type(mazelevels_target[current_level]['PICK'])==list:
		level_pick=mazelevels_target[current_level]['PICK']
		text_pick='NEED to PICK: '
		for i in level_pick:
			if text_pick!='NEED to PICK: ': text_pick+=', '
			if i[2]==True:
				count_picked=0
				for j in pick_array:
					if j[0]==i[0] and j[2]==False: count_picked+=1 #если предмет совпадает и собран с карты
				if count_picked>i[1]: count_picked=i[1] 
				text_pick=text_pick+str(i[1]-count_picked)+' '+objects_dict[i[0]]['name']
		mytext = myfont.render(text_pick, True, white)
		gameDisplay.blit(mytext,(40,280))

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
	display_level_target()
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
			display_button("Continue",display_x//2-75,display_y//2,150,50,green,bright_green,startlevel) #1
			display_button("Save Player",display_x//2-75,display_y//2+180,150,50,green,bright_green,saveplayer) #4
			display_button("Upgrade Player",display_x//2-75,display_y//2+240,150,50,green,bright_green,upgradeplayer) #5
		if mazenumber==0:
			display_button("Start Game",display_x//2-75,display_y//2,150,50,green,bright_green,startlevel) #1
		display_button("Quit",display_x//2-75,display_y//2+60,150,50,red,bright_red,quit_game) #2
		display_button("Load Player",display_x//2-75,display_y//2+120,150,50,green,bright_green,loadplayer) #3
		display_button("Help",display_x//2-75,display_y//2+300,150,50,green,bright_green,helpscreen) #6
		pygame.display.update()
		clock.tick(10)

#сделать выстрел, потратить пулю в оружии, создать пулю
def weapon_fire():
	global player_inventory, player_bullets,player_action
	player_inventory[player_inventory[0]][2]-=1 #уменьшить число пуль на 1
	print('bullets in weapon remain:'+str(player_inventory[player_inventory[0]][2]))
	current_weapon=player_inventory[player_inventory[0]][1] #текущий тип оружия
	print ('weapon fire: '+weapons[current_weapon][7]+'type: '+str(current_weapon))
	new_bullet=[current_weapon,weapons[current_weapon][3],0,weapons[current_weapon][5],player_x,player_y,player_x+directions[player_direction][0],player_y+directions[player_direction][1],player_direction,weapons[current_weapon][2]]
	player_bullets.append(new_bullet)
	print(player_bullets)
	player_action['FIRE']+=1
	#player bullets:
	#	0 - тип вооружения
	#	1 - speed (from weapon speed)
	#	2 - tick (current tick)
	#	3 - range (from weapon range)
	#	4 - x_begin
	#	5 - y_begin
	#	6 - x_current
	#	7 - y_current
	#	8 - direction 'LEFT','RIGHT','UP','DOWN' 
	#	9 - damage (from weapon damage)

#пересчет такта полета всех пуль, просчет попаданий
def bullets_fly(bullets):
	global enemy,maze_objects,player_action
	for i in range(len(bullets)): #счетчик пуль увеличить
		bullets[i][2]+=1
	length=len(bullets)
	for i in range(length-1,-1,-1): #удалить пули больше range, в обратном порядке так как список уменьшается и может стать пустым
		if bullets[i][2]==bullets[i][3]:
			print('bullet range maximum')
			bullets.pop(i)
	for i in range(len(bullets)): #пересчет координат player_x+direction[0]*tick//speed
		dx=directions[bullets[i][8]][0]
		dy=directions[bullets[i][8]][1]
		bullets[i][6]=bullets[i][4]+dx*(bullets[i][2]//bullets[i][1])
		bullets[i][7]=bullets[i][5]+dy*(bullets[i][2]//bullets[i][1])
	length=len(bullets)
	for i in range(length-1,-1,-1):
		x=bullets[i][6]
		y=bullets[i][7]
		if x<0 or x>=grid_x or y<0 or y>=grid_y:
			print('bullet out of maze')
			bullets.pop(i)
		elif maze[y][x]==1 or maze_objects[y][x]==4:#если стена, или двигающийся блок
			print('bullet in block')
			bullets.pop(i)
		elif maze_objects[y][x]==5: #если враг, нанести урон
			print('bullet in enemy')
			player_action['HIT']+=1
			damage=bullets[i][9]
			enemy_index=[enemy.index(j) for j in enemy if j[0]==x and j[1]==y and j[8]==False][0]#найти индекс врага
			enemy[enemy_index][6]=enemy[enemy_index][6]-damage #урон врагу пулей
			if enemy[enemy_index][6]<=0: #проверка здоровья врага
				print('enemy destroyed by fire')
				enemy[enemy_index][8]=True #враг считается убитым
				enemy[enemy_index][11]=time.time() #time of killed
				maze_objects[y][x]=0 #враг удаляется из предметов
				player_action['KILL']+=1 #увеличиваем статистику убийств
				if slime_level>0: slime_kill_enemy(x,y,enemy[enemy_index][5]) #generate food after kill if slime on level
			bullets.pop(i)
	#print(bullets)
	return bullets

#пересчет специальных объектов
def objects_change(objects_on_level):
	for obj in objects_on_level:
		if obj[2]==True: #0 - type, 1 - value, 2 - state (ON==True,OFF==False)
			if obj[0]==50: #energy generator
				obj[1]=obj[1]+objects_dict[50]['cooldown']/cooldown['TICK']
				if obj[1]>objects_dict[50]['max']:obj[1]=objects_dict[50]['max']
			if obj[0]==51: #health generator
				obj[1]=obj[1]+objects_dict[51]['cooldown']/cooldown['TICK']
				if obj[1]>objects_dict[51]['max']:obj[1]=objects_dict[51]['max']
			if obj[0]==52: #oxygen generator
				obj[1]=obj[1]+objects_dict[52]['cooldown']/cooldown['TICK']
				if obj[1]>objects_dict[52]['max']:obj[1]=objects_dict[52]['max']
			if obj[0]==53: #slime  generator
				obj[1]=obj[1]+objects_dict[53]['cooldown']/cooldown['TICK']
				if obj[1]>objects_dict[53]['max']:obj[1]=objects_dict[53]['max']
	return objects_on_level

#add food after in-place enemy kill
def slime_kill_enemy(x,y,type):
	global maze_food
	add_food=enemy_type[type][6]*slimes[slime_level]['kill']
	print('added food:'+str(add_food)+' at x:'+str(x)+' y:'+str(y))
	maze_food[y][x]+=add_food

#generate new slime in-place big concentration of food
def slime_new_enemy():
	global enemy, maze_objects, maze_food
	random.seed()
	count=len(enemy)
	new=enemy_type[ slimes[slime_level]['level'] ] #slime
	p=slimes[slime_level]['probability'] #probability
	c=slimes[slime_level]['newenemy'] #concentration
	for i in range(1,grid_x-1):
		for j in range(1,grid_y-1):
			if maze_food[j][i]>=c and maze_objects[j][i]==0 and maze[j][i]==0: #поле пустое, есть еда
				if player_x!=i or player_y!=j: #в поле не находится игрок
					generate=random.random()
					if generate<p: #случайная генерация врага
						#print(generate,p)
						enemy.append([ i,j,new[2],0   ,new[4],new[5],new[6],new[7],False, 0        ,False,time.time() ])
						#			   x y speed  act  state  type   heal   damage killed direction moved time
						maze_food[j][i]-=c
						maze_objects[j][i]=5
	if count<len(enemy): print( 'new slimes:'+str(len(enemy)-count)+' enemies:'+str(len(enemy)) )

def slime_regenerate_enemy():
	pass

def slime_split_enemy():
	pass

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
enemyimg5 = pygame.image.load('enemy5.png').convert()
zoomenemy5=[pygame.transform.smoothscale(enemyimg5,(size,size)) for size in zoomsize]
enemyimg6 = pygame.image.load('enemy8.png').convert()
zoomenemy6=[pygame.transform.scale(enemyimg6,(size,size)) for size in zoomsize]

health = pygame.image.load('health1.png').convert()
zoomhealth=[pygame.transform.scale(health,(size,size)) for size in zoomsize]
hole = pygame.image.load('hole1.png').convert()
zoomhole=[pygame.transform.scale(hole,(size,size)) for size in zoomsize]
#ammo for weapons:
ammo1_image = pygame.image.load('ammo3.png').convert()
zoomammo1=[pygame.transform.scale(ammo1_image,(size,size)) for size in zoomsize]
ammo2_image = pygame.image.load('ammo1.png').convert()
zoomammo2=[pygame.transform.scale(ammo2_image,(size,size)) for size in zoomsize]

exit_image = pygame.image.load('exit1.png').convert()
zoomexit=[pygame.transform.smoothscale(exit_image,(size,size)) for size in zoomsize]
gen_energy_img = pygame.image.load('generator1.png').convert()
zoom_gen_energy=[pygame.transform.scale(gen_energy_img,(size,size)) for size in zoomsize]
gen_heal_img   = pygame.image.load('generator2.png').convert()
zoom_gen_heal  =[pygame.transform.scale(gen_heal_img  ,(size,size)) for size in zoomsize]
gen_oxygen_img   = pygame.image.load('generator3.png').convert()
zoom_gen_oxygen  =[pygame.transform.scale(gen_oxygen_img  ,(size,size)) for size in zoomsize]
gen_food_img   = pygame.image.load('generator4.png').convert()
zoom_gen_food  =[pygame.transform.scale(gen_food_img  ,(size,size)) for size in zoomsize]
bloodimg   = pygame.image.load('blood.png').convert()
zoomblood =[pygame.transform.scale(bloodimg,(size,size)) for size in zoomsize]
offimg = pygame.image.load('off.png').convert()
zoomoff =[pygame.transform.scale(offimg,(size,size)) for size in zoomsize]

#weapons:
zoomweapon=[]
weapon1_img=pygame.image.load(weapons[0][8]).convert() #small gun
zoomweapon.append([pygame.transform.scale(weapon1_img,(size,size)) for size in zoomsize])
weapon2_img=pygame.image.load(weapons[1][8]).convert() #small gun
zoomweapon.append([pygame.transform.scale(weapon2_img,(size,size)) for size in zoomsize])
#material
zoommaterial=[]
material1_img=pygame.image.load('material1.png').convert() #small gun
zoommaterial.append([pygame.transform.scale(material1_img,(size,size)) for size in zoomsize])
material2_img=pygame.image.load('material2.png').convert() #small gun
zoommaterial.append([pygame.transform.scale(material2_img,(size,size)) for size in zoomsize])
#print('zoomweapon:',zoomweapon)

arrow_up = pygame.image.load('arrow_up.png').convert()
zoomarrow_up=[pygame.transform.scale(arrow_up,(size,size)) for size in zoomsize]
arrow_down = pygame.image.load('arrow_down.png').convert()
zoomarrow_down=[pygame.transform.scale(arrow_down,(size,size)) for size in zoomsize]
arrow_left = pygame.image.load('arrow_left.png').convert()
zoomarrow_left=[pygame.transform.scale(arrow_left,(size,size)) for size in zoomsize]
arrow_right = pygame.image.load('arrow_right.png').convert()
zoomarrow_right=[pygame.transform.scale(arrow_right,(size,size)) for size in zoomsize]

bullet1=pygame.image.load('bullet1.png').convert()
#bullet1=pygame.image.load('bullet2.png').convert()
zoombullet1=[[],[],[],[]]
zoombullet1[0]=[pygame.transform.scale(bullet1,(size,size)) for size in zoomsize]
zoombullet1[1]=[pygame.transform.rotate(bullet_sized,180) for bullet_sized in zoombullet1[0]]
zoombullet1[2]=[pygame.transform.rotate(bullet_sized,90) for bullet_sized in zoombullet1[0]]
zoombullet1[3]=[pygame.transform.rotate(bullet_sized,-90) for bullet_sized in zoombullet1[0]]
for i in range(len(zoomsize)): 
	zoomenemy1[i].set_colorkey((0x000000))
	zoomenemy2[i].set_colorkey((0x000000))
	zoomenemy3[i].set_colorkey((0x000000))
	zoomenemy4[i].set_colorkey((0x000000)) #black
	zoomenemy5[i].set_colorkey((0x000000)) #black
	zoomenemy6[i].set_colorkey((16777215)) #white
	zoomhealth[i].set_colorkey((4147404))
	zoomenergy[i].set_colorkey((15539236)) #red
	zoomoxygen[i].set_colorkey((16777215)) #white
	zoomhole[i].set_colorkey((16777215))
	zoomammo1[i].set_colorkey((15539236))
	zoomammo2[i].set_colorkey((15539236))
	zoom_gen_energy[i].set_colorkey((15539236)) #red
	zoom_gen_heal[i].set_colorkey((15539236)) #red
	zoom_gen_oxygen[i].set_colorkey((15539236)) #red
	zoom_gen_food[i].set_colorkey((15539236)) #red
	zoomblood[i].set_colorkey((16777215)) #white
	zoomoff[i].set_colorkey((16777215)) #white
	for j in range(2):
		zoomweapon[j][i].set_colorkey((16777215)) #white
	for j in range(2):
		zoommaterial[j][i].set_colorkey((16777215)) #white
	
	zoomarrow_up[i].set_colorkey((16777215))
	zoomarrow_down[i].set_colorkey((16777215))
	zoomarrow_left[i].set_colorkey((16777215))
	zoomarrow_right[i].set_colorkey((16777215))
	
	for j in range(len(zoombullet1)):
		zoombullet1[j][i].set_colorkey((16777215))
#zoomoxygen.set_alpha(128)
player1_img = pygame.image.load('player2.png').convert()
zoomplayer1=[pygame.transform.scale(player1_img,(size,size)) for size in zoomsize]
for i in range(len(zoomsize)): zoomplayer1[i].set_colorkey((15539236))
zoomscanner=pygame.Surface((info_height,info_height)) #заранее готовая черная картинка сканнера (потом перерисовать)
#zoomplayer1.set_alpha(128)
#screen=pygame.image.load('screen2.png').convert()
#zoomscreen=pygame.transform.smoothscale(screen,(display_x,display_y))



startover() #start splash screen 1 second
#gameDisplay.fill(white) #fill display
#startlevel()
'''
mazelevels_update(mazenumber) #update level global parameters
maze=startmaze() #generate maze
maze_objects=startobjects() #generate array of objects
#print(maze_objects)
#mazenumber+=1	#calculate count of maze generation and write count in console and display
initplayer()	#reset player settings to default
maze_fog_update(player_x,player_y)	#update fog of war in player position
maze_oxygen=start_env(concentration_oxygen) #generate oxygen in maze in empty place
#maze_oxygen=next_env(maze_oxygen) #next step oxygen stream
'''
#tests
#print(maze)
#print(maze_objects)



#main game play loop:
def gameloop():
	#global act
	global player_action,player_x,player_y,player_oxygen,player_energy,player_expirience,player_heal,player_upgrades
	global maze,maze_objects,FLAG_FOG,mazenumber
	global pausegame
	global cellsize
	global enemy
	global env_speed, maze_oxygen, maze_food
	global player_direction, player_last_move
	global FLAG_SCANNER, FLAG_SOUNDON
	global player_inventory
	global player_bullets
	global objects_array
	global player_display_x, player_display_y
	global pick_array
	act=['',0] #действие игрока текущее и длительность в тиках
	#act['MOVE',10]
	#act['MOVE BLOCK',15]
	current_level=mazenumber
	i=len(mazelevels) #длина массива уровней
	if current_level>=i: current_level=i-1 #уровень не превышает последний
	x_complete=EXIT[0]
	y_complete=EXIT[1]
	kill_complete=mazelevels_target[current_level]['KILL']
	boss_complete=mazelevels_target[current_level]['BOSS']
	pick_complete=0
	if type(mazelevels_target[current_level]['PICK'])==list:
		for i in mazelevels_target[current_level]['PICK']:
			if i[2]==True:
				print('need to pick:',i[1],' ',objects_dict[i[0]]['name'])
				pick_complete+=i[1]
			else: print('you can pick:',i[1],' ',objects_dict[i[0]]['name'])
	print('need to pick:',pick_complete, pick_array)

	print('goto x:'+str(x_complete)+' y:'+str(y_complete)+' kill:'+str(kill_complete)+' boss:'+str(boss_complete))

	while True:
		#startcicle=time.clock() #timer test
		keypressed=pygame.key.get_pressed()
		if act[1]==0:
			#print(clock.get_time())
			#test RIGHT MOVE
			if (keypressed[pygame.K_RIGHT] or keypressed[pygame.K_d]) and act[1]==0:
				player_direction='RIGHT'
				player_last_move='RIGHT'
				if maze[player_y][player_x+1]==0 and maze_objects[player_y][player_x+1]!=4 and maze_objects[player_y][player_x+1]!=5 and maze_objects[player_y][player_x+1]!=7:#пустое поле справа и не move block и не враг и не яма(hole)
					act=['MOVE',cooldown['MOVE']-player_speed]
					player_action['MOVE']+=1
					player_x+=1
					maze_fog_update(player_x,player_y)
					sound_start(1,0,200) #включить звук шага(sound[1]) один раз (0), на 0.155сек (155)
					#continue
				elif maze_objects[player_y][player_x+1]==5:#справа враг
					act=['MOVE ON ENEMY',cooldown['MOVE ON ENEMY']-player_speed]
					enemy_index=[enemy.index(i) for i in enemy if i[0]==player_x+1 and i[1]==player_y][0]#найти индекс врага
					print('нападение на врага')
					player_heal=player_heal-enemy[enemy_index][7] #урон от врага
					enemy[enemy_index][6]=enemy[enemy_index][6]-player_damage #урон врагу
					if enemy[enemy_index][6]<=0: #проверка здоровья врага
						enemy[enemy_index][8]=True #враг считается убитым
						enemy[enemy_index][11]=time.time() #time of killed
						maze_objects[player_y][player_x+1]=0 #враг удаляется из предметов
						player_action['KILL']+=1 #увеличиваем статистику убийств
						if slime_level>0: slime_kill_enemy(player_x+1,player_y,enemy[enemy_index][5]) #generate food after kill if slime on level
					#continue
				elif player_x<grid_x-2: #справа есть 2 поля
					if maze_objects[player_y][player_x+1]==4 and maze_objects[player_y][player_x+2]==0 and maze[player_y][player_x+2]==0: #справа move block и за ним нет предметов и пустое поле
						maze_objects[player_y][player_x+1]=0
						maze_objects[player_y][player_x+2]=4
						act=['MOVE BLOCK',cooldown['MOVE BLOCK']-player_speed]
						player_action['MOVE']+=1
						player_x+=1
						maze_fog_update(player_x,player_y)
						#continue
			#test LEFT MOVE
			if (keypressed[pygame.K_LEFT] or keypressed[pygame.K_a]) and act[1]==0:
				player_direction='LEFT'
				player_last_move='LEFT'
				if maze[player_y][player_x-1]==0 and maze_objects[player_y][player_x-1]!=4 and maze_objects[player_y][player_x-1]!=5 and maze_objects[player_y][player_x-1]!=7:
					act=['MOVE',cooldown['MOVE']-player_speed]
					player_action['MOVE']+=1
					player_x-=1
					maze_fog_update(player_x,player_y)
					sound_start(1,0,200) #включить звук шага(sound[1]) один раз (0), на 0.155сек (155)
					#continue
				elif maze_objects[player_y][player_x-1]==5:#справа враг
					act=['MOVE ON ENEMY',cooldown['MOVE ON ENEMY']-player_speed]
					enemy_index=[enemy.index(i) for i in enemy if i[0]==player_x-1 and i[1]==player_y][0]#найти врага
					print('нападение на врага')
					player_heal=player_heal-enemy[enemy_index][7] #урон от врага
					enemy[enemy_index][6]=enemy[enemy_index][6]-player_damage #урон врагу
					if enemy[enemy_index][6]<=0:
						enemy[enemy_index][8]=True #враг считается убитым
						enemy[enemy_index][11]=time.time() #time of killed
						maze_objects[player_y][player_x-1]=0 #враг удаляется из предметов
						player_action['KILL']+=1 #увеличиваем статистику убийств
						if slime_level>0: slime_kill_enemy(player_x-1,player_y,enemy[enemy_index][5]) #generate food after kill if slime on level
					#continue
				elif player_x>2:
					if maze_objects[player_y][player_x-1]==4 and maze_objects[player_y][player_x-2]==0 and maze[player_y][player_x-2]==0:
						maze_objects[player_y][player_x-1]=0
						maze_objects[player_y][player_x-2]=4
						act=['MOVE BLOCK',cooldown['MOVE BLOCK']-player_speed]
						player_action['MOVE']+=1
						player_x-=1
						maze_fog_update(player_x,player_y)
						#continue
			#test UP MOVE
			if (keypressed[pygame.K_UP] or keypressed[pygame.K_w]) and act[1]==0:
				player_direction='UP'
				player_last_move='UP'
				if maze[player_y-1][player_x]==0 and maze_objects[player_y-1][player_x]!=4 and maze_objects[player_y-1][player_x]!=5 and maze_objects[player_y-1][player_x]!=7:
					act=['MOVE',cooldown['MOVE']-player_speed]
					player_action['MOVE']+=1
					player_y-=1
					maze_fog_update(player_x,player_y)
					sound_start(1,0,200) #включить звук шага(sound[1]) один раз (0), на 0.155сек (155)
					#continue
				elif maze_objects[player_y-1][player_x]==5:#справа враг
					act=['MOVE ON ENEMY',cooldown['MOVE ON ENEMY']-player_speed]
					enemy_index=[enemy.index(i) for i in enemy if i[0]==player_x and i[1]==player_y-1][0]#найти врага
					print('нападение на врага')
					player_heal=player_heal-enemy[enemy_index][7] #урон от врага
					enemy[enemy_index][6]=enemy[enemy_index][6]-player_damage #урон врагу
					if enemy[enemy_index][6]<=0:
						enemy[enemy_index][8]=True #враг считается убитым
						enemy[enemy_index][11]=time.time() #time of killed
						maze_objects[player_y-1][player_x]=0 #враг удаляется из предметов
						player_action['KILL']+=1 #увеличиваем статистику убийств
						if slime_level>0: slime_kill_enemy(player_x,player_y-1,enemy[enemy_index][5]) #generate food after kill if slime on level
					#continue
				elif player_y>2:
					if maze_objects[player_y-1][player_x]==4 and maze_objects[player_y-2][player_x]==0 and maze[player_y-2][player_x]==0:
						maze_objects[player_y-1][player_x]=0
						maze_objects[player_y-2][player_x]=4
						act=['MOVE BLOCK',cooldown['MOVE BLOCK']-player_speed]
						player_action['MOVE']+=1
						player_y-=1
						maze_fog_update(player_x,player_y)
						#continue
			#test DOWN MOVE
			if (keypressed[pygame.K_DOWN] or keypressed[pygame.K_s]) and act[1]==0:
				player_direction='DOWN'
				player_last_move='DOWN'
				if maze[player_y+1][player_x]==0 and maze_objects[player_y+1][player_x]!=4 and maze_objects[player_y+1][player_x]!=5 and maze_objects[player_y+1][player_x]!=7:
					act=['MOVE',cooldown['MOVE']-player_speed]
					player_action['MOVE']+=1
					player_y+=1
					maze_fog_update(player_x,player_y)
					sound_start(1,0,200) #включить звук шага(sound[1]) один раз (0), на 0.155сек (155)
					#continue
				elif maze_objects[player_y+1][player_x]==5:#справа враг
					act=['MOVE ON ENEMY',cooldown['MOVE ON ENEMY']-player_speed]
					enemy_index=[enemy.index(i) for i in enemy if i[0]==player_x and i[1]==player_y+1][0]#найти врага
					print('нападение на врага')
					player_heal=player_heal-enemy[enemy_index][7] #урон от врага
					enemy[enemy_index][6]=enemy[enemy_index][6]-player_damage #урон врагу
					if enemy[enemy_index][6]<=0:
						enemy[enemy_index][8]=True #враг считается убитым
						enemy[enemy_index][11]=time.time() #time of killed
						maze_objects[player_y+1][player_x]=0 #враг удаляется из предметов
						player_action['KILL']+=1 #увеличиваем статистику убийств
						if slime_level>0: slime_kill_enemy(player_x,player_y+1,enemy[enemy_index][5]) #generate food after kill if slime on level
					#continue
				elif player_y<grid_y-2:
					if maze_objects[player_y+1][player_x]==4 and maze_objects[player_y+2][player_x]==0 and maze[player_y+2][player_x]==0:
						maze_objects[player_y+1][player_x]=0
						maze_objects[player_y+2][player_x]=4
						act=['MOVE BLOCK',cooldown['MOVE BLOCK']-player_speed]
						player_action['MOVE']+=1
						player_y+=1
						maze_fog_update(player_x,player_y)
						#continue
			'''
			if keypressed[pygame.K_RETURN] and player_inventory[player_inventory[0]][0]=='WEAPON': #если нажат предмет и предмет - оружие 
				#print('enter pressed')
				current_weapon=player_inventory[player_inventory[0]][1] #тип оружия
				if player_inventory[player_inventory[0]][3]==weapons[current_weapon][4]: #если достигло cooldown
					player_inventory[player_inventory[0]][3]=0 #сбросить счетчик tick
					if player_inventory[player_inventory[0]][2]>0:
						print('fire')
						weapon_fire() #сделать выстрел, потратить пулю в оружии, создать пулю
					else: print('no bullets')
			'''

		if pygame.mouse.get_pressed()[0]==1 and player_inventory[player_inventory[0]][0]=='WEAPON': #если нажата левая кнопка мышки и предмет - оружие 
			#print ('x: ',pygame.mouse.get_pos()[0],'y: ',pygame.mouse.get_pos()[1],'player x: ',player_display_x,'player y: ',player_display_y)
			pos_x=pygame.mouse.get_pos()[0]
			pos_y=pygame.mouse.get_pos()[1]
			pos_dx=pos_x-player_display_x
			pos_dy=pos_y-player_display_y
			print(pos_dx,pos_dy)
			#расчет направления, пока только 4
			if pos_dx>0 and pos_dy>0 and pos_dx>pos_dy: player_direction='RIGHT'
			if pos_dx>0 and pos_dy>0 and pos_dx<pos_dy: player_direction='DOWN'
			if pos_dx>0 and pos_dy<0 and pos_dx>abs(pos_dy): player_direction='RIGHT'
			if pos_dx>0 and pos_dy<0 and pos_dx<abs(pos_dy): player_direction='UP'
			if pos_dx<0 and pos_dy<0 and abs(pos_dx)>abs(pos_dy): player_direction='LEFT'
			if pos_dx<0 and pos_dy<0 and abs(pos_dx)<abs(pos_dy): player_direction='UP'
			if pos_dx<0 and pos_dy>0 and abs(pos_dx)>pos_dy: player_direction='LEFT'
			if pos_dx<0 and pos_dy>0 and abs(pos_dx)<pos_dy: player_direction='DOWN'
			#fire:
			current_weapon=player_inventory[player_inventory[0]][1] #тип оружия
			if player_inventory[player_inventory[0]][3]>=weapons[current_weapon][4]: #если достигло cooldown
				player_inventory[player_inventory[0]][3]=0 #сбросить счетчик tick
				if player_inventory[player_inventory[0]][2]>0: #если есть патроны (для оружия с расходниками, не энергетическое)
					print('fire')
					sound_start(0,0,500) #включить звук выстрела(sound[0]) один раз (0), на 0.3сек (300)
					weapon_fire() #сделать выстрел, потратить пулю в оружии, создать пулю					
				else: print('no bullets')

		for event in pygame.event.get():
			#print(event)
			#https://www.pygame.org/docs/ref/key.html
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:#генерировать новый лабиринт
						mazenumber+=1	#calculate count of maze generation and write count in console and display
						main_menu()
						'''
						mazelevels_update(mazenumber)
						maze=startmaze() #generate maze
						maze_objects=startobjects() #generate array of objects
						initplayer()	#reset player settings to default
						maze_fog_update(player_x,player_y)	#update fog of war in player position
						maze_oxygen=start_env(concentration_oxygen) #generate oxygen
						'''
						#print ('концентрация кислорода: ',concentration_oxygen)
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
					if event.key == pygame.K_F11:#sound on/off
						FLAG_SOUNDON=not(FLAG_SOUNDON)
					if event.key == pygame.K_RETURN: #pressed ENTER, interact with objects
						if maze_objects[player_y][player_x]>=50 and maze_objects[player_y][player_x]<=53: #if GENERATOR
							for obj in objects_array:
								if obj[3]==player_x and obj[4]==player_y: obj[2]=not(obj[2]) #turn on/off generator
					if event.key == pygame.K_c:#change item in inventory, change weapon etc.
						player_inventory[0]+=1
						if player_inventory[0]>=len(player_inventory):player_inventory[0]=1
						print(player_inventory[0], len(player_inventory))
					
		#gameDisplay.fill(white) #fill display - убрал, так как в displayinfo() заливается нижняя часть белым цветом
		displaymaze(act) #display maze
		player_display_x,player_display_y=displayplayer(act) #display player on maze and get display position of player
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
		#test pick ammo for small gun:
		if maze_objects[player_y][player_x]==8:
			inventory_index=0
			for i in range(1,len(player_inventory)):
				if player_inventory[i][0]=="WEAPON" and player_inventory[i][1]==0: #if player have weapon and type=0 (small gun)
					inventory_index=i
			if inventory_index>0: #if player have gun
				player_inventory[inventory_index][2]+=50
				bullets_maximum=upgrades['BULLETS_MAX'][player_upgrades['BULLETS_MAX']]*weapons[0][6]//100 #расчет максимума пуль для оружия по апгрейдам
				if player_inventory[inventory_index][2]>bullets_maximum: #bullets in weapon no more when maximum in small gun
					player_inventory[inventory_index][2]=bullets_maximum
				maze_objects[player_y][player_x]=0
				player_action['PICK']+=1
		#test pick ammo for minigun:
		if maze_objects[player_y][player_x]==9:
			inventory_index=0
			for i in range(1,len(player_inventory)):
				if player_inventory[i][0]=="WEAPON" and player_inventory[i][1]==1: #if player have weapon and type=1 (minigun)
					inventory_index=i
			if inventory_index>0: #if player have gun
				player_inventory[inventory_index][2]+=50
				bullets_maximum=upgrades['BULLETS_MAX'][player_upgrades['BULLETS_MAX']]*weapons[0][6]//100 #расчет максимума пуль для оружия по апгрейдам
				if player_inventory[inventory_index][2]>bullets_maximum: #bullets in weapon no more when maximum in small gun
					player_inventory[inventory_index][2]=bullets_maximum
				maze_objects[player_y][player_x]=0
				player_action['PICK']+=1
		#test pick energy generator:
		if maze_objects[player_y][player_x]==50:
			player_energy_diff=upgrades['ENERGY_MAX'][player_upgrades['ENERGY_MAX']]-player_energy
			for i in range(len(objects_array)): #найти нужный объект
				if player_x==objects_array[i][3] and player_y==objects_array[i][4]: obj_index=i
			obj_value=objects_array[obj_index][1]
			if obj_value>1 and player_energy_diff>1: #если энергии у игрока мало и есть энергия в генераторе
				player_energy+=1
				objects_array[obj_index][1]-=1
				print('player pick energy from generator')
		#test pick heal generator:
		if maze_objects[player_y][player_x]==51:
			player_heal_diff=upgrades['HEALTH_MAX'][player_upgrades['HEALTH_MAX']]-player_heal
			for i in range(len(objects_array)): #найти нужный объект
				if player_x==objects_array[i][3] and player_y==objects_array[i][4]: obj_index=i
			obj_value=objects_array[obj_index][1]
			if obj_value>1 and player_heal_diff>1: #если здоровья у игрока мало и есть запас здоровья в генераторе
				player_heal+=1
				objects_array[obj_index][1]-=1
				print('player pick health from generator')
		#test pick any type of WEAPON:
		if maze_objects[player_y][player_x] in [60,61,62,63,64,65,66,67,68,69]: #если оружие
			pick_object=maze_objects[player_y][player_x] #номер объекта
			print('picked weapon!!! type:'+objects_dict[pick_object]['name'])
			FLAG_ADDED=False
			if player_inventory[player_inventory[0]][0]=='EMPTY':  
				player_inventory.pop(player_inventory[0]) #если инвентарь пустой
				player_inventory.append(['WEAPON',objects_dict[pick_object]['type'],50,0]) #добавить в inventory запись WEAPON и 50 патронов
				FLAG_ADDED=True #объект добавлен
			for i in range(1,len(player_inventory)):
				if player_inventory[i][0]=='WEAPON' and FLAG_ADDED==False:
					if player_inventory[i][1]==objects_dict[pick_object]['type'] :
						player_inventory[i][2]+=50 #добавил к уже собранным
						FLAG_ADDED=True
			if FLAG_ADDED==False:
				player_inventory.append(['WEAPON',objects_dict[pick_object]['type'],50,0]) #собрал первый раз
				FLAG_ADDED=True #объект добавлен

			maze_objects[player_y][player_x]=0
			player_action['PICK']+=1
			if pick_complete>0: #если объект - часть задания на 'PICK'
				for i in mazelevels_target[current_level]['PICK']:
					if i[2]==True and i[0]==pick_object: pick_complete-=1 #если предмет обязателен и есть в задании
			for i in pick_array:
				if i[3]==player_x and i[4]==player_y: #если предмет найден в списке
					i[2]=False #помечается как убранный с карты 
			print(player_inventory)
			print('need to pick:',pick_complete, pick_array)
		
		#test pick any type of MATERIAL:
		if maze_objects[player_y][player_x] in [70,71,72,73,74,75,76,77,78,79]: #если материал
			pick_object=maze_objects[player_y][player_x] #номер объекта
			print('picked material!!! type:'+objects_dict[pick_object]['name'])
			FLAG_ADDED=False
			if player_inventory[player_inventory[0]][0]=='EMPTY':  
				player_inventory.pop(player_inventory[0]) #если инвентарь пустой
				player_inventory.append(['MATERIAL',objects_dict[pick_object]['type'],1,0]) #собрал первый раз
				FLAG_ADDED=True #объект добавлен
			for i in range(1,len(player_inventory)):
				if player_inventory[i][0]=='MATERIAL' and FLAG_ADDED==False:
					if player_inventory[i][1]==objects_dict[pick_object]['type'] :
						player_inventory[i][2]+=1 #добавил к уже собранным
						FLAG_ADDED=True
			if FLAG_ADDED==False:
				player_inventory.append(['MATERIAL',objects_dict[pick_object]['type'],1,0]) #собрал первый раз
				FLAG_ADDED=True #объект добавлен
			
			maze_objects[player_y][player_x]=0
			player_action['PICK']+=1
			if pick_complete>0: #если объект - часть задания на 'PICK'
				for i in mazelevels_target[current_level]['PICK']:
					if i[2]==True and i[0]==pick_object: pick_complete-=1 #если предмет обязателен и есть в задании
			for i in pick_array:
				if i[3]==player_x and i[4]==player_y: #если предмет найден в списке
					i[2]=False #помечается как убранный с карты
			print(player_inventory)
			print('need to pick:',pick_complete, pick_array)

		#test level complete:
		#test GOTO and KILL complete
		#if player_x==grid_x-1 and player_y==grid_y-2: #game complete, reset game and player
		if player_x==x_complete and player_y==y_complete:
			if boss_complete>0 and enemy[0][8]==True: #если есть босс и он убит (босс всегда генериться нулевым в списке врагов)
				boss_complete=0 #сбросить уромень босса в 0 - т.е. босса нет
			if kill_complete<=player_action['KILL'] and boss_complete==0 and pick_complete==0: #если убито достаточно врагов и босса нет(или убит) и собраны все предметы
				mazenumber+=1
				update_expirience()
				#startlevel()
				'''
				mazelevels_update(mazenumber) #считывание глобальных параметров уровня
				maze=startmaze()
				maze_objects=startobjects() #generate array of objects
				initplayer()
				maze_fog_update(player_x,player_y)
				maze_oxygen=start_env(concentration_oxygen) #generate oxygen
				'''
				main_menu()
			#else:player_x-=1
		#test game over:
		if player_oxygen<=0 or player_energy<=0 or player_heal<=0:
			gameovertext='oxygen over'*(player_oxygen<=0)+'energy over'*(player_energy<=0)+'health over'*(player_heal<=0)
			print('game over:'+gameovertext)
			gameover(gameovertext) #надпись game over
			player_expirience=0 #сброс накопленного опыта
			mazenumber=0 #сброс на начальный уровень
			player_upgrades={'EXP':0,'ENERGY_MAX':0,'OXYGEN_MAX':0,'HEALTH_MAX':0,'SPEED_TICK':0,'FOG_RADIUS':0,'MELEE_DAMAGE':0,'OXYGEN_TIME':0,'OXYGEN_ENERGY':0,'BULLETS_MAX':0}
			player_inventory=[1,['EMPTY',0,0,0]]
			#startlevel()
			'''
			mazelevels_update(mazenumber) #считывание глобальных параметров уровня
			#update_expirience()
			maze=startmaze()
			maze_objects=startobjects() #generate array of objects
			initplayer()
			maze_fog_update(player_x,player_y)
			maze_oxygen=start_env(concentration_oxygen) #generate oxygen
			'''
			main_menu()
		
		#bullets fly cicle
		player_bullets=bullets_fly(player_bullets)
		#enemy move cicle
		enemy_move()
		#change objects(generators) cicle
		objects_array=objects_change(objects_array)
		
		#change environment (oxygen) with env_speed tick
		#print(concentration_oxygen, env_speed['OXYGEN'][1])
		if env_speed['OXYGEN'][1]<=0 and concentration_oxygen>0:
			maze_oxygen=next_env(maze_oxygen,'OXYGEN')
			env_speed['OXYGEN'][1]=env_speed['OXYGEN'][0]
			#for i in range(grid_y):
			#	print (maze_oxygen[i])
		env_speed['OXYGEN'][1]-=1
		#change environment (food) with env_speed tick
		if env_speed['FOOD'][1]<=0 and concentration_food>0:
			maze_food=next_env(maze_food,'FOOD')
			env_speed['FOOD'][1]=env_speed['FOOD'][0]
		if slime_level>0:
			slime_new_enemy()
			slime_regenerate_enemy()
			slime_split_enemy()
		env_speed['FOOD'][1]-=1
		

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

		#пересчет cooldown on inventory (weapon fire)
		if player_inventory[player_inventory[0]][0]=='WEAPON': #если текущий предмет - оружие
			current_weapon=player_inventory[player_inventory[0]][1] #тип оружия
			if player_inventory[player_inventory[0]][3]<weapons[current_weapon][4]: #если не достигло cooldown
				player_inventory[player_inventory[0]][3]+=1 #увеличить счетчик на 1, растет до cooldown, сбрасывается в 0 когда происходит выстрел
		#print(player_inventory[player_inventory[0]][3])
		#ticker 1sec=50tick
		clock.tick(cooldown['TICK'])


#start main menu
main_menu()
#start game loop	
#gameloop()
pygame.quit()
quit()