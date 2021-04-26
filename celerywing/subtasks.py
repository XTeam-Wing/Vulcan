#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : RedTeamWing
# @CreateTime: 2020/5/4 11:42 下午
# @FileName: subtasks.py
# @Blog：https://redteamwing.com
import nmap
import time
from app.core.database.database_wing import DBSubdomain, TaskDB, PocscanTask, PocsuiteDB, PocsuiteVuln
from app.core.database.db_mongo import mongo
from app.common.utils.logger import logger
import json, os, socket, requests, sys
from bs4 import BeautifulSoup
from app.config.settings import shodankey, chromepath, crawlergopath, plugindir, masscanpath
from queue import Queue
import threading
from celerywing.config import CeleryConfig
from celery import Celery

requests.packages.urllib3.disable_warnings()

app = Celery('tasks3')

app.config_from_object(CeleryConfig)
requests.packages.urllib3.disable_warnings()


def notice(contents, info="Wing"):
    ddheaders = {"Content-Type": "application/json; charset=utf-8"}
    try:
        data = '{ "markdown": { "title": "' + info + '!", "text": "' + \
               contents + 'By IceWing" }, "msgtype": "markdown" }'
        resp = requests.post(
            url="https://oapi.dingtalk.com/robot/send?access_token=",
            data=data.encode('utf-8'), headers=ddheaders)
    except Exception as e:
        logger.warning(e)


def get_title(markup):
    """
    获取标题

    :param markup: html标签
    :return: 标题
    """
    soup = BeautifulSoup(markup, 'lxml')

    title = soup.title
    if title:
        return title.text

    h1 = soup.h1
    if h1:
        return h1.text

    h2 = soup.h2
    if h2:
        return h2.text

    h3 = soup.h3
    if h2:
        return h3.text

    desc = soup.find('meta', attrs={'name': 'description'})
    if desc:
        return desc['content']

    word = soup.find('meta', attrs={'name': 'keywords'})
    if word:
        return word['content']

    text = soup.text
    if len(text) <= 200:
        return text

    return 'None'


