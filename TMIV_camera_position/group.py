import math

# r = 2.75
# angle = 0
# step = 180/5
# arr = []
# while angle <= 180:
#     arr.append((round(r*math.sin(angle*math.pi/180),2), round(r*math.cos(angle*math.pi/180),2),angle-90))
#     angle = angle + step
# print(arr)

r = 4
angle = 0
step = 180/12
arr = []
while angle <= 180:
    arr.append((round(r*math.sin(angle*math.pi/180),2), round(r*math.cos(angle*math.pi/180),2),angle-90))
    angle = angle + step
print(arr)


