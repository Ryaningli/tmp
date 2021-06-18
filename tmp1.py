from functools import wraps


class Request:
    def __init__(self):
        self.body = {
            'username': 'test001',
            'age': 20.2
        }


request = Request()


class DotDict(dict):
    """使用'点'访问字典属性，无属性时返回None"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Fields:
    def __init__(self, zh_name=None, data_type=None, required=None, max_length=None):
        print('初始')
        self.is_valid = True
        self.error_message = '校验成功'
        self.zh_name = zh_name

        self.data_type = data_type
        self.required = required
        self.max_length = max_length

    def check_fail(self, error_message, custom=False):
        self.is_valid = False
        if not custom:
            self.error_message = '{}: {}'.format(self.zh_name or '参数', error_message)
        else:
            self.error_message = error_message
        return {
            'is_valid': self.is_valid,
            'error_message': self.error_message
        }

    @staticmethod
    def check_success():
        return {
            'is_valid': True,
            'error_message': '校验成功'
        }

    def _check_data_type(self, value):
        if isinstance(value, self.data_type):
            return True

    @staticmethod
    def _check_required(value):
        if value is not None or value != '':
            return True

    def _check_max_length(self, value):
        # 后期需考虑数据类型（字典、列表）
        return value <= len(str(self.max_length))

    def all_check(self, value, *args, **kwargs):
        if self.required:
            if value is None or value == '':
                return self.check_fail('不可为空')

        if self.max_length is not None:
            if len(str(value)) > self.max_length:
                return self.check_fail('长度不可大于{}'.format(self.max_length))

        return self.check_success()


class CharFields(Fields):
    def __init__(self, *args, **kwargs):
        super(CharFields, self).__init__(*args, **kwargs)

    def check(self, value):
        if not isinstance(value, str):
            return self.check_fail('数据类型错误')
        else:
            self.all_check(value)


class Login:
    username = CharFields('用户名', required=True, max_length=10)
# age = IntegerFields()


class Validate:
    def __init__(self, scheme, data):
        self.scheme = scheme
        self.data = data

    def get_result(self):
        result = None
        json_data = DotDict(self.data.body)
        for key in dir(self.scheme)[::-1]:
            if not key.startswith('_'):
                value = json_data.__getattr__(key)
                result = getattr(self.scheme, key).check(value)
                # 加判断，错误时停止检查
        return result


def validator(scheme):
    def validator_decorator(func):
        @wraps(func)
        def wrapper(request):
            checker = Validate(scheme, request)
            result = checker.get_result()
            request.body['is_valid'] = result['is_valid']
            request.body['error_message'] = result['error_message']
            return func(request)

        return wrapper

    return validator_decorator

# test = Validate(Login, request)
# @ validator(Login)
# def ApiLogin(request):
#     print(request.body['is_valid'])
#     print(request.body['error_message'])
#
# ApiLogin(request)





