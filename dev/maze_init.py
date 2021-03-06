import time #for starttime

#константы цветов:
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
bright_red = (128,0,0)
bright_green = (0,128,0)
bright_blue = (0,0,128)

#screen:
display_x=1500 #размер игрового поля по горизонтали
display_y=1000 #размер игрового поля по вертикали
info_height=200 #размер поля с инофрмацией по вертикали
display_y-=info_height #уменьшить размер игрового поля по вертикали на высоту поля с информацией
cellsize=100 #size of cell
zoomsize=[20,30,50,60,80,100] #разные размеры cellsize на разных режимах масштабирования, картинки образуют массивы с каждым размером
player_display_x=0 #позиция игрока на экране
player_display_y=0 #позиция игрока на экране
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
FLAG_SOUNDON=True  #True for sound on, False - off
# 0 - not visible
# 1 - visible
maze_objects=[[]]
objects_oxygen=10
objects_energy=50
objects_movingblock=100
objects_health=5
objects_hole=100
objects_ammo=[0,0] #ammo for 50 bullets
# 0 - no objects
# 1 - block
# 2 - energy +50%
# 3 - oxygen +50%
# 4 - moving block
# 5 - enemy
# 6 - health +50%
# 7 - hole (яма, дыра, засасывающая кислород)
# 8 - bullets (small gun)
# 9 - bullets (minigun)
#generators and other objects:
objects_dict={
50:{'name':'energy generator','objects_id':50,'max':50.0,'cooldown':1  ,'state':True},
51:{'name':'health generator','objects_id':51,'max':50.0,'cooldown':1  ,'state':True},
52:{'name':'oxygen generator','objects_id':52,'max':200.0,'cooldown':50,'state':True},
53:{'name':'food   generator','objects_id':53,'max':100.0,'cooldown':50,'state':True},
54:{'name':'water  generator','objects_id':54,'max':200.0,'cooldown':50,'state':True},
#50-59 GENERATORS
60:{'name':'small gun'       ,'objects_id':60,'type':0}, #weapons
61:{'name':'minigun'         ,'objects_id':61,'type':1}, #weapons
#60-69 WEAPON
70:{'name':'chip'            ,'objects_id':70,'type':0}, #material
71:{'name':'radio'           ,'objects_id':71,'type':1}  #material
#70-79 MATERIAL
}
# name
# objects_id - number in maze_objects[][]
# max - maximum value resource in object
# cooldown - increment resource in 1 sec (need divide by cooldown['TICK'])
# state - default state by generation (True(ON), False(OFF))
objects_array=[]
# objects dropped and generated on startobjects(), changed by mainloop in objects_change()
# objects_id,current value, state, x, y
# example: [ [50,45,True, 10,10], [51,0,False, 20,10] ]
# 	this is energy_generator, with current 45 energy adn state=True x=10 y=10
# 	this is heal_generator, with current 0 health adn state=False x=20 y=10
pick_array=[]
#objects for PICK (weapon, material) and generated on startobjects()
#objects_id, need_to_pick, on map, x, y
#example: [ [60,True,True,10,10] ] - small gun, NEED for PICK, on map, x=10, y=10
#example: [ [61,False,False,11,11] ] - minigun, not NEED for PICK, picked, x=11, y=11

