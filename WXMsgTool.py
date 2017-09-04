#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-12-07 09:28:00
# @Link    : http://fengmm521.blog.163.com
# @Version : $Id$
#https服务器
import os
import urllib2
import time
import xmltodict;  #xml转为字典
import json;


def httpGet(urlstr):
    req = urllib2.Request(urlstr)
    req.add_header('User-agent', 'Mozilla 5.10')
    res = urllib2.urlopen(req)
    html = res.read()
    return html


class WXMsgTool(object):
    """docstring for WXMsgTool"""
    def __init__(self,token = '',appID = '',pseckey = '',pAesKey = ''):
        super(WXMsgTool, self).__init__()

        self.ltctool = None         #ltc设置工具
        self.btctool = None         #btc设置工具

        self.msgToken = token
        self.appid = appID
        self.seckey = pseckey
        self.aesKey = pAesKey
        self.access_token = ''
        self.expires_time = 0

        self.lastMsg = ''

        self.lastCallUserName = ''
        self.myName = ''
        self.lastMsgID = ''

        self.getAccess_token()

    #给发送的消息用access_token签名
    def msgSign(self,msg):
        pass
    #获取微信token
    def getAccess_token(self):
        askurl = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'%(self.appid,self.seckey)
        baskstr = httpGet(askurl)
        jsdic = json.loads(baskstr)
        # print jsdic
        if 'access_token' in jsdic.keys():
            self.access_token = jsdic['access_token'] 
            self.expires_time = jsdic['expires_in']  + int(time.time()) - 5         #access_token有效时间
            # print baskstr
            # print self.access_token
            # print self.expires_time
        else:
            print '请求token错误'
            print jsdic
    #获取微信服务器ip列表
    def getWXServerIPList(self):
        pass
    
    #得到微信发来消息，这里的wxMsg为微信服务器post来的xml数据
    def getWXMsg(self,wxMsg,httpHandler):
        # print wxMsg
        dictdat = xmltodict.parse(wxMsg)
        if dictdat['xml']['MsgType'] == 'text' and dictdat['xml']['ToUserName'] == '':
            self.getUserMsg(dictdat['xml']['FromUserName'], dictdat['xml']['MsgId'], dictdat['xml']['Content'], httpHandler)
        else:
            if httpHandler:
                httpHandler.sendEmptyMsg()

    def new_friends(self,msg,httpHandler):
        # 处理好友逻辑代码
        self.lastMsg = msg
        strs = self.lastMsg.split(',')
        if len(strs) == 3:
            if strs[0] == 'btc':
                self.setBTCOnceTrade(float(strs[1]), float(strs[2]),httpHandler)
            elif strs[0] == 'ltc':
                self.setLTCOnceTrade(float(strs[1]), float(strs[2]),httpHandler)
            else:
                self.badkCallMsg('msg erro',httpHandler)
        elif len(strs) == 5:
            if strs[0] == 'btc':
                self.setBTCTradeConf(float(strs[1]), float(strs[2]),float(strs[3]),float(strs[4]),httpHandler)
            elif strs[0] == 'ltc':
                self.setLTCTradeConf(float(strs[1]), float(strs[2]),float(strs[2]),float(strs[2]),httpHandler)
            else:
                self.badkCallMsg('msg erro',httpHandler)
        elif len(strs) == 1:
            if strs[0] == 'ltc':
                self.getLTCSetTrade(httpHandler)
            elif strs[0] == 'btc':
                self.getBTCSetTrade(httpHandler)
            elif strs[0] == 'cny':
                self.getCNYUser(httpHandler)
            else:
                self.badkCallMsg('msg erro',httpHandler)
        else:
            self.badkCallMsg('msg erro',httpHandler)
    #callback
    
    def badkCallMsg(self,msg,handler):
        if handler:
            # print self.lastCallUserName
            # print self.myName
            print msg,time.time(),'\n'
            handler.sendMsg(self.lastCallUserName,self.myName,msg)

    #得到用户发来消息,消息已经过校验，分解出用户消息和用户ID
    def getUserMsg(self,userName,msgID,userMsg,httpHandler):
        self.lastCallUserName = userName
        self.lastMsgID = msgID
        # print self.lastCallUserName
        # print self.lastMsgID
        print userMsg,time.time(),'\n'
        if userName == '':
            self.new_friends(userMsg, httpHandler)
        else:
            self.badkCallMsg(u'自动回复接口还在调试中，请以后再试',httpHandler)
        

    def setBTCTool(self,btc):
        self.btctool = btc
    def setLTCTool(self,ltc):
        self.ltctool = ltc

    #获取帐号信息
    def getCNYUser(self,httpHandler):
        accountstr = self.ltctool.getAccountDataReque()
        accountstr = accountstr.replace(',','\n')
        self.badkCallMsg(accountstr, httpHandler)
    def getBTCSetTrade(self,httpHandler):
        sendmsg = ''
        if self.btctool:
            if self.btctool.isTradeOnce:
                sendmsg = 'btc-isOnceType,lastOpt:%d,buyprice:%.2f,sellprice:%.2f,tradecount:%d'%(self.btctool.lastOpt,self.btctool.onceBuyPrice,self.btctool.onceSellPrice,self.btctool.onceTradeCount)
            else:
                sendmsg = 'btc-isConfType,lastOpt:%d,buyprice:%.2f,buycount:%.2f,sellprice:%.2f,sellcount:%.2f'%(self.btctool.lastOpt,self.btctool.netBuyPrice,self.btctool.netBuyCount,self.btctool.netSellPrice,self.btctool.netSellCount)
        else:
            sendmsg = 'ltctool in None'
        sendmsg = sendmsg.replace(',','\n')
        self.badkCallMsg(sendmsg, httpHandler)

    def getLTCSetTrade(self,httpHandler):
        sendmsg = ''
        if self.ltctool:
            if self.ltctool.isTradeOnce:
                sendmsg = 'ltc-isOnceType,lastOpt:%d,buyprice:%.2f,sellprice:%.2f,tradecount:%d'%(self.ltctool.lastOpt,self.ltctool.onceBuyPrice,self.ltctool.onceSellPrice,self.ltctool.onceTradeCount)
            else:
                sendmsg = 'ltc-isConfType,lastOpt:%d,buyprice:%.2f,buycount:%.2f,sellprice:%.2f,sellcount:%.2f'%(self.ltctool.lastOpt,self.ltctool.netBuyPrice,self.ltctool.netBuyCount,self.ltctool.netSellPrice,self.ltctool.netSellCount)
        else:
            sendmsg = 'ltctool in None'
        sendmsg = sendmsg.replace(',','\n')
        self.badkCallMsg(sendmsg, httpHandler)


    def setBTCOnceTrade(self,buyprice,sellprice,httpHandler):
        sendmsg = ''
        if self.btctool:
            self.btctool.setNetBuyAndSellWithAll(buyprice,sellprice)
            sendmsg = 'confBTC,%.2f,%.2f'%(buyprice,sellprice)
        else:
            sendmsg = 'btctool is None'
        sendmsg = sendmsg.replace(',','\n')
        self.badkCallMsg(sendmsg, httpHandler)
    def setLTCOnceTrade(self,buyprice,sellprice,httpHandler):
        sendmsg = ''
        if self.ltctool:
            self.ltctool.setNetBuyAndSellWithAll(buyprice,sellprice)
            sendmsg = 'confLTC,%.2f,%.2f'%(buyprice,sellprice)
        else:
            sendmsg = 'ltctool is None'
        sendmsg = sendmsg.replace(',','\n')
        self.badkCallMsg(sendmsg, httpHandler)

    def setBTCTradeConf(buyprice,buycount,sellprice,sellcount,httpHandler):
        sendmsg = ''
        if self.btctool and (not (buyprice <=0 or buycount <= 0 or sellprice <= 0 or sellcount <= 0)):
            self.btctool.setNetBuyAndSellConfig(buyprice,buycount,sellprice,sellcount)
            sendmsg = 'confBTC,buyprice:%.2f,count:%.2f,sellprice:%.2f,count:%2f'%(buyprice,buycount,sellprice,sellcount)
        elif self.btctool and (buyprice <=0 or buycount <= 0 or sellprice <= 0 or sellcount <= 0):
            sendmsg = 'some setbtcconf <= 0,confBTC,buyprice:%.2f,count:%.2f,sellprice:%.2f,count:%2f'%(buyprice,buycount,sellprice,sellcount)
        else:
            sendmsg = 'btctool is None'
        sendmsg = sendmsg.replace(',','\n')
        self.badkCallMsg(sendmsg, httpHandler)

    def setLTCTradeConf(buyprice,buycount,sellprice,sellcount,httpHandler):
        sendmsg = ''
        if self.ltctool and (not (buyprice <=0 or buycount <= 0 or sellprice <= 0 or sellcount <= 0)):
            self.ltctool.setNetBuyAndSellConfig(buyprice,buycount,sellprice,sellcount)
            sendmsg = 'confLTC,buyprice:%.2f,count:%.2f,sellprice:%.2f,count:%.2f'%(buyprice,buycount,sellprice,sellcount)
        elif self.ltctool and (buyprice <=0 or buycount <= 0 or sellprice <= 0 or sellcount <= 0):
            sendmsg = 'some setltcconf <= 0,confLTC,buyprice:%.2f,count:%.2f,sellprice:%.2f,count:%.2f'%(buyprice,buycount,sellprice,sellcount)
        else:
            sendmsg = 'ltctool is None'
        sendmsg = sendmsg.replace(',','\n')
        self.badkCallMsg(sendmsg, httpHandler)

    def sendMsgToMage(self,msg):
        tmpmsg = msg.replace(',','\n')
        tmpstr = unicode(tmpmsg,'utf-8')

if __name__ == '__main__':
    wxtool = WXMsgTool()
    wxtool.getWXMsg(msgtmp, None)


# # 生成rsa密钥
# $ openssl genrsa -des3 -out server.key 2048
# # 去除掉密钥文件保护密码
# $ openssl rsa -in server.key -out server.key
# # 生成ca对应的csr文件
# $ openssl req -new -key server.key -out server.csr
# # 自签名
# $ openssl x509 -req -days 2048 -in server.csr -signkey server.key -out server.crt
# $ cat server.crt server.key > server.pem
