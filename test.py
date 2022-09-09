number_column = int(input("Введите количество столбцов латинсоком квадрате: "))

for i in range(number_column):
    for j in range(1, number_column + 1):
        print((j + i) % number_column + 1, end=' ')
    print()

# 1 2 3 4
# 4 1 2 3
# 3 4 1 2
# 2 3 4 1