#На карте появляются враги(монстры), которые перемещаются, у них есть скорость, уровень агрессии, урон, здоровье.
objects_enemy=50
enemy_maxlevel=[0]
enemy_blood_timer=120 #time in sec to see blood of killed enemies
#убрать генерацию в функцию startobjects()
#enemy=[[] for i in range(objects_enemy)]
enemy_type=[
[0,0,10,0,2,0,5 ,2 ,False,''             ,100], #0 heal=5 damage=2 cooldown=10 state - agressive zoomenemy1 
[0,0,5 ,0,0,1,2 ,10,False,''             ,50 ], #1 heal=2 damage=10 cooldown=5 state - random move zoomenemy2 
[0,0,20,0,0,2,4 ,10,False,''             ,100], #2 heal=4 damage=10 cooldown=20 state - random move zoomenemy3
[0,0,30,0,0,3,6 ,15,False,'DOG'          ,150], #3 heal=6 damage=15 cooldown=30 state - random move zoomenemy4

[0,0,5 ,0,3,4,2 ,10,False,''             ,50 ], #4 heal=2 damage=10 cooldown=5 state - affraid move zoomenemy2
[0,0,20,0,2,5,4 ,10,False,''             ,100], #5 heal=4 damage=10 cooldown=20 state - agressive move zoomenemy3
[0,0,15,0,2,6,50,10,False,'BIG DOG ROBOT',1000], #6 heal=50 damage=10 cooldown=20 state - agressive move zoomenemy5 BOSS for 7 level
[0,0,30,0,2,7,6 ,15,False,'DOG'          ,150], #7 heal=6 damage=15 cooldown=30 state - agressive move zoomenemy4
[0,0,20,0,0,8,2 ,2 ,False,'slime 1'      ,10 ], #8 heal=1 damage=1 cooldown=10 state - agressive
[0,0,10,0,2,9,3 ,5 ,False,'slime 2'      ,20 ], #9 heal=1 damage=1 cooldown=10 state - agressive
]
#0 1 2s 3 4 5 6h 7d 8
#0 - x
#1 - y
#2 - speed(10 act)
#3 - act(счетчик хода)
#4 - state(0 - случайное блуждание, 1 - от края до края, 2 - нападение, 3 - убегает, 4 - ?)
#5 - type(тип врага)
#6 - здоровье
#7 - урон от столкновения
#8 - killed (False, True)
#9 - name of enemy type for 'BOSS'
#10 - exp for kill
#
# only in enemy list (init in startobjects()) :
#9 - 0,1,2 or 3 move: enemy_move() - dirarray) - direction
#10 - FLAG enemy moved (False or True)
#11 - time.time() - created or killed

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
[21, 21, 30  ,0, 3 , 0   ,0   ,[0]      ,0 ,0  ,0 ,[0]    ,2 ,1 ,1, 4, 60, 1], #0 easy test level, +energy
[51, 45, 100 ,5 ,20, 0   ,10  ,[4]      ,0 ,0  ,0 ,[0]    ,0 ,0 ,0, 0,  0, 0], #1 medium test level, +oxygen, affraid enemies
[75, 45, 200 ,10,50, 0   ,20  ,[4]      ,0 ,0  ,0 ,[0]    ,0 ,0 ,0, 0,  0, 0], #2 medium level, energy+oxygen, affraid enemies
[75, 45, 100 ,10,50, 100 ,10  ,[0]      ,0 ,0  ,0 ,[2]    ,0 ,0 ,0, 0,  0, 0], #3 moving blocks (сложный лабиринт)
[75, 45, 200 ,10,50, 150 ,30  ,[0]      ,2 ,0  ,0 ,[2]    ,0 ,0 ,0, 0,  0, 0], #4 enemie level 0
[75, 45, 150 ,10,50, 300 ,60  ,[0]      ,8 ,0  ,0 ,[4]    ,0 ,0 ,0, 0,  0, 0], #5 more enemie level 0
[75, 75, 300 ,15,80, 200 ,90  ,[0,1]    ,8 ,0  ,0 ,[8]    ,0 ,0 ,0, 0,  0, 0], #6 enemie level 1 75*75
[75, 75, 200 ,15,80, 400 ,120 ,[0,1]    ,12,0  ,0 ,[16]   ,0 ,0 ,0, 0,  0, 0], #7(HARD) more enemie level 1 75*75 + boss
[101,101,500 ,0, 100,300 ,200 ,[0,1,2]  ,12,100,20,[16]   ,0 ,0 ,0, 0,  0, 0], #8 big level enemie level 2 101*101 holes and env_oxygen
[201,201,2000,40,400,2000,300 ,[0,1,2,3],20,0  ,0 ,[50]   ,0 ,0 ,0, 0,  0, 0], #9 very big level enemie level 3 201*201 трудный лабиринт
[201,201,9999,10,400,2000,1000,[0,1,2,3],10,100,20,[80]   ,0 ,0 ,0, 0,  0, 0], #10 very big, more enemies, больше пустых мест, меньше аптечек, для стрельбы
# 10 - надо агрессию у врагов! патроны заканчиваются!
[201,201,5000,0 ,200,3000,1000,[0,5,7]  ,30,0  ,0 ,[99,99],30,30,30,0,  0, 0], #11 Цель - убить большое количество врагов. Миниган, генераторы
# вылетает ошибка [Finished in 14.6s with exit code 3221225725] если делать 250 на 250
[101,101,1000,0 ,0  ,1000,0   ,[0]      ,0 ,0  ,0 ,[30,30],30,10,10,20, 0, 1], #12 Цель - slime1, других врагов нет. есть генераторы еды
[151,151,4000,0 ,0  ,4000,100 ,[7]      ,0 ,0  ,0 ,[40,40],60,20,20,10, 30,2]  #13 Цель - slime2, других врагов нет. есть генераторы еды b еда
#12,13 - возможно стоит новый элемент, например телепорт 
] 
#0   1   2    3  4   5    6    7         8  9   10 11      12 13 14 15  16 17
print(mazelevels)
#лабиринты задают параметры при увеличении mazenumber
#0 - grid_x
#1 - grid_y
#2 - maze_randomcicles
#3 - objects_oxygen
#4 - objects_energ
#5 - objects_movingblock
#6 - objects_enemy
#7 - enemy_maxlevel (list of enemy types)
#8 - objects_health
#9 - objects_hole
#10 - concentration_oxygen
#11 - objects_ammo (list of ammo: small gun 50 bullets, minigun 50 bullets)
#12 - special object: energy generators
#13 - special object: health generators
#14 - special object: oxygen generators
#15 - special object: food   generators
#16 - concentration_food
#17 - slime_level (of slime_level>0: generate slimes[slime_level-1])
#пока нет, но надо:  oxygen env flag on/off (просчитывать ли вообще кислород или он в нуле), oxygen generator, bullet(small gun)
mazelevels_target=[
#[0,1,21-1,21-2] 0 level START/EXIT test: [0,0,0   ,0   ]
{'GOTO': [0,1,21-2,21-2]  ,'KILL': 5,   'PICK': [[60,1,False]]             , 'BOSS':0, 'TEXT':'test level with energy and agressive enemies, kill 5 enemy!'}, #0
{'GOTO': [0,1,51-2,45-2]  ,'KILL': 1,   'PICK': 0                          , 'BOSS':0, 'TEXT':'small level with oxygen, enemies are running away'}, #1
{'GOTO': [0,1,0,0      ]  ,'KILL': 1,   'PICK': 0                          , 'BOSS':0, 'TEXT':'medium level with oxygen, enemies are running away, find EXIT'}, #2
{'GOTO': [0,1,75-2,45-2]  ,'KILL': 0,   'PICK': [[60,1,True]]              , 'BOSS':0, 'TEXT':'complex medium level with moving blocks and agressive enemies and GUN'}, #3
{'GOTO': [0,1,75-2,45-2]  ,'KILL': 0,   'PICK': 0                          , 'BOSS':0, 'TEXT':'medium level with agressive enemies and ammo for gun'}, #4
{'GOTO': [0,1,75-2,45-2]  ,'KILL': 0,   'PICK': 0                          , 'BOSS':0, 'TEXT':'complex medium level with more agressive enemies'}, #5
{'GOTO': [0,1,75-2,75-2]  ,'KILL': 0,   'PICK': 0                          , 'BOSS':0, 'TEXT':'big level with 2 types of enemies'}, #6
{'GOTO': [0,1,75-2,75-2]  ,'KILL': 30,  'PICK': 0                          , 'BOSS':6, 'TEXT':'complex big level with 2 types of enemies and BOSS'}, #7
{'GOTO': [0,1,101-2,101-2],'KILL': 0,   'PICK': 0                          , 'BOSS':0, 'TEXT':'very big level with 3 types of enemies and oxygen environment'}, #8
{'GOTO': [0,1,201-2,201-2],'KILL': 0,   'PICK': [[70,5,True],[70,50,False]], 'BOSS':0, 'TEXT':'super level with 4 types of enemies, find CHIPS'}, #9
{'GOTO': [0,1,201-2,201-2],'KILL': 100, 'PICK': 0                          , 'BOSS':0, 'TEXT':'open super level with 4 types of enemies and oxygen, kill 100 enemy!'}, #10
{'GOTO': [0,1,201-2,201-2],'KILL': 500, 'PICK': [[61,1,True],[61,3,False]] , 'BOSS':0, 'TEXT':'super level with 3 types of agressive enemies and generators, find minigun, kill 500 enemy!'}, #11
{'GOTO': [0,1,0,0]        ,'KILL': 300, 'PICK': [[70,5,True],[70,10,False]], 'BOSS':0, 'TEXT':'very big level with slime and food generators, kill 300, find EXIT'}, #12
{'GOTO': [0,0,0,0]        ,'KILL': 500, 'PICK': [[71,10,True],[71,30,False]],'BOSS':0, 'TEXT':'very big level with slime and food generators, kill 500, find EXIT'}  #13
]
#GOTO - start and level complete player position. If [0,0,*,*] or [*,*,0,0] - generate START or EXIT points random
#!!! need 3D coordinates START_Z,EXIT_Z
#KILL - need to kill enemies for level complete (общее количество, которых надо убить)
#PICK - need to pick all objects with type (0 - no PICK) to level complete
#	list of lists: [type,quantity,nessesary] [60,1,True] - small gun, 1 gun, True - NEED to PICK for complete level
#BOSS - need to kill BOSS with type in enemy_type (0 - no BOSS) to level complete
#TEXT - level discription

