from rediscluster import RedisCluster
import redis
from settings.config import *


class Cluster:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        try:
            self.conn = RedisCluster(startup_nodes=redis_cluster.get("nodes"),
                                     skip_full_coverage_check=True,
                                     decode_responses=False, password=redis_cluster.get("password"))
        except Exception as e:
            raise e


def get_redis():
    r = redis.StrictRedis(host=redis_single.get("host"), port=redis_single.get("port"), db=0, decode_responses=True)
    return r
