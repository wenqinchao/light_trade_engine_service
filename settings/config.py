redis_cluster = {
    "nodes": [
        {'host': '127.0.0.1', 'port': 7001},
        {'host': '127.0.0.1', 'port': 7002},
        {'host': '127.0.0.1', 'port': 7003},
        {'host': '127.0.0.1', 'port': 7004},
        {'host': '127.0.0.1', 'port': 7005},
        {'host': '127.0.0.1', 'port': 7006},
    ],
    "password": None
}

redis_single = {
    "host": "127.0.0.1",
    "port": 6379,
    "password": None
}

back_url = {
    "order": "http://127.0.0.1:6372/order/order",
    "deep": "http://127.0.0.1:6372/order/deep",
    "order_deep": "http://127.0.0.1:6372/order/order_deep"
}
