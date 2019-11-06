import random
import time
from queue import Queue

import gevent
from .constants import BUCKET_NUMBER, BUCKET_SIZE, BUCKET_MIN_DISTANCE, Logger, \
    KAD_ALPHA, K_MAX_KEY_VALUE, K_PUBKEY_SIZE, REFRESH_INTERVAL, RE_VALIDATE_INTERVAL
from .crypto import keccak256, int_to_big_endian


def push_node(collection, node, max_size):
    collection.insert(0, node)
    if len(collection) > max_size:
        return collection.pop()


def del_node(collection, node):
    for n in collection:
        if n.node_id == node.node_id:
            collection.remove(n)
            return


def find_farther_to_target_than(arr, t, node):
    n_id = node.node_id
    for c in arr:
        c_id = c.node_id
        for i in len(t):
            tc = ord(t[i]) ^ ord(c_id[i])
            tn = ord(t[i]) ^ ord(n_id[i])
            if tc > tn:
                return c
            else:
                break


class Bucket(object):
    def __init__(self):
        self.nodes = []
        self.replace_cache = []


class RoutingTable(object):
    def __init__(self, self_node, server):
        self.buckets = [Bucket() for _ in range(BUCKET_NUMBER)]
        self.self_node = self_node
        self.server = server
        for bn in self.server.boot_nodes:
            self.add_node(bn)
        gevent.spawn(self.re_validate)
        gevent.spawn(self.refresh)

    # 在本地节点路由表中找出num个离target最近的节点
    def closest(self, target_id, num):
        arr = []
        for bucket in self.buckets:
            for node in bucket.nodes:
                farther = find_farther_to_target_than(arr, target_id, node)
                if farther:
                    arr.remove(farther)
                if len(arr) < num:
                    arr.append(node)
        return arr

    # 全网查找离target最近的num个节点
    def lookup(self, target_key):
        target_id = keccak256(target_key)
        closest = []
        while not closest:
            closest = self.closest(target_id, BUCKET_SIZE)
            if not closest:
                for bn in self.server.boot_nodes:
                    self.add_node(bn)
        asked = [self.self_node.node_id]
        pending_queries = 0
        reply_queue = Queue()
        while True:
            for n in closest:
                if pending_queries >= KAD_ALPHA:
                    break
                if n.node_id not in asked:
                    asked.append(n.node_id)
                    pending_queries += 1
                    gevent.spawn(self.find_neighbours, n, target_key, reply_queue)
            if pending_queries == 0:
                break
            ns = reply_queue.get()
            pending_queries -= 1
            if ns:
                for node in ns:
                    farther = find_farther_to_target_than(closest, target_id, node)
                    if farther:
                        closest.remove(farther)
                    if len(closest) < BUCKET_SIZE:
                        closest.append(node)

    def add_node(self, node):
        bucket = self.get_bucket(node)
        if self.self_node.node_id == node.node_id:
            return
        for n in list(bucket.nodes):
            if n.node_id == node.node_id:
                bucket.nodes.remove(n)
                bucket.nodes.insert(0, node)
                Logger.info('refresh node')
        if len(bucket.nodes) >= BUCKET_SIZE:
            for rc in bucket.replace_cache:
                if rc.node_id == node.node_id:
                    return
            push_node(bucket.replace_cache, node, BUCKET_SIZE)
            Logger.info('push{} to replacement #{}'.format(node, self.buckets.index(bucket)))
            return
        push_node(bucket.nodes, node, BUCKET_SIZE)
        Logger.info('push{} to replacement #{}'.format(node, self.buckets.index(bucket)))
        del_node(bucket.replace_cache, node)
        node.add_time = time.time()

    # 查找对应节点所在的k桶
    def get_bucket(self, node):
        self_id = self.self_node.node_id
        node_id = node.node_id
        lead_zero = 0
        for i in range(len(self_id)):
            diff = ord(self_id[i]) ^ ord(node_id[i])
            if diff == 0:
                lead_zero += 8
            else:
                lead_zero += 8 - len('{:b}'.format(diff))
                break
        distance = len(self_id) * 8 - lead_zero
        if distance <= BUCKET_MIN_DISTANCE:
            return self.buckets[0]
        else:
            return self.buckets[distance - BUCKET_MIN_DISTANCE - 1]

    # 定时检查随机桶的最后一个节点，如果能ping通就将节点放到索引0位置，如果ping不通就
    # 从桶的replace——cache中随机去一个添加
    def re_validate(self):
        while True:
            time.sleep(RE_VALIDATE_INTERVAL)
            last = None
            ids = [i for i in range(len(self.buckets))]
            random.shuffle(ids)
            for id in ids:
                bucket = self.buckets[id]
                if len(bucket.nodes) > 0:
                    last = bucket.nodes.pop()
                    break
            if last is not None:
                Logger.info('revalidate {}'.format(last))
                ret = self.server.ping(last).get()
                if ret:
                    bucket.nodes.insert(0, last)
                else:
                    if len(bucket.replace_cache) > 0:
                        r = bucket.replace_cache.pop(random.randint(0, len(bucket.replace_cache) - 1))
                        if r:
                            bucket.nodes.append(r)

    # 定时刷新路由表
    def refresh(self):
        assert self.server.boot_nodes, "no boot nodes"
        while True:
            self.lookup(self.self_node.node_key)
            for i in range(3):
                random_int = random.randint(0, K_MAX_KEY_VALUE)
                node_key = int_to_big_endian(random_int).rjust(K_PUBKEY_SIZE / 8, b'\x00')
                self.lookup(node_key)
            time.sleep(REFRESH_INTERVAL)

    def find_neighbours(self, node, target_key, reply_queue):
        ns = self.server.find_neighbours(node, target_key)
        if ns:
            for n in ns:
                self.add_node(n)
        reply_queue.put(ns)
