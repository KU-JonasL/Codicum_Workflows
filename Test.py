
from math import *


Sample_Number = 128
Sample_Col = ceil(Sample_Number/8)

## ()-Setup
Spot_Pattern = [('A1','A5','A9'),('A2','A6','A10'),('A3','A7','A11'),('A4','A8','A12'),('A13','A17','A21'),('A14','A18','A22'),('A15','A19','A23'),('A16','A20','A24'),('B1','B5','B9'),('B2','B6','B10'),('B3','B7','B11'),('B4','B8','B12'),('B13','B17','B21'),('B14','B18','B22'),('B15','B19','B23'),('B16','B20','B24')]

Spot_Pattern = list(Spot_Pattern)


## []-Setup
#Spot_Pattern = [['A1','A5','A9'],['A2','A6','A10'],['A3','A7','A11'],['A4','A8','A12'],['A13','A17','A21'],['A14','A18','A22'],['A15','A19','A23'],['A16','A20','A24'],['B1','B5','B9'],['B2','B6','B10'],['B3','B7','B11'],['B4','B8','B12'],['B13','B17','B21'],['B14','B18','B22'],['B15','B19','B23'],['B16','B20','B24']]

for i in range(Sample_Col):
    print(i)
    print(Spot_Pattern[i])
    print(Spot_Pattern[i][1])


for l in range(2):
    print(l)