class PortScan(threading.Thread):
    def __init__(self, queue, tmpid, project, ipcount, flagnum):
        threading.Thread.__init__(self)
        self.final_domains = []
        self.ports = []
        self._queue = queue
        self.data = []
        self.tmpid = tmpid
        self.project = project
        self.flag = 0
        self.ipcount = ipcount
        self.portnum = 0
        self.tmpres = 0
        self.flagnum = flagnum

    def run(self):
        while not self._queue.empty():
            # data = [ip, subdomain, subcount, company, tmpid, project]
            self.data = self._queue.get()
            self.scan_ip = self.data[0]
            self.tmpid = self.data[4]
            self.subdomain = self.data[1]
            self.company = self.data[3]
            self.subcount = self.data[2]
            self.project = self.data[5]
            try:
                self.portscan(self.scan_ip)
                self.Scan(self.scan_ip)
                self.save_data()
            except Exception as e:
                print(str(e))
                logger.error(str(e))

    def save_data(self):
        # print(self.final_domains)
        flag = TaskDB.get_by_id(self.tmpid)
        for i in flag:
            self.tmpres = i["flag"]
            self.portnum = i["portcount"]
            if self.tmpres == "100.00%":
                self.tmpres = "100.00%"
            else:
                self.tmpres = self.flagnum
        print("进度:" + str(self.tmpres))
        for res in self.final_domains:
            port = int(res["port"])
            if port != 0:
                server = res["server"]
                url = res["url"].replace(self.scan_ip, self.subdomain)
                title = res["title"]
                db_query = mongo['Subdomain'].find(
                    {"domain": "{}".format(self.subdomain), "project": str(self.project), "port": str(port)})
                count = db_query.count()
                for j in db_query:
                    if j:
                        _id = str(j["_id"])
                self.portnum = self.portnum + 1
                tmp_data2 = {"subdomain_count": self.subcount, "portcount": int(self.portnum),
                             "flag": self.tmpres, "date": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime())}
                TaskDB.update(taskid=self.tmpid, data=tmp_data2)
                if count == 0:
                    pid = DBSubdomain.add(taskid=self.tmpid, domain=self.subdomain, url=str(url), ip=str(self.scan_ip),
                                          title=str(title),
                                          server=str(server),
                                          project=self.project,
                                          company_name=self.company, port=port)
                    msg = "子域名{0} 入库成功----> pid:{1}".format(self.subdomain, pid)
                    contents = "### 子域名信息 \n" + \
                               "子域名: {domain} \n\n".format(domain=self.subdomain) + \
                               "标题: {title} \n\n".format(title=title) + \
                               "公司: {company} \n\n".format(company=self.company) + \
                               "端口: {port} \n\n".format(port=port) + \
                               "服务: {server} \n\n".format(server=server)
                    notice(contents=contents, info="新的子域名:" + self.subdomain)
                    logger.success(msg)

                elif count == 1:

                    domain_update = {"ip": str(self.scan_ip), "server": str(server), "title": str(title),
                                     "port": port,
                                     "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                     }
                    pid = DBSubdomain.update_by_id(tid=_id, data=domain_update)
                    msg = "子域名{0} 更新成功".format(self.subdomain)

                    contents = "### 子域名数据更新 \n" + \
                               "子域名: {domain} \n\n".format(domain=self.subdomain) + \
                               "标题: {title} \n\n".format(title=title) + \
                               "公司: {company} \n\n".format(company=self.company) + \
                               "端口: {port} \n\n".format(port=port) + \
                               "服务: {server} \n\n".format(server=server)
                    # if len(self.final_domains) != 0:
                    #     self.final_domains.pop(0)
                    notice(contents=contents, info="子域名数据更新:" + self.subdomain)
                    logger.success(msg)
            else:
                logger.warning("[+] 未发现域名 [{0}] 存在开放端口,继续扫描.".format(self.subdomain))
        if self.tmpres == "100.00%":
            tmp_data = {"flag": self.tmpres, "date": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime())}
            TaskDB.update(taskid=self.tmpid, data=tmp_data)
            # os.system("rm {0}/oneforall/results/*".format(plugindir))
            # os.remove("/Users/wing/evilwing/pentesting/OneForAll/oneforall/results/{0}.json".format(rootdomain))
            notice(contents="[+]  " + self.project + " <----> Subdomain Scan Complete")
            logger.success(self.project + "=====Subdomain Scan Complete!=======")
            return self.project + "=====Subdomain Scan Complete!======="

    def portscan(self, scan_ip):
        tmp_data = {"subdomain_count": self.subcount, "portcount": int(self.portnum),
                    "flag": self.tmpres, "date": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime())}
        TaskDB.update(taskid=self.tmpid, data=tmp_data)
        #####
        temp_ports = []
        os.system(masscanpath + scan_ip + ' -p 1-65535 -oJ masscan.json --rate 1000')
        # 提取json文件中的端口
        with open('masscan.json', 'r') as f:
            for line in f:
                if line.startswith('{ '):
                    temp = json.loads(line[:-2])
                    temp1 = temp["ports"][0]
                    temp_ports.append(str(temp1["port"]))
        logger.info(str(scan_ip) + ":masscan port:" + str(temp_ports))
        if len(temp_ports) > 30:
            logger.info(str(self.subdomain) + ":" + str(scan_ip) + "->有CDN")
            temp_ports.clear()  # 如果端口数量大于50，说明可能存在防火墙，属于误报，清空列表
            temp_ports.append("80")
            self.ports.extend(temp_ports)
        elif len(temp_ports) == 0:
            logger.info(str(scan_ip) + "无开放端口")
            temp_ports.clear()
            self.ports.extend(temp_ports)
        else:
            self.ports.extend(temp_ports)
            # logger.info("ports:" + str(self.ports))  # 小于50则放到总端口列表里

    # 获取网站的web应用程序名和网站标题信息
    def Title(self, scan_url_port, service_name, port):
        try:
            r = requests.get(scan_url_port, timeout=10, verify=False)
            r.encoding = 'utf-8'
            title = get_title(r.text)
            self.final_domains.append(
                {"url": scan_url_port, "title": title, "server": service_name, "port": port})
        except Exception as e:
            logger.warning(e)
            self.final_domains.append({"url": scan_url_port, "title": "空", "server": service_name, "port": port})

    # 调用nmap识别服务
    def Scan(self, scan_ip):
        nm = nmap.PortScanner()
        try:
            if len(self.ports) == 0:
                self.final_domains.append(
                    {"url": "http://" + scan_ip, "title": "空", "server": "空", "port": 0})
            else:
                for port in self.ports:
                    ret = nm.scan(scan_ip, port, arguments='-Pn,-sS')
                    service_name = ret['scan'][scan_ip]['tcp'][int(port)]['name']
                    logger.info('[*]主机 ' + scan_ip + ' 的 ' + str(port) + ' 端口服务为：' + service_name)
                    if service_name or service_name == 'sun-answerbook':
                        if service_name == 'https' or service_name == 'https-alt':
                            scan_url_port = 'https://' + scan_ip + ':' + str(port)
                            self.Title(scan_url_port, service_name, port)
                        else:
                            scan_url_port = 'http://' + scan_ip + ':' + str(port)
                            self.Title(scan_url_port, service_name, port)
                    else:

                        self.final_domains.append(
                            {"url": "http://" + scan_ip + ":" + str(port), "title": "空", "server": service_name,
                             "port": port})
                        # return final_domains
        except Exception as e:
            logger.warning(e)


@app.task
def main_scan(tmpid, ip, project, subdomain, company, subcount, ipcount, flagnum):
    queue = Queue()
    try:
        data = [ip, subdomain, subcount, company, tmpid, project]
        queue.put(data)
        threads = []
        thread_count = 1
        for i in range(thread_count):
            threads.append(PortScan(queue, tmpid, project, ipcount, flagnum=flagnum))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # f.close()
        return "=====分布式扫描中====="
    except Exception as e:
        logger.warning(e)

