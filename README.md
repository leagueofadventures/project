Ачкасов фармит серу 24/7

d = int(input())
x = int(input())
a = (365 - 75 / d**3) /(3 * d**2 - d) * 5
b = (412 - 125 / d**3) / (2 * d**2 - d) * 4
c = ( a + b) * x
y = int(c)
print(y)