#среды:
maze_oxygen=[[]] #кислород, концентрация
concentration_oxygen=100 #максимальная концентрация, используется для генерации в start_env(concentration)
env_speed={'OXYGEN':[100,0],'FOOD':[100,0]} #шаги, через которые произойдет изменение концентрации и распространение среды в next_env(env_maze), первое значение - константа, второе - шаг

maze_food=[[]] #еда, концентрация
concentration_food=100 #максимальная концентрация, используется для генерации в start_env(concentration)
slimes=[
{},
{'level':8,'kill':5 ,'newenemy':40,'regenerate':20,'split':4, 'probability':0.1,'exp':10,'near':True,'maxhealth':6}, #enemy health: 2 40(newenemy)/5(kill)/2=4 killed -> +1
{'level':9,'kill':10,'newenemy':60,'regenerate':20,'split':6, 'probability':0.2,'exp':20,'near':False,'maxhealth':9}  #enemy health: 3 60/10/3=2 killed -> +1
]
'''
example: slime[0]
after kill 0 level enemy (heal=5) add to food=5*10=50 ->generate 1 slime enemy level 8 (heal=1)
after regenerate 4*10 enemy heal=1+4=5 -> split to 2 slime enemies
all probability = 10% (0.1) - newenemy, regenerate,split
'level':8, #level of slime enemy
'kill':10, #killed enemy add to maze_food=health*slimes['kill'] (after kill enemy)
'newenemy' :50, #concentration of maze_food for generate slime enemy
'regenerate':10, #food for 1 health regen
'split': #health of enemy to split enemy to 2 enemies after move
'probability':0.1 #probability of generate and split at 'FOOD' cooldown
'exp':10 #expirience for 1 kill slime unit
'near':True newenemy generation worked if only near another slime unit
'maxhealth': maximum health of slime unit
'''

