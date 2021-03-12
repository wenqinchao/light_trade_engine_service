import tornado.web
from tornado.util import unicode_type
from tornado.escape import json_decode, utf8
import tornado.locale
import time
import json
import decimal
import datetime


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Methods', 'POST,GET,OPTIONS,DELETE,HEAD,PUT,PATCH')
        self.set_header('Access-Control-Allow-Headers',
                        'authorization, Authorization, Content-Type, Access-Control-Allow-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods, Token, Lang, Access-Control-Request-Headers')

    def initialize(self):
        """初始化Handler"""
        self.set_default_headers()
        self.translate = self.locale.translate

    def write(self, chunk) -> None:
        """重写write方法，可以序列化decimal类型"""
        if self._finished:
            raise RuntimeError("Cannot write() after finish()")
        if not isinstance(chunk, (bytes, unicode_type, dict)):
            message = "write() only accepts bytes, unicode, and dict objects"
            if isinstance(chunk, list):
                message += (
                        ". Lists not accepted for security reasons; see "
                        + "http://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.write"  # noqa: E501
                )
            raise TypeError(message)
        if isinstance(chunk, dict):
            chunk = json.dumps(chunk, cls=MyJsonEncoder).replace("</", "<\\/")
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        chunk = utf8(chunk)
        self._write_buffer.append(chunk)

    def resp(self, code=None, msg=None, ext_data=None):
        """返回值格式整理，所有/api/的数据接口，都应该采用此函数处理返回值
        :param code:
        :param msg:
        :param ext_data:
        :return:
        """
        resp_dict = {}
        resp_dict['status'] = code
        resp_dict['info'] = msg
        resp_dict['result'] = ext_data
        return self.write(resp_dict)

    def get_user_locale(self):
        """多语言支持，根据请求头中的LANG切换语言
        :return:
        """
        head = self.request.headers
        user_locale = head.get("Lang")
        return tornado.locale.get(user_locale)

    def get_json_arguments(self):
        """获取请求中的json数据
        :return:
        """
        args = self.request.arguments
        args = {x: args.get(x)[0].decode("utf-8") for x in args.keys()}
        if not args and self.request.body:
            args = json_decode(self.request.body)
        return args

    def get_timestmap(self):
        return int(time.time())

    def get_datetime(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self, results):
        if results is None:
            return results
        if type(results) is list:
            data = [dict(zip(result.keys(), result)) for result in results]
        else:
            data = dict(zip(results.keys(), results))
        return data



class MyJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, o)
