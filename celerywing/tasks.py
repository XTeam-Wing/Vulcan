#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing
import nmap
import re
from celery import Celery

from app.core.database.db_mongo import mongo
from app.core.database.database_wing import DBSubdomain, TaskDB, PocscanTask, PocsuiteDB, PocsuiteVuln, VulnScanDB, \
    LinksDB
from app.common.utils.logger import logger

import json, os, socket, requests, sys
from bs4 import BeautifulSoup
from shodan import Shodan
from app.config.settings import shodankey, chromepath, crawlergopath, plugindir, masscanpath
from app.plugins.oneforall.oneforall import OneForAll
from queue import Queue
import queue
import uuid
import time
import threading

requests.packages.urllib3.disable_warnings()
from celerywing.config import CeleryConfig
from celerywing.subtasks import main_scan

sys.path.append("../")
import simplejson

app = Celery('tasks')

app.config_from_object(CeleryConfig)

base_path = os.path.abspath(os.path.dirname(__file__))


@app.task
def Crawlscan(host, ports, projectid):
    try:
        np = nmap.PortScanner()
        ip = socket.gethostbyname(host)
        print(ports, ip)
        np.scan(hosts=host, ports=ports, arguments="-Pn")
        urllist = []
        try:
            if 'tcp' in np[ip].all_protocols():
                for port in np[ip]["tcp"].keys():
                    try:
                        if np[ip]["tcp"][port]["state"] == "open":
                            url = "http://{}:{}".format(host, port)

                            rsp = os.popen(
                                crawlergopath + " -c {0} -t 5 --fuzz-path --robots-path  -o json --push-to-proxy http://127.0.0.1:1664 {1}".format(
                                    chromepath,
                                    url))
                            # cmd = ["/Users/wing/evilwing/pentesting/crawlergo_x_XRAY/crawlergo", "-c", "/Applications/Google\ Chrome.app/Contents/MacOS/Google\  Chrome", "-t", "20","--fuzz-path","--robots-path","--push-to-proxy","http://127.0.0.1:1664", host]
                            # rsp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            result = simplejson.loads(rsp.read().split("--[Mission Complete]--")[1])
                            req_list = result["req_list"]
                            for req in req_list:
                                url1 = req['url']
                                method = req['method']
                                # print(url1 + "[+]" + method)
                                urllist.append({str(port): method + "-->" + url1})

                            LinksDB.AddLinks(projectid=projectid, host=host, port=port, links=urllist)
                        else:
                            print("tcp Error!")
                    except Exception as e:
                        return str(e) + "tcp Error!"
            else:
                print("Port Close!")
        except Exception as e:
            return str(e) + "Scan Error!"
        return " Crawler Scan Complete"
    except Exception as e:
        return str(e) + "Crawer Error!"


