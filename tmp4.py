from functools import reduce
rule = (int, str)
value = 12.1
# b = map(lambda z: isinstance(value, z), rule)

a = reduce(lambda x, y: x or y, map(lambda z: isinstance(value, z), rule))
print(a)