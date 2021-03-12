import bisect


class OrderTree:
    def __init__(self):
        self.buy_prices = []  # sorted prices array asc
        self.sale_prices = []  # sorted prices array asc
        self.buy_orders = {}  # {"price":[{"id":1,"price":123,"num":23},{"id":2,"price":123,"num":23}]}
        self.sale_orders = {}
        self.buy_deep_num = []
        self.sale_deep_num = []

    def check_buy_price(self, buy_price: float):
        return self.sale_prices and buy_price >= self.sale_prices[0]

    def check_sale_price(self, sale_price: float):
        return self.buy_prices and sale_price <= self.buy_prices[-1]

    def insert_buy_price_num(self, buy_price: float, buy_num: float):
        if buy_price not in self.buy_prices:
            index = bisect.bisect_left(self.buy_prices, buy_price)
            self.buy_prices.insert(index, buy_price)
            self.buy_deep_num.insert(index, buy_num)
        else:
            index = self.buy_prices.index(buy_price)
            self.buy_deep_num[index] += buy_num

    def insert_sale_price_num(self, sale_price: float, sale_num: float):
        if sale_price not in self.sale_prices:
            index = bisect.bisect_left(self.sale_prices, sale_price)
            self.sale_prices.insert(index, sale_price)
            self.sale_deep_num.insert(index, sale_num)
        else:
            index = self.sale_prices.index(sale_price)
            self.sale_deep_num[index] += sale_num

    def add_buy_order(self, order_id: str, buy_price: float, buy_num: float, buy_fee_rate: float = 0,
                      sale_fee_rate: float = 0):
        order_deal_info = []
        change_orders = []
        if not self.check_buy_price(buy_price):
            self.insert_buy_price_num(buy_price, buy_num)
            self.buy_orders.setdefault(buy_price, []).append(
                {"order_id": order_id, "price": buy_price, "num": buy_num})
        else:
            end = bisect.bisect_right(self.sale_prices, buy_price)
            start = 0

            buy_deal_num = 0
            buy_deal_fee = 0
            while start <= end and buy_num > 0 and self.sale_prices:
                orders = self.sale_orders[self.sale_prices[0]]
                while orders and buy_num > 0:
                    order = orders[0]
                    if order["num"] < buy_num:
                        buy_fee = order["num"] * buy_fee_rate
                        buf_get = order["num"] - buy_fee
                        sale_fee = order["num"] * order["price"] * sale_fee_rate
                        sale_get = order["num"] * order["price"] - sale_fee
                        order_deal_info.append(
                            {"buy_id": order_id, "sale_id": order["order_id"], "deal_price": order["price"],
                             "deal_num": order["num"], "buy_get": buf_get, "buy_fee": buy_fee,
                             "sale_get": sale_get,
                             "sale_fee": sale_fee})
                        change_orders.append({"order_id": order["order_id"], "deal_num": order["num"], "fee": sale_fee})
                        buy_deal_num += order["num"]
                        buy_deal_fee += buy_fee
                        buy_num -= order["num"]
                        self.sale_deep_num[0] -= order["num"]
                        order["num"] = 0
                        orders.pop(0)

                    elif order["num"] > buy_num:
                        buy_fee = buy_num * buy_fee_rate
                        buf_get = buy_num - buy_fee
                        sale_fee = buy_num * order["price"] * sale_fee_rate
                        sale_get = buy_num * order["price"] - sale_fee
                        order_deal_info.append(
                            {"buy_id": order_id, "sale_id": order["order_id"], "deal_price": order["price"],
                             "deal_num": buy_num, "buy_get": buf_get, "buy_fee": buy_fee,
                             "sale_get": sale_get,
                             "sale_fee": sale_fee})
                        change_orders.append({"order_id": order["order_id"], "deal_num": buy_num, "fee": sale_fee})
                        buy_deal_num += buy_num
                        buy_deal_fee += buy_fee

                        self.sale_deep_num[0] -= buy_num
                        order["num"] -= buy_num
                        buy_num = 0

                    else:
                        buy_fee = buy_num * buy_fee_rate
                        buf_get = buy_num - buy_fee
                        sale_fee = buy_num * order["price"] * sale_fee_rate
                        sale_get = buy_num * order["price"] - sale_fee
                        order_deal_info.append(
                            {"buy_id": order_id, "sale_id": order["order_id"], "deal_price": order["price"],
                             "deal_num": buy_num, "buy_get": buf_get, "buy_fee": buy_fee,
                             "sale_get": sale_get,
                             "sale_fee": sale_fee})
                        change_orders.append({"order_id": order["order_id"], "deal_num": buy_num, "fee": sale_fee})
                        change_orders.append({"order_id": order_id, "deal_num": buy_num, "fee": buy_fee})
                        self.sale_deep_num[0] -= order["num"]
                        buy_deal_num += buy_num
                        buy_deal_fee += buy_fee

                        order["num"] = 0
                        buy_num = 0
                        orders.pop(0)
                if not orders:
                    price = self.sale_prices.pop(0)
                    self.sale_deep_num.pop(0)
                    self.sale_orders.pop(price)
                start += 1
            change_orders.append({"order_id": order_id, "deal_num": buy_deal_num, "fee": buy_deal_fee})
        return {"change_orders": change_orders, "order_deal_info": order_deal_info}

    def add_sale_order(self, order_id: str, sale_price: float, sale_num: float, buy_fee_rate: float = 0,
                       sale_fee_rate: float = 0):
        order_deal_info = []
        change_orders = []
        if not self.check_sale_price(sale_price):
            self.insert_sale_price_num(sale_price, sale_num)
            self.sale_orders.setdefault(sale_price, []).append(
                {"order_id": order_id, "price": sale_price, "num": sale_num})
        else:
            start = bisect.bisect_left(self.buy_prices, sale_price)
            end = len(self.buy_prices) - 1

            sale_deal_num = 0
            sale_deal_fee = 0
            while start <= end and sale_num > 0 and self.buy_prices:
                orders = self.buy_orders[self.buy_prices[end]]
                while orders and sale_num > 0:
                    order = orders[0]
                    if order["num"] < sale_num:
                        buy_fee = order["num"] * buy_fee_rate
                        buf_get = order["num"] - buy_fee
                        sale_fee = order["num"] * order["price"] * sale_fee_rate
                        sale_get = order["num"] * order["price"] - sale_fee
                        order_deal_info.append(
                            {"buy_id": order["order_id"], "sale_id": order_id, "deal_price": order["price"],
                             "deal_num": order["num"], "buy_get": buf_get, "buy_fee": buy_fee,
                             "sale_get": sale_get,
                             "sale_fee": sale_fee})
                        change_orders.append({"order_id": order["order_id"], "deal_num": order["num"], "fee": buy_fee})
                        sale_deal_fee += sale_fee
                        sale_deal_num += order["num"]

                        self.buy_deep_num[end] -= order["num"]
                        sale_num -= order["num"]
                        order["num"] = 0
                        orders.pop(0)

                    elif order["num"] > sale_num:
                        buy_fee = sale_num * buy_fee_rate
                        buf_get = sale_num - buy_fee
                        sale_fee = sale_num * order["price"] * sale_fee_rate
                        sale_get = sale_num * order["price"] - sale_fee
                        order_deal_info.append(
                            {"buy_id": order["order_id"], "sale_id": order_id, "deal_price": order["price"],
                             "deal_num": sale_num, "buy_get": buf_get, "buy_fee": buy_fee,
                             "sale_get": sale_get,
                             "sale_fee": sale_fee})
                        change_orders.append({"order_id": order["order_id"], "deal_num": sale_num, "fee": buy_fee})
                        sale_deal_fee += sale_fee
                        sale_deal_num += sale_num

                        self.buy_deep_num[end] -= sale_num
                        order["num"] -= sale_num
                        sale_num = 0

                    else:
                        buy_fee = sale_num * buy_fee_rate
                        buf_get = sale_num - buy_fee
                        sale_fee = sale_num * order["price"] * sale_fee_rate
                        sale_get = sale_num * order["price"] - sale_fee
                        order_deal_info.append(
                            {"buy_id": order["order_id"], "sale_id": order_id, "deal_price": order["price"],
                             "deal_num": sale_num, "buy_get": buf_get, "buy_fee": buy_fee,
                             "sale_get": sale_get,
                             "sale_fee": sale_fee})
                        change_orders.append({"order_id": order["order_id"], "deal_num": sale_num, "fee": buy_fee})
                        sale_deal_fee += sale_fee
                        sale_deal_num += sale_num

                        self.buy_deep_num[end] -= order["num"]
                        order["num"] = 0
                        sale_num = 0
                        orders.pop(0)

                if not orders:
                    price = self.buy_prices.pop()
                    self.buy_orders.pop(price)
                    self.buy_deep_num.pop()
                end -= 1
            change_orders.append({"order_id": order_id, "deal_num": sale_deal_num, "fee": sale_deal_fee})
        return {"change_orders": change_orders, "order_deal_info": order_deal_info}

    def del_order(self, order_id: str, direction: int, price: float):
        out_order = {}
        if direction == 1:
            if price in self.buy_prices:
                index = self.buy_prices.index(price)
                orders = self.buy_orders.get(price)
                for i in range(len(orders)):
                    if orders[i]["order_id"] == order_id:
                        out_order = orders.pop(i)
                        if len(orders) == 0:
                            self.buy_prices.pop(index)
                            self.buy_deep_num.pop(index)
                        else:
                            self.buy_deep_num[index] -= orders[i]["num"]
                        break
        else:
            if price in self.sale_prices:
                index = self.sale_prices.index(price)
                orders = self.sale_orders.get(price)
                for i in range(len(orders)):
                    if orders[i]["order_id"] == order_id:
                        out_order = orders.pop(i)
                        if len(orders) == 0:
                            self.sale_prices.pop(index)
                            self.sale_deep_num.pop(index)
                        else:
                            self.sale_deep_num[index] -= orders[i]["num"]
                        break
        return out_order

    def get_deep(self, depth=20):
        buy_prices = self.buy_prices[-depth:]
        buy_prices.reverse()
        buy_deep_num = self.buy_deep_num[-depth:]
        buy_deep_num.reverse()
        sale_prices = self.sale_prices[:depth]
        sale_deep_num = self.sale_deep_num[:depth]
        out = {}
        for i in range(depth):
            if i < len(buy_prices):
                out.setdefault("buy", []).append({"price": buy_prices[i], "num": buy_deep_num[i]})
            if i < len(sale_prices):
                out.setdefault("sale", []).append({"price": sale_prices[i], "num": sale_deep_num[i]})
        return out

    def get_order_deep(self, depth=5):
        buy_prices = self.buy_prices[-depth:]
        buy_prices.reverse()
        buy_deep_num = self.buy_deep_num[-depth:]
        buy_deep_num.reverse()
        sale_prices = self.sale_prices[:depth]
        sale_prices.reverse()
        sale_deep_num = self.sale_deep_num[:depth]
        sale_deep_num.reverse()
        out = {}
        for i in range(depth):
            if i < len(buy_prices):
                out.setdefault("buy", []).append({"price": buy_prices[i], "num": buy_deep_num[i]})
            if i < len(sale_prices):
                out.setdefault("sale", []).append({"price": sale_prices[i], "num": sale_deep_num[i]})
        return out

    def get_insert(self, arr: list, b):
        length = len(arr)
        left = 0
        right = length - 1
        while left < right - 1:
            mid_index = (left + right) // 2
            if arr[mid_index] == b:
                return mid_index
            elif arr[mid_index] > b:
                left = mid_index
            else:
                right = mid_index
        if arr[left] > b:
            return left + 1
        else:
            return left
