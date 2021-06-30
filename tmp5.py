def check(password):
    for i in range(len(password) - 3):
        c = password[i: i + 4]
        c_list = list(map(lambda x: ord(x), list(c)))
        diff = c_list[1] - c_list[0]
        if diff in [0, 1, -1]:
            if c_list[2] - c_list[1] == diff and c_list[3] - c_list[2] == diff:
                print(password + ': 不行啊: ' + ''.join(c))
                return False
            else:
                continue
        else:
            continue
    print(password + ': 没问题的')
    return True


check('cbaa')
check('987654321')
check('qwer1234asd')
check('asd1111dasdsa')
check('asshhhhhhhh12')
check('伟鹏牛逼逼逼逼')
check('121212!!!!')
check('伟鹏牛逼')
check('qwe123qwe')
