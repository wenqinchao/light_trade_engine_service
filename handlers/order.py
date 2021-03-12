from handlers.base import BaseHandler
from settings.config import *
from utils.redis_clusters import Cluster
import pickle
import requests
from utils.order_tree import OrderTree


class AddOrderHandler(BaseHandler):
    def post(self):
        """
        @api {get} /order/add_order 1.add a order
        @apiGroup order
        @apiParam {string} pair  (like "BTC/USDT")
        @apiParam {string} order_id  (Uniq order id)
        @apiParam {int} direction  (1 represent buy ，2 represent sale)
        @apiParam {float} price (Order price)
        @apiParam {float} num (Order num)
        @apiParam {float} buy_fee (Fee rate of buyer, default 0 without input)
        @apiParam {float} sale_fee (Fee rate of seller, default 0 without input)
        @apiSuccess {int} status
        @apiSuccess {string} msg
        @apiSuccessExample Success-Response:
           HTTP 1.1/ 200K
           {
               'status': 1,
               'info': 'Request success',
               'result':
           }
        @apiErrorExample Error-Response:
           HTTP 1.1/ 404K
           {
               'status': 0,
               'info': 'Request fail',
               'result':
           }
           :return:
        """
        args = self.get_json_arguments()
        pair = args.get("pair")
        if not pair:
            return self.resp(0, "Pair can not be null")
        direction = args.get("direction")
        if not direction:
            return self.resp(0, "Direction can not be null")
        direction = int(direction)

        order_id = args.get("order_id")
        if not order_id:
            return self.resp(0, "Order id can not be null")
        
        price = args.get("price")
        if not price:
            return self.resp(0, "Price can not be null")
        price = float(price)

        num = args.get("num")
        if not num:
            return self.resp(0, "Order num can not be null")
        num = float(num)
        buy_fee = args.get("buy_fee", 0)
        sale_fee = args.get("sale_fee", 0)

        self.resp(1, "Request Success")

        cluster = Cluster()
        redis = cluster.conn

        tree = redis.get(pair)
        if not tree:
            order_tree = OrderTree()
        else:
            order_tree = pickle.loads(tree)

        # buy
        if direction == 1:
            deal_info = order_tree.add_buy_order(order_id, price, num, buy_fee, sale_fee)
        # sale
        else:
            deal_info = order_tree.add_sale_order(order_id, price, num, buy_fee, sale_fee)


        redis.set(pair, pickle.dumps(order_tree))

        if deal_info.get("change_orders"):
            requests.post(back_url.get("order"),
                          json=deal_info)
            requests.post(back_url.get("deep"), json=order_tree.get_deep())
            requests.post(back_url.get("order_deep"), json=order_tree.get_order_deep())


class DelOrderHandler(BaseHandler):
    def post(self):
        """
        @api {get} /order/delete_order 2.Delete a order
        @apiGroup order
        @apiParam {string} pair  (like "BTC/USDT")
        @apiParam {string} order_id  (Uniq order id)
        @apiParam {int} direction  (1 represent buy ，2 represent sale)
        @apiParam {string} price (Raw order price)
        @apiSuccess {int} status
        @apiSuccess {string} msg
        @apiSuccessExample Success-Response:
           HTTP 1.1/ 200K
           {
               'status': 1,
               'info': 'Request success',
               'result':
           }
        @apiErrorExample Error-Response:
           HTTP 1.1/ 404K
           {
               'status': 0,
               'info': 'Request fail',
               'result':
           }
           :return:
        """
        args = self.get_json_arguments()
        pair = args.get("pair")
        if not pair:
            return self.resp(0, "Pair can't be null")
        order_id = args.get("order_id")
        direction = args.get("direction")
        if not direction:
            return self.resp(0, "Direction can not ne null")
        if not order_id:
            return self.resp(0, "Order id can not be null")
        price = args.get("price")
        if not price:
            return self.resp(0, "Order price can not be null")

        self.resp(1, "Request Success")

        cluster = Cluster()
        redis = cluster.conn

        tree = redis.get(pair)
        if not tree:
            return self.resp(0, "Order doesn't exist")
        else:
            order_tree = pickle.loads(tree)
            order_tree.del_order(order_id, direction, price)


