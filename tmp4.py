import re
pattern = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')
str = '166997150@qq.com'
print(pattern.match(str))