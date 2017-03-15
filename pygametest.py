import pygame
import random

pygame.init()

white = (255,255,255)
black = (0,0,0)

red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)

gameDisplay = pygame.display.set_mode((800,600))
gameDisplay.fill(red)

pixAr = pygame.PixelArray(gameDisplay)
pixAr[10][20] = green
del pixAr #unlock surface

pygame.draw.line(gameDisplay, blue, (100,200), (300,450),5)
pygame.draw.rect(gameDisplay, red, (400,400,50,25))
pygame.draw.circle(gameDisplay, white, (150,150), 75)
pygame.draw.polygon(gameDisplay, green, ( (25,75),(76,125),(250,375),(400,25),(60,540) ) )

pygame.display.update()

#загрузка картинки, создание массива картинок разного размера, отображение
wall = pygame.image.load('player1.png').convert()
wallarray=pygame.surfarray.array2d(wall)
print (wallarray)
wall.unlock()
print('размер картинки:',wall.get_size())
newwall=[]
for cellsize in range(50,10,-5):
	print(cellsize)
	newwall.append(pygame.transform.smoothscale(wall,(cellsize,cellsize)))
cellsize=60
for i in range(len(newwall)):
	gameDisplay.blit(newwall[i],(200+cellsize*i,200))
pygame.display.update()

#генерация картинки и отображение, цвет красный
randomsurface=pygame.Surface((20,20)).convert()
randomarray=pygame.PixelArray(randomsurface)
for i in range(20):
	for j in range(20):
		randomarray[i][j]=random.randint(0,255)*256*256
#print(randomarray)
del randomarray
print(randomsurface.get_alpha())
gameDisplay.blit(randomsurface,(300,300))

energy = pygame.image.load('hole2.png').convert()
zoomenergy=pygame.transform.scale(energy,(cellsize,cellsize))
zoomenergy_array=pygame.PixelArray(zoomenergy)
print(zoomenergy_array)
del zoomenergy_array
zoomenergy.set_colorkey((15539236))
gameDisplay.blit(zoomenergy,(400,300))

pygame.display.update()

# test 'a' get_pressed()
clock = pygame.time.Clock()
act=['',0]
while True:
	key=pygame.key.get_pressed()
	if key[pygame.K_q]:
		pygame.quit()
		quit()
	if act[1]==0:
		if key[pygame.K_a]:
			print('left move')
			act=['MOVE',10]
	for event in pygame.event.get():
		#print(event)
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
	clock.tick(50)
	
	if act[1]>0:
		#здесь делается run action
		act[1]-=1
	#print (action[1])



