import re
import time
from functools import reduce, wraps


class DotDict(dict):
    """使用'点'访问字典属性，无属性时返回None"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def make_kwargs(old_kwargs, default_para_back='required', **kwargs):
    """
    此函数的使用场景：创建Fields类的子类时，按照合理的顺序传参验证
    :param old_kwargs: 子类中的参数
    :param default_para_back: 默认放到required后面
    :param kwargs: 字类中需要添加的参数
    :return: 按照合理顺序组合的参数
    """

    over = False
    if 'required' not in old_kwargs:
        new_kwargs = {**kwargs, **old_kwargs}
    else:
        kw1 = {}
        kw2 = {}
        for o_k, o_v in old_kwargs.items():
            if not over:
                kw1[o_k] = o_v
                if o_k == 'required':
                    over = True
            else:
                kw2[o_k] = o_v
        new_kwargs = {**kw1, **kwargs, **kw2}
    return new_kwargs


class Fields:

    def __init__(self, zh_name=None, required=True, **kwargs):
        self.kw = DotDict(kwargs)
        self.is_valid = True
        self.error_message = '校验成功'
        self.zh_name = zh_name or '参数'
        self.required = required

        self._data_type = self.kw.data_type
        self._max_length = self.kw.max_length
        self._min_length = self.kw.min_length
        self._equal = self.kw.equal
        self._not_equal = self.kw.not_equal
        self._regex = self.kw.regex

    def __call__(self, value, *args, **kwargs):
        """
        1.首先判断是否为必填，为非必填且值为None时，停止验证，直接返回成功
        2.通过初始化得kw值中获取需要验证得方法，
        :param value:
        :param args:
        :param kwargs:
        :return:
        """
        if self.required:
            if not self.check_required(value):
                return self.check_fail('不可为空')
        else:
            if value is None:
                return self.check_success()

        # 组合需要验证的方法
        checkers = []
        custom_error_message = None
        for k, v in self.kw.items():
            if hasattr(self, '_' + k):
                checkers.append('_check' + '_' + k)     # 如：max_length -> self._max_length
            elif k == 'custom_error_message':
                custom_error_message = v
            else:
                raise AttributeError('无此属性: {}'.format(k))

        # 执行需要验证的方法
        for checker in checkers:
            check = getattr(self, checker)
            if not check(value):
                if custom_error_message:    # 子类自定义错误信息
                    err_msg = self.get_error_message(custom_error_message, default=False)
                else:   # 使用验证函数的注释文档作为错误信息
                    err_msg = self.get_error_message(check.__doc__)

                fmt = list(map(lambda x: str(getattr(self, '_' + x)), err_msg[1]))
                return self.check_fail(err_msg[0].format(*fmt))
        return self.check_success()

    @staticmethod
    def get_error_message(value, default=True):
        """
        传入参数，转换成合理的错误信息与format参数
        :param value: 错误信息
        :param default: 当为True时，取验证函数的注释，当为False时，直接取value
        :return: 返回元组，[0]为错误信息，[1]为format参数
        """
        err_msg = ''
        if default:
            for msg in value.split('\n'):
                if msg.strip().startswith(':error_message:'):  # 通过指定字符串开头的行找到错误信息行
                    err_msg = msg.split(':error_message:')[1].strip()  # 通过split取得错误信息
                    break
        else:
            err_msg = value
        if err_msg:
            msg_split = re.split(r'[{|}]', err_msg)  # 通过正则拆分大括号内的内容
            error_message = '{}'.join(msg_split[::2])  # 组装错误信息，加上{}
            fmt = msg_split[1::2]  # 组装format信息成列表，解包
            return error_message, fmt
        else:
            return '', ''

    def check_fail(self, error_message):
        return {
            'is_valid': False,
            'error_message': '{}: {}'.format(self.zh_name, error_message)
        }

    @staticmethod
    def check_success():
        return {
            'is_valid': True,
            'error_message': '校验成功'
        }

    def _check_data_type(self, value):
        """
        :error_message: 数据类型错误
        :param value: 为tuple时，为or关系
        """
        if isinstance(value, tuple) or isinstance(value, list):
            return reduce(lambda x, y: x or y, map(lambda z: isinstance(value, z), self._data_type))
        else:
            return isinstance(value, self._data_type)

    def check_required(self, value):
        """
        :error_message: 不可为空
        :param value:
        :return:
        """
        if self.required:
            if value is not None:
                return True
        else:
            return True

    def _check_max_length(self, value):
        """
        :error_message: 长度不可大于{max_length}
        :param value:
        :return:
        """
        # 后期需考虑数据类型（字典、列表）
        return len(str(value)) <= self._max_length

    def _check_min_length(self, value):
        """
        :error_message: 长度不可小于{min_length}
        :param value:
        :return:
        """
        return len(str(value)) >= self._min_length

    def _check_equal(self, value):
        """
        :error_message: 必须等于{equal}
        :param value:
        :return:
        """
        return self._equal == value

    def _check_not_equal(self, value):
        """
        :error_message: 不可等于{not_equal}
        :param value:
        :return:
        """
        return self._not_equal != value

    def _check_regex(self, value):
        """
        :error_message: 正则匹配失败
        :param value:
        :return:
        """
        pattern = re.compile(self._regex)
        return pattern.match(value)


class CharFields(Fields):
    def __init__(self, *args, **kwargs):
        kwargs = make_kwargs(kwargs, data_type=str)
        super(CharFields, self).__init__(*args, **kwargs)


class IntegerFields(Fields):
    def __init__(self, *args, **kwargs):
        kwargs = make_kwargs(kwargs, data_type=int)
        super(IntegerFields, self).__init__(*args, **kwargs)


class FloatFields(Fields):
    def __init__(self, *args, **kwargs):
        kwargs = make_kwargs(kwargs, data_type=float)
        super(FloatFields, self).__init__(*args, **kwargs)


class NumFields(Fields):
    def __init__(self, *args, **kwargs):
        kwargs = make_kwargs(kwargs, data_type=(float, int))
        super(NumFields, self).__init__(*args, **kwargs)


class EmailFields(CharFields):
    def __init__(self, *args, **kwargs):
        kwargs = make_kwargs(kwargs, regex=r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')
        super(EmailFields, self).__init__(custom_error_message='格式错误', *args, **kwargs)


class ValidateBase:
    def __get_result__(self, data):
        result = None
        json_data = DotDict(data)
        for key in self.__dir__():
            if not key.startswith('_'):
                value = json_data.__getattr__(key)
                result = getattr(self, key)(value)
                if not result['is_valid']:
                    return result
        return result


def validator(scheme):
    def validator_decorator(func):
        @wraps(func)
        def wrapper(request):
            checker = scheme()
            result = checker.__get_result__(request.body)
            request.body['is_valid'] = result['is_valid']
            request.body['error_message'] = result['error_message']
            return func(request)
        return wrapper
    return validator_decorator


class Login(ValidateBase):
    username = CharFields('用户名', min_length=4, max_length=20, not_equal='test001')
    password = CharFields('密码', min_length=8, max_length=18)
    email = EmailFields('电子邮箱')
    height = NumFields('身高', required=False, equal=1)


test_data = {
    'username': 'test00',
    'password': 'abc0000000000',
    'email': '1669971502@qq.com',
    'height': 1
}


login = Login()
print(login.__get_result__(test_data))