@app.task
def Portscan(host, ports, projectid, threads):
    try:
        ip = socket.gethostbyname(host)
        try:
            res = requests.get(
                'https://api.tx7.co/icp.php?url={0}'.format(
                    host), timeout=3)
            company_name = json.loads(res.text)["主办名称"]
            logger.warning(message=company_name)
        except Exception as e:
            logger.warning(message=e)
            company_name = "snowing"

        portserver = dict()
        singleportdetail = {}
        np = nmap.PortScanner()
        np.scan(hosts=ip, ports=ports, arguments="-Pn -sT")
        if 'tcp' in np[ip].all_protocols():
            for port in np[ip]["tcp"].keys():
                if np[ip]["tcp"][port]["state"] == "open":
                    pattern = re.compile('(php)|(aspx?)|(jsp)|(python)|(go?)|(ruby)', re.I)
                    match = pattern.search(np[ip]["tcp"][port]["extrainfo"])
                    if match:
                        codes = match.group().lower()
                    else:
                        codes = ""
                    # host = host
                    port = port
                    server = np[ip]["tcp"][port]["name"]
                    product = np[ip]["tcp"][port]["product"]
                    state = np[ip]["tcp"][port]["state"]
                    extrainfo = np[ip]["tcp"][port]["extrainfo"]
                    codes = codes
                    version = np[ip]["tcp"][port]["version"]
                    url = "http://{0}:{1}".format(host, port)
                    try:
                        res = requests.get(url=url, timeout=5)
                        res.encoding = 'utf-8'
                        soup = BeautifulSoup(res.text, 'lxml')
                        title = soup.find('title').text
                    except:
                        title = ""
                    # 指纹识别
                    try:
                        resp = requests.get(
                            url="http://api.yunsee.cn/fingerApi/?token=&id\=191&url\={0}:{1}\&level\=2".format(
                                host, port), timeout=5)
                        temp = json.loads(resp.text)
                        if temp['data']['cms']:
                            finger = temp['data']['server'][0]['name'] + " " + temp['data']['cms'][0]['name'] + \
                                     temp['data']['cms'][0]['version']
                        else:
                            finger = server
                    except:
                        finger = server
                    # 目录扫描
                    dirscan = webdir(str(url), int(threads))
                    dirscan.work()
                    path = dirscan.output()
                    # return path
                    singleportdetail[str(port)] = {"port": port, "finger": finger, "title": title, "product": product,
                                                   "state": state, "extrainfo": extrainfo, "codes": codes,
                                                   "version": version, "path": path}

        portserver.setdefault("portserver", singleportdetail)
        # print(portserver)
        VulnScanDB.AddVulScan(projectid=projectid, host=host, ip=ip, portserver=portserver, company_name=company_name)

        return portserver
    except Exception as e:
        print(e)
        return "[!]" + str(e) + "[======]PortScan Error!"


class webdir:
    def __init__(self, root, threadNum):
        self.root = root
        self.threadNum = threadNum
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20',
            'Referer': 'http://baidu.com',
            'Cookie': 'baiduspider=dasdasdsadasccasdasd',
        }
        self.task = queue.Queue()
        self.s_list = []
        filename = base_path + "/../dict/top100dir.txt"
        for line in open(filename):
            self.task.put(root + "/" + line.strip())

    def checkdir(self, url):
        status_code = 0
        try:
            r = requests.head(url, headers=self.headers, timeout=5)
            status_code = r.status_code
        except:
            status_code = 0
        return status_code

    def test_url(self):
        while not self.task.empty():
            url = self.task.get()
            s_code = self.checkdir(url)
            if s_code == 200:
                self.s_list.append(url)
            print("Testing: %s status:%s" % (url, s_code))

    def work(self):
        threads = []
        for i in range(self.threadNum):
            t = threading.Thread(target=self.test_url())
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        print('[*] The DirScan is complete!')

    def output(self):
        if len(self.s_list):
            print("[*] status = 200 dir:")
            for url in self.s_list:
                print(url)
            print(self.s_list)
            return self.s_list


@app.task
def SubdomainScan(rootdomain, project, freq):
    global company
    logger.info("[*] 开始找寻 {} 的子域名".format(rootdomain))
    tmpid = str(uuid.uuid1())
    TaskDB.add(taskid=tmpid, project=project, rootdomain=rootdomain, subdomain_count=0, portcount=0, flag=0,
               freq=int(freq))
    one = OneForAll(target=rootdomain)
    one.format = "json"
    one.brute = True
    one.req = True
    one.run()
    oneres = one.datas
    logger.info("[*] 子域名入库")
    # ICP查询
    # res = os.popen("curl https://api.66mz8.com/api/icp.php?domain={}".format(rootdomain)).read()
    domainkey = ""
    try:
        res = requests.get('http://apidata.chinaz.com/CallAPI/Domain?key={0}&domainName={1}}'
                           .format(domainkey, rootdomain), verify=False)
        if json.loads(res.text)['StateCode'] == 1:
            company = json.loads(res.text)['Result']["CompanyName"]
            logger.info(company)
    except:
        logger.warning("查询域名的key失效")
        company = "Vulcan"
    with open("{0}/oneforall/results/{1}.json".format(plugindir,
                                                      str(rootdomain))) as f:
        lines = f.read()
        tmp = json.loads(lines)
        subcount = len(tmp)
        ipcount = 0
        logger.info("[+] 找到{0}的子域 {1} 个".format(rootdomain, (len(tmp))))
        # 先获取所有子域名ip
        for i in range(0, len(tmp)):
            ip = tmp[i]["content"]
            if ip:
                ipcount += 1
        flagnum = 0
        for i in range(0, len(tmp)):
            ip = tmp[i]["content"]
            if ip:
                # print(ip)
                ip = tmp[i]["content"].split(',')[0]
                # 入库信息
                flagnum += 1
                tmpres = "%.2f%%" % ((flagnum / ipcount) * 100)
                subdomain = tmp[i]["subdomain"].strip("\n")
                logger.info("[+]Scanning  subdomain: " + subdomain + "--IP: " + ip)
                main_scan.delay(tmpid, ip, project, subdomain, company, subcount,
                                ipcount, tmpres)
    return project + "=====Subdomain Scanning!======="