#player:
player_x=0
player_y=1
START=[0,1]
#массив для разных направлений игрока и врагов dx,dy,image_index for display maze
directions={
'RIGHT': [1 , 0, 0],
'LEFT' : [-1, 0, 1],
'UP'   : [0 ,-1, 2],
'DOWN' : [0 , 1, 3]
}
player_direction='RIGHT' #направление взгляда игрока по умолчанию, по нему идет стрельба или другое использование предметов, если не используется мышь. Мышь меняет позицию.
player_last_move='RIGHT' #направление последнего движения, учитывается при прорисовке игрока если он двигался и act>0
#player statistics:
player_action={'MOVE':0,'FIRE':0,'FOG':0, 'PICK':0,'KILL':0,'HIT':0} #player action counts. statistics
print('player x:',player_x,' player y:',player_y,' move:',player_action['MOVE'])
starttime=time.clock()
pausegame=False
player_expirience=0

#cooldown: для врагов смотреть в enemy_types
cooldown={'TICK':50,'MOVE':10,'MOVE BLOCK':15,'MOVE ON ENEMY':15}#default cooldown={'TICK':50,'MOVE':10,'MOVE BLOCK':15,'MOVE ON ENEMY':15}
#upgrades:
upgrades={
	'EXP':          [0,  4000,8000,16000,32000], #сколько опыта уходит на апгрейд по каждому уровню, 0 уровень - значения характеристик по умолчанию
	'ENERGY_MAX':   [100,125, 150, 175  ,200  ],
	'OXYGEN_MAX':   [100,120, 140, 160  ,180  ],
	'HEALTH_MAX':   [100,125, 150, 175  ,200  ],
	'SPEED_TICK':   [0,  1,   2,   3    ,4    ], #на сколько сокращается cooldown по способностям игрока
	'FOG_RADIUS':   [2,  3,   4,   5    ,6    ],
	'MELEE_DAMAGE': [1,  2,   3,   4    ,6    ],
	'OXYGEN_TIME':  [0.6,0.5, 0.4, 0.3  ,0.2  ],
	'OXYGEN_ENERGY':[0.4,0.3, 0.2, 0.1  ,0.05 ], #затраты энергии при сборе внешнего кислорода
	'BULLETS_MAX'  :[100,150, 200, 300  ,500  ]  #maximum bullets from weapons[6]
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
	'OXYGEN_ENERGY':0,
	'BULLETS_MAX':0
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

#fire:
weapons=[
	[0,0,1,5,10,50,200,'small gun','gun1.png','bullet1.png'], #[0,0,1,5,10,50,200,'small gun','gun1.png','bullet1.png']
	[1,0,2,3,5 ,50,200,'minigun'  ,'gun2.png','bullet2.png']
]
#    0 1 2 3 4  5  6    7          8          9
#weapons:
#		0 - типы вооружения (type(номер типа) = index in list
#		1 - effect(0 - физический точечный, 1 - энергетический точечный, 2 - разрывной с радиусом поражения)
#		2 - damage
#		3 - speed(сколько тиков проходит через одно поле)
#		4 - cooldown(сколько тиков минимум между выстрелами)
#		5 - range(сколько тиков максимально в полете)
#		6 - bullets (максимальное количество снарядов в оружии))
#		7 - name
#		8 - image name for gun
#		9 - image name for bullet
player_bullets=[]
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
# пример: [0,weapons[0][3],0,weapons[0][5],player_x,player_y,player_x+direction[player_direction][0],player_y+direction[player_direction][1],player_direction,weapons[0][2]] - начало при выстреле
player_inventory=[
1,
['EMPTY' ,0,0  ,0]
#['WEAPON',0,100,0],
#['WEAPON',1,50 ,0]
#need remove, added for tests
]
# player inventory
#	player_inventory[0] - текущий предмет
#	0 - class 'WEAPON', 'KEY', 'MATERIAL' etc.
#	1 - type in class, if 'WEAPON' weapons[0]
#	2 - value, if 'WEAPON' - bullets количество пуль текущее, т.е. это small gun со 100 пулями
#	3 - tick (current tick) - if 'WEAPON' max tick = weapons[0][4] cooldown , т.е. это значение растет за цикл, увеличиваясть до cooldown , после этого опять сбрасывается в 0 и можно снова выстрелить


print('module imported: maze_init')