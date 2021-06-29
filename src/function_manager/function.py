import docker
import time
import math
import gevent
from gevent import event
from container import Container
from function_info import FunctionInfo

update_rate = 0.65 # the update rate of lambda and mu

# data structure for request info
class RequestInfo:
    def __init__(self, request_id, data):
        self.request_id = request_id
        self.data = data
        self.result = event.AsyncResult()
        self.arrival = time.time()

class Function:
    def __init__(self, client, database, function_info, port_controller, function_name):
        self.client = client
        self.db = database
        self.info = function_info
        self.port_controller = port_controller
        self.function_name = function_name

        self.num_processing = 0
        self.rq = []

        # container pool
        self.num_exec = 0
        self.exec_pool = []
        # self.lender_pool = []
        # self.renter_pool = []

        # statistical infomation for idle container identifying
        self.lambd = -1
        self.rec_mu = -1
        self.qos_real = 1
        self.qos_time = self.info.qos_time
        self.qos_requirement = self.info.qos_requirement
        self.request_log = {
            'start': [time.time()],
            'duration': [],
            'alltime': []
        }
    
    # put the request into request queue
    def send_request(self, request_id, runtime, input, output, to, keys):
        # print('send_request', request_id, runtime)
        start = time.time()
        self.request_log['start'].append(start)

        data = {'request_id': request_id, 'runtime': runtime, 'input': input, 'output': output, 'to': to, 'keys': keys}
        req = RequestInfo(request_id, data)
        self.rq.append(req)
        res = req.result.get()
        self.db[request_id + "_" + self.function_name] = res

        end = time.time()
        self.request_log['duration'].append(res['duration'])
        self.request_log['alltime'].append(end - start)

        return res

    # receive a request from upper layer
    # the precedence of container source:
    #   1. function's executant pool
    #   2. function's renter pool
    #   3. function's lender pool
    #   4. other functions' lender container
    #   5. create new container
    def dispatch_request(self):
        # no request to dispatch
        if len(self.rq) - self.num_processing == 0:
            return
        self.num_processing += 1
        
        # 1.1 try to get a workable container from pool
        container = self.self_container()
        # 1.2 try to get a renter container from interfunction controller
        # rent_start = time.time()
        # if container is None:
        #     container = self.rent_container()
        # rent_end = time.time()
        
        # 1.3 create a new container
        if container is None:
            container = self.create_container()
           
        # the number of exec container hits limit
        if container is None:
            self.num_processing -= 1
            return

        req = self.rq.pop(0)
        self.num_processing -= 1
        # 2. send request to the container
        res = container.send_request(req.data)
        req.result.set(res)
        
        # 3. put the container back into pool
        self.put_container(container)

    # get a container from container pool
    # if there's no container in pool, return None
    def self_container(self):
        res = None

        if len(self.exec_pool) != 0:
            res = self.exec_pool.pop(-1)
        # elif len(self.renter_pool) != 0:
        #     res = self.renter_pool.pop(-1)
        # elif len(self.lender_pool) != 0:
        #     res = self.lender_pool.pop(-1)
        
        return res

    # rent a container from interfunction controller
    # if no container can be rented, return None
    # def rent_container(self):
    #     start_time = time.time()
    #     res = self.function_manager.rent(self.name)
    #     if res is None:
    #         return None
        
    #     container_id, port = res
    #     container = Container.inherit(self.client, container_id, port, 'renter')
    #     self.init_container(container)
    #     return container

    # create a new container
    def create_container(self):
        # do not create new exec container
        # when the number of execs hits the limit
        if self.num_exec > self.info.max_containers:
            return None
        
        try:
            container = Container.create(self.client, self.info.img_name, self.port_controller.get(), 'exec')
        except Exception as e:
            return None

        self.num_exec += 1
        self.init_container(container)
        return container

    # put the container into one of the three pool, according to its attribute
    def put_container(self, container):
        if container.attr == 'exec':
            self.exec_pool.append(container)
        # elif container.attr == 'renter':
        #     self.renter_pool.append(container)
        # elif container.attr == 'lender':
        #     self.lender_pool.append(container)

    # repack a executant container into a lender container
    # executant container's port will be reused
    # def repack_container(self, container):
    #     container.destroy()

    #     if self.pack_img_name is None:
    #         self.pack_img_name = self.function_manager.create_pack_image(self.name)
        
    #     container = Container.create(self.client, self.pack_img_name, container.port, 'lender')
    #     self.init_container(container)
    #     return container

    # give out a lender container to interfunction controller
    # if there's no lender container, return None
    # def giveout_container(self):
    #     # no container in lender pool
    #     if len(self.lender_pool) == 0:
    #         return None

    #     # take the least hot lender container
    #     container = self.lender_pool.pop(0)

    #     container_id = container.container.id
    #     port = container.port
    #     return container_id, port

    # after the destruction of container
    # its port should be give back to port manager
    def remove_container(self, container):
        container.destroy()
        self.port_controller.put(container.port)
    
    # return the status of all container pools
    def get_status(self):
        return {
            "exec": [self.num_exec, len(self.exec_pool)],
            # "lender": len(self.lender_pool),
            # "renter": len(self.renter_pool),
            "lambda": self.lambd,
            "rec_mu": self.rec_mu,
            "qos_real": self.qos_real,
            "quene_len": len(self.rq)
        }

    # remove all lender containers in lender pool
    # it should be called when pack image (lender's image) has been changed
    # def remove_lender(self):
    #     lenders = self.lender_pool
    #     self.lender_pool = []

    #     for c in lenders:
    #         self.remove_container(c)

    # do the function specific initialization work
    def init_container(self, container):
        container.init(self.info.function_name)

    # update stat info for idle alg
    def update_statistics(self):
        if len(self.request_log['start']) > 1:
            logs = self.request_log['start']
            self.request_log['start'] = logs[-1:]
            intervals = [y - x for x, y in zip(logs, logs[1:])]
            new_lambd = favg(intervals)
            if self.lambd > 0:
                self.lambd = update_rate * self.lambd + (1 - update_rate) * new_lambd
            else:
                self.lambd = new_lambd

        if len(self.request_log['duration']) > 0:
            new_rec_mu = favg(self.request_log['duration'])
            self.request_log['duration'] = []
            if self.rec_mu > 0:
                self.rec_mu = update_rate * self.rec_mu + (1 - update_rate) * new_rec_mu
            else:
                self.rec_mu = new_rec_mu

        if len(self.request_log['alltime']) > 0:
            alltime = self.request_log['alltime']
            self.request_log['alltime'] = []
            new_qos_real = sum([x < self.qos_time for x in alltime]) / len(alltime)
            self.qos_real = update_rate * self.qos_real + (1 - update_rate) * new_qos_real

    # do the repack and cleaning work regularly
    def repack_and_clean(self):
        # find the old containers
        old_container = []
        self.exec_pool = clean_pool(self.exec_pool, exec_lifetime, old_container)
        self.num_exec -= len(old_container)
        # self.lender_pool = clean_pool(self.lender_pool, lender_lifetime, old_container)
        # self.renter_pool = clean_pool(self.renter_pool, renter_lifetime, old_container)

        # # repack containers
        # self.update_statistics()
        # repack_container = None
        # if len(self.exec_pool) > 0:
        #     n = len(self.exec_pool) + len(self.lender_pool) + len(self.renter_pool)
        #     idle_sign = idle_status_check(1/self.lambd, n-1, 1/self.rec_mu, self.qos_time, self.qos_real, self.qos_requirement)
        #     print("idle: ", idle_sign, " ", 1/self.lambd, " ", n-1, " ", 1/self.rec_mu, " ", self.qos_time, " ", self.qos_real, " ", self.qos_requirement)
        #     if idle_sign:
        #         self.num_exec -= 1
        #         repack_container = self.exec_pool.pop(0)

        # time consuming work is put here
        for c in old_container:
            self.remove_container(c)
        # if repack_container is not None:
        #     repack_container = self.repack_container(repack_container)
        #     self.lender_pool.append(repack_container)
            
        # if len(self.lender_pool) == 1:
        #     self.function_manager.have_lender(self.name)
        # elif len(self.lender_pool) == 0:
        #     self.function_manager.no_lender(self.name)

def favg(a):
    return math.fsum(a) / len(a)

# life time of three different kinds of containers
exec_lifetime = 60
lender_lifetime = 120
renter_lifetime = 40

# the pool list is in order:
# - at the tail is the hottest containers (most recently used)
# - at the head is the coldest containers (least recently used)
def clean_pool(pool, lifetime, old_container):
    cur_time = time.time()
    idx = -1
    for i, c in enumerate(pool):
        if cur_time - c.lasttime < lifetime:
            idx = i
            break
    # all containers in pool are old, or the pool is empty
    if idx < 0:
        idx = len(pool)
    old_container.extend(pool[:idx])
    return pool[idx:]
