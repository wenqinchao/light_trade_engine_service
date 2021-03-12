from handlers.order import *
from tornado.web import StaticFileHandler
import os

routes = [
    (r"/.*\.png", StaticFileHandler, {"path": os.path.join("static", "logos")}),
    (r"/.*\.plist", StaticFileHandler, {"path": os.path.join("static", "plists")}),
    (r"/.*\.html", StaticFileHandler, {"path": os.path.join("static", "apidoc")}),
    (r"/order/add_order", AddOrderHandler),
    (r"/order/delete_order", DelOrderHandler)
]
