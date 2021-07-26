import numpy as np
from PIL import Image as im

print()


F = open("KAU_Height.txt", 'r') 
F = F.readlines()

xlen = int(F[-1].split(",")[0]) + 1
ylen = int(F[-1].split(",")[1].split(":")[0]) + 1


arr = np.zeros((ylen, xlen))

# print(arr.shape)

for line in range(len(F)):
    arr[int(F[line].split(",")[0])][int(F[line].split(",")[1].split(":")[0])] = F[line].split(":")[1]


data = im.fromarray(arr)
data.save('KAU_Hmap.png')


# for x in range(xlen):
#     for y in range(ylen):
#         arr[x][y] = F[][]

# arr = np.zeros((ylen, xlen))
# arr = np.zeros((6, 4))
# arr[1][1:3] = 5
# print(arr)