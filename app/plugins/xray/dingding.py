# -*- coding=utf-8 -*-
from flask import Flask, request
import requests
import datetime
import logging


app = Flask(__name__)

def push_ftqq(datas):
    ddheaders={"Content-Type": "application/json; charset=utf-8"}
    try:
        resp = requests.post("https://oapi.dingtalk.com/robot/send?access_token=",data=datas,headers=ddheaders)
        print(resp.content)
    except :
        pass

@app.route('/webhook', methods=['POST','GET'])
def xray_webhook():
    vuln = request.json
    print(vuln)



    try:
        contents = """## xray vuln

url: {url}

plugin: {plugin}

vuln type: {vuln_class}

Time: {create_time}
""".format(url=vuln["target"]["url"], plugin=vuln["plugin"],
           vuln_class=vuln["vuln_class"] or "Default",
           create_time=str(datetime.datetime.fromtimestamp(vuln["create_time"] / 1000)))
        datas = '{ "markdown": { "title": "Master, find a new Vuln!", "text": "' +  contents +' By IceWing" }, "msgtype": "markdown" }'
        # print(datas)
        push_ftqq(datas)
    except Exception as e:
        return "Something is error"
    return 'ok'
'''
{'create_time': 1579534962314, 'detail': {'filename': '/vul/fileinclude/', 'host': '192.168.100.2', 'param': {}, 'payload': '', 'port': 8090, 'request': 'GET /vul/fileinclude/ HTTP/1.1\r\nHost: 192.168.100.2:8090\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nAccept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\nContent-Type: text/plain\r\nCookie: key=value; PHPSESSID=no6gv63k7c54q41037tbjvdj8u\r\nDnt: 1\r\nReferer: http\r\nUpgrade-Insecure-Requests: 1\r\nAccept-Encoding: gzip\r\n\r\n', 'response': 'HTTP/1.1 200 OK\r\nContent-Type: text/html;charset=UTF-8\r\nDate: Mon, 20 Jan 2020 15:42:42 GMT\r\nServer: Apache/2.4.29 (Ubuntu)\r\nVary: Accept-Encoding\r\n\r\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<html>\n <head>\n  <title>Index of /vul/fileinclude</title>\n </head>\n <body>\n<h1>Index of /vul/fileinclude</h1>\n  <table>\n   <tr><th valign="top"><img src="/icons/blank.gif" alt="[ICO]"></th><th><a href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last modified</a></th><th><a href="?C=S;O=A">Size</a></th><th><a href="?C=D;O=A">Description</a></th></tr>\n   <tr><th colspan="5"><hr></th></tr>\n<tr><td valign="top"><img src="/icons/back.gif" alt="[PARENTDIR]"></td><td><a href="/vul/">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - </td><td>&nbsp;</td></tr>\n<tr><td valign="top"><img src="/icons/unknown.gif" alt="[   ]"></td><td><a href="fi_local.php">fi_local.php</a></td><td align="right">2020-01-20 11:43  </td><td align="right">2.9K</td><td>&nbsp;</td></tr>\n<tr><td valign="top"><img src="/icons/unknown.gif" alt="[   ]"></td><td><a href="fi_remote.php">fi_remote.php</a></td><td align="right">2020-01-20 11:43  </td><td align="right">3.5K</td><td>&nbsp;</td></tr>\n<tr><td valign="top"><img src="/icons/unknown.gif" alt="[   ]"></td><td><a href="fileinclude.php">fileinclude.php</a></td><td align="right">2020-01-20 11:43  </td><td align="right">3.9K</td><td>&nbsp;</td></tr>\n<tr><td valign="top"><img src="/icons/folder.gif" alt="[DIR]"></td><td><a href="include/">include/</a></td><td align="right">2020-01-20 11:46  </td><td align="right">  - </td><td>&nbsp;</td></tr>\n   <tr><th colspan="5"><hr></th></tr>\n</table>\n<address>Apache/2.4.29 (Ubuntu) Server at 192.168.100.2 Port 8090</address>\n</body></html>\n', 'url': 'http://192.168.100.2:8090/vul/fileinclude/'}, 'plugin': 'dirscan', 'target': {'url': 'http://192.168.100.2:8090/vul/fileinclude/'}, 'type': 'web_vuln', 'vuln_class': 'directory'}
'''

if __name__ == '__main__':
    app.run(debug=True,port=6000)
