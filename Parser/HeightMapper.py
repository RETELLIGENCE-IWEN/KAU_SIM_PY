import numpy as np
from PIL import Image as im

print()


F = open("KAU_Height.txt", 'r') 
F = F.readlines()

xlen = int(F[-1].split(",")[0]) + 1
ylen = int(F[-1].split(",")[1].split(":")[0]) + 1


arr = np.zeros((ylen, xlen))

print(arr.shape)

for line in range(len(F)):
    
    s = F[line].split(",")
    x = int(s[0])
    c = s[1].split(":")
    y = int(c[0])
    v = float(c[1])

    # print(x,y)
    arr[y][x] = v


data = im.fromarray(arr)
data = data.convert("L")
data.save('KAU_Hmap.png')


# for x in range(xlen):
#     for y in range(ylen):
#         arr[x][y] = F[][]

# arr = np.zeros((ylen, xlen))
# arr = np.zeros((6, 4))
# arr[1][1:3] = 5
# print(arr)