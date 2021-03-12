import tornado.ioloop
import tornado.web
import tornado.httpserver
from routes.route import routes
import tornado.autoreload
import os
import tornado.locale


def make_app():
    current_path = os.path.dirname(__file__)
    return tornado.web.Application(routes, debug=True, static_path=os.path.join(current_path, 'static'))
if __name__ == "__main__":
    app = make_app()

    # 多语言支持
    i18n_path = os.path.join(os.path.dirname(__file__), 'locales')
    tornado.locale.load_translations(i18n_path)
    tornado.locale.set_default_locale('zh_CN')

    app.listen(7100)
    print('Tornado app running')
    tornado.ioloop.IOLoop.current().start()
