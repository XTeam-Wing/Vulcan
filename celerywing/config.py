#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing
from datetime import timedelta
# from kombu import Queue
from celery.schedules import crontab
# Redis配置
class RedisConfig(object):
    HOST = "localhost"
    PORT = 6379
    PASSWORD = ""
    BR = 1
    # HOSTSCANKEY = "hostScan"
    # VULTASKKEY = "vulTask"


# Celery配置
class CeleryConfig(RedisConfig):
    BROKER_URL = "redis://:{0}@{1}:{2}/{3}".format(RedisConfig.PASSWORD, RedisConfig.HOST, RedisConfig.PORT,
                                                   RedisConfig.BR)
    CELERY_TASK_SERIALIZER = "json"
    CELERY_TIMEZONE = "Asia/Shanghai"
    CELERY_ENABLE_UTC = True

    # 不存取返回结果，加快响应速度。
    # CELERY_IGNORE_RESULT = False

    # 该配置可以保证task不丢失，中断的task在下次启动时将会重新执行。
    # TASK_REJECT_ON_WORKER_LOST = True

    # 只有当worker完成了这个task时，任务才被标记为ack状态
    # CELERY_ACKS_LATE = True

    # 任务超时会分配给其他worker
    BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 600}

    # 每个worker执行了多少次任务后就会死掉，建议数量大一些
    # CELERYD_MAX_TASKS_PER_CHILD = 200

    # 导入Task所在的模块，所有使用celery.task装饰器装饰过的函数，所需要把所在的模块导入
    # 我们之前创建的几个测试用函数，都在handlers.async_tasks和handlers.schedules中
    # 所以在这里需要导入这两个模块，以str表示模块的位置，模块组成tuple后赋值给CELERY_IMPORTS
    # 这样Celery在启动时，会自动找到这些模块，并导入模块内的task
    CELERY_IMPORTS = ('celerywing.tasks')

    # 为Celery设定多个队列，CELERY_QUEUES是个tuple，每个tuple的元素都是由一个Queue的实例组成
    # 创建Queue的实例时，传入name和routing_key，name即队列名称
    # 配置队列（settings.py）
    # CELERY_QUEUES = (
    #     Queue(name='Crawlscan', routing_key='Crawlscan'),
    #     Queue(name='Portscan', routing_key='Portscan'),
    #     Queue(name='SubdomainScan', routing_key='SubdomainScan'),
    #     Queue(name='celery_pocscan', routing_key='celery_pocscan'),
    #     Queue(name='schedule_poc_scanner', routing_key='schedule_poc_scanner'),
    # )

    # 最后，为不同的task指派不同的队列
    # 将所有的task组成dict，key为task的名称，即task所在的模块，及函数名
    # 如async_send_email所在的模块为handlers.async_tasks
    # 那么task名称就是handlers.async_tasks.async_send_email
    # 每个task的value值也是为dict，设定需要指派的队列name，及对应的routing_key
    # 这里的name和routing_key需要和CELERY_QUEUES设定的完全一致
    # 路由（哪个任务放入哪个队列）
    # CELERY_ROUTES = {
    #     'celerywing.tasks.Crawlscan':
    #         {
    #             'queue': 'Crawlscan',
    #             'routing_key': 'Crawlscan'
    #         },
    #     'celerywing.tasks.Portscan':
    #         {
    #             'queue': 'Portscan',
    #             'routing_key': 'Portscan'
    #         },
    #     'celerywing.tasks.SubdomainScan':
    #         {
    #             'queue': 'SubdomainScan',
    #             'routing_key': 'SubdomainScan'
    #         },
    #     'celerywing.tasks.celery_pocscan':
    #         {
    #             'queue': 'celery_pocscan',
    #             'routing_key': 'celery_pocscan'
    #         },
    #     'celerywing.tasks.schedule_poc_scanner':
    #         {
    #             'queue': 'schedule_poc_scanner',
    #             'routing_key': 'schedule_poc_scanner'
    #         }
    # }
    CELERYBEAT_SCHEDULE = {
        'poc_scanner_loop_1': {
            'task': "celerywing.tasks.schedule_poc_scanner",
            'schedule': timedelta(seconds=600),
         },
        'subdomain_scanner_loop_2': {
            'task': "celerywing.tasks.schedule_subdomain_scanner",
            'schedule': timedelta(seconds=600),
        }
        # "morning_msg_1": {
        #     "task": "celerywing.tasks.schedule_subdomain_scanner",
        #     "schedule": crontab(minute=21, hour=21)
        # }
    }


SCANCONFIG = {
    "scanports": "8080,80,81,8081,7001,8000,8088,8888,9090,8090,88,3389,8001,82,9080,8082,8089,9000,8443,9999,8002,89,8083,8200,8008,90,8086,801,8011,8085,9001,9200,8100,8012,85,8084,8070,7002,8091,8003,99,7777,8010,443,8028,8087,83,7003,10000,808,38888,8181,800,18080,8099,8899,86,8360,8300,8800,8180,3505,7000,9002,8053,1000,7080,8989,28017,9060,888,3000,8006,41516,880,8484,6677,8016,84,7200,9085,5555,8280,7005,1980,8161,9091,7890,8060,6080,8880,8020,7070,889,8881,9081,8009,7007,8004,38501,1010,27010"
}