@app.task()
def celery_pocscan(pid, flag):
    from app.api.common.utils.utils import target_parse, poc_config_init
    from app.api.common.utils.pocsuite_api import pocsuite_scanner
    try:
        items = PocscanTask.find_by_id(pid)
        taskname = items['name']
        target_list = target_parse(items["target"])
        poc_list = items["poc"]
        thread = items['thread']
        if flag == 1:
            PocscanTask.update_by_id(pid, {"status": "Running",
                                           "end_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        else:
            PocscanTask.update_by_id(pid, {"status": "Running"})
        count = 0
        for poc_id in poc_list:
            poc_item = PocsuiteDB.get_detail_by_id(poc_id)
            if not poc_item:
                continue
            _poc_config = poc_config_init(target_list=target_list,
                                          poc_str=poc_item['poc_content'].replace('\\ufeff', ''),
                                          threat=thread)
            _scan_items = pocsuite_scanner(_poc_config)
            for _item in _scan_items:
                try:
                    result = _item['result'] if _item['result'] else _item['error_msg'][1]
                    if _item['status'] == "success":
                        PocsuiteVuln.add(
                            taskid=pid, poc=poc_id, task_name=taskname,
                            poc_name=poc_item['name'], status=_item['status'],
                            target=_item['target'], app=poc_item['app'],
                            result=result
                        )
                        contents = "### PocScan \n" + \
                                   "目标: {domain} \n\n".format(domain=_item['target']) + \
                                   "漏洞名称: {title} \n\n".format(title=poc_item['name']) + \
                                   "app: {company} \n\n".format(company=poc_item['app'])

                        notice(contents=contents, info="任务" + taskname + "[+]" + _item['target'] + "!!发现高危漏洞!!")
                        count += 1
                except Exception as e:
                    logger.warning("save poc result failed: {}".format(e))

        # Update task information
        update_data = {
            "status": "Success",
            "vul_count": count,
            "end_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }
        notice(contents=taskname + " 扫描完成!^_^", info=taskname + " 扫描完成!^_^")
        PocscanTask.update_by_id(tid=pid, data=update_data)
        logger.success("poc task completed: {}".format(pid))
        return taskname + " 扫描完成!^_^"
    except Exception as e:
        logger.warning("poc scan  failed: {}".format(e))


@app.task()
def schedule_subdomain_scanner():
    try:
        task_items = TaskDB.get_list()
        for item in task_items:
            t_id = str(item['_id'])
            freq = int(item['freq'])
            domain = item['rootdomain']
            end_date = item['date']
            if str(end_date) == str(0):
                end_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            else:
                end_date = end_date
            timeArray = time.strptime(str(end_date), "%Y-%m-%d %H:%M:%S")
            timestamp = time.mktime(timeArray)
            status = item['flag']
            project = item["project"]
            # print(item)
            if freq == 1:
                if str(100) in str(status):
                    plan_time = int(time.time()) - int(timestamp)
                    if plan_time > 60 * 60 * 24:
                        logger.info("daily task running: subdomain scan {}:{}".format(t_id, domain))
                        # delete old data
                        TaskDB.delete_by_id(t_id)
                        # notice(contents=project + "==>子域名定时扫描开始", info="开始扫描:" + project)
                        # celery_pocscan.delay(t_id, flag=1)
                        SubdomainScan.delay(domain, project, 1)
                        notice(contents=project + "==>子域名定时扫描开始", info="开始扫描{}子域名".format(project))

            elif freq == 3:
                if str(100) in str(status):
                    plan_time = int(time.time()) - int(timestamp)
                    if plan_time > 60 * 60 * 24 * 3:
                        logger.info("weekly task running: poc scan {}".format(t_id))
                        # delete old data
                        # PocsuiteVuln.delete_by_tid(t_id)
                        TaskDB.delete_by_id(t_id)
                        SubdomainScan.delay(domain, project, 3)
                        logger.info("daily task running: subdomain scan {}:{}".format(t_id, domain))
                        notice(contents=project + "==>子域名定时扫描开始", info="开始扫描{}子域名".format(project))

            elif freq == 7:
                if str(100) in str(status):
                    plan_time = int(time.time()) - int(timestamp)
                    if plan_time > 60 * 60 * 24 * 7:
                        logger.info("daily task running: subdomain scan {}:{}".format(t_id, domain))
                        # delete old data
                        # PocsuiteVuln.delete_by_tid(t_id)
                        TaskDB.delete_by_id(t_id)
                        SubdomainScan.delay(domain, project, 7)
                        logger.info("weekly task completed: poc scan {}".format(t_id))
                        notice(contents=project + "==>子域名定时扫描开始", info="开始扫描{}子域名".format(project))
    except Exception as e:
        print(e)

    return "SudomainScan定时任务正常运行!"


@app.task()
def schedule_poc_scanner():
    task_items = PocscanTask.get_list()
    for item in task_items:
        t_id = str(item['_id'])
        freq = int(item['frequency'])
        end_date = item['end_date']
        if str(end_date) == str(0):
            end_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        else:
            end_date = end_date
        timeArray = time.strptime(str(end_date), "%Y-%m-%d %H:%M:%S")
        timestamp = time.mktime(timeArray)

        status = item['status']
        project = item["name"]
        if freq == 1:
            if "Success" in status:
                plan_time = int(time.time()) - int(timestamp)
                if plan_time > 60 * 60 * 24:
                    logger.info("daily task running: poc scan {}".format(t_id))
                    # delete old data
                    notice(contents=project + "==>定时任务扫描开始扫描", info="开始扫描:" + project)
                    PocsuiteVuln.delete_by_tid(t_id)
                    celery_pocscan.delay(t_id, flag=1)
                    logger.info("daily task completed: poc scan {}".format(t_id))

        elif freq == 3:
            if "Success" in status:
                plan_time = int(time.time()) - int(timestamp)
                if plan_time > 60 * 60 * 24 * 3:
                    logger.info("weekly task running: poc scan {}".format(t_id))
                    # delete old data
                    PocsuiteVuln.delete_by_tid(t_id)
                    celery_pocscan.delay(t_id, flag=1)
                    logger.info("threely task completed: poc scan {}".format(t_id))
                    notice(contents=project + "==>定时任务扫描开始扫描", info="开始扫描" + project)

        elif freq == 7:
            if "Success" in status:
                plan_time = int(time.time()) - int(timestamp)
                if plan_time > 60 * 60 * 24 * 7:
                    logger.info("monthly task running: poc scan {}".format(t_id))
                    # delete old data
                    PocsuiteVuln.delete_by_tid(t_id)
                    celery_pocscan.delay(t_id, flag=1)
                    logger.info("weekly task completed: poc scan {}".format(t_id))
                    notice(contents=project + "==>定时任务扫描开始扫描", info="开始扫描" + project)

    return "PocScan定时任务正常运行!"


@app.task()
def portscanner(ip):
    pass


# other func
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


# if __name__ == '__main__':
#     w = webdir('http://127.0.0.1:8080', 10)
#     w.work()
#     dd = w.output()
#     print(dd)
