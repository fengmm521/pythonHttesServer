#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-12-07 09:28:00
# @Link    : http://fengmm521.blog.163.com
# @Version : $Id$
#https服务器
import os
import ssl
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import logging
import cgi
import time
import posixpath
import urllib
import sys
import shutil
import mimetypes
import json

import hashlib

import WXMsgTool


wxtool = WXMsgTool.WXMsgTool()

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

nowPth = os.path.split(os.getcwd())[1]
curdir = '.'

class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):  
    	# print self.path
        if self.path=="/":  
            self.path="/index.html"  
  
        try:  
            #根据请求的文件扩展名，设置正确的mime类型  
            sendReply = False  
            if self.path.endswith(".html"):  
                mimetype='text/html'  
                sendReply = True  
            if self.path.endswith(".jpg"):  
                mimetype='image/jpg'  
                sendReply = True  
            if self.path.endswith(".gif"):  
                mimetype='image/gif'  
                sendReply = True  
            if self.path.endswith(".js"):  
                mimetype='application/javascript'  
                sendReply = True  
            if self.path.endswith(".css"):  
                mimetype='text/css'  
                sendReply = True  
            if self.path.endswith(".swf"):  
                mimetype='application/x-shockwave-flash'  
                sendReply = True  
            if self.path[0:3] == "/wx":
                sendReply = False
                datastrs = self.path.split('?')
                if len(datastrs) > 1:
                    requestr = datastrs[1]
                    coms = requestr.split('&')
                    reqdata = {}
                    for c in coms:
                        tmps = c.split('=')
                        reqdata[tmps[0]] = tmps[1]
                    # print reqdata
                # sendstr = json.dumps(tokenback)
                    if 'echostr' in reqdata.keys():
                        sendstr = reqdata['echostr']
                        length = len(sendstr)
                        self.send_response(200)
                        self.send_header("Content-type", 'application/json; encoding=utf-8')
                        self.send_header("Content-Length", str(length))
                        self.end_headers()
                        self.wfile.write(sendstr)
                    else:
                        return reqdata

            if sendReply == True:  
                #读取相应的静态资源文件，并发送它  
                f = open(curdir + os.sep + self.path, 'rb')  
                self.send_response(200)  
                self.send_header('Content-type',mimetype)  
                self.end_headers()  

                self.wfile.write(f.read())  
                f.close()  
            return  
  
        except IOError:  
            self.send_error(404,'File Not Found: %s' % self.path)  
  
    def sendEmptyMsg(self):
        self.send_response(200)
        self.send_header("Content-type", 'application/xml; encoding=utf-8')
        self.send_header("Content-Length", str(''))
        self.end_headers()
        self.wfile.write('')

    def sendMsg(self,toUserName,fromUserName,msg):
        sendmsg = u'<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%d</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA['%(toUserName,fromUserName,int(time.time())) + unicode(msg,'utf-8') + u']]></Content></xml>'
        sendmsg = sendmsg.encode('UTF-8')
        self.send_response(200)
        self.send_header("Content-type", 'application/xml; encoding=utf-8')
        self.send_header("Content-Length", str(len(sendmsg)))
        self.end_headers()
        self.wfile.write(sendmsg)

    #校验消息真实性
    def verifyMsg(self,reqdict):
        tokenver = []
        tokenver.append('tokenxxx')
        tokenver.append(reqdict['nonce'])
        tokenver.append(reqdict['timestamp'])
        tokenver.sort()
        tmpstr = tokenver[0] + tokenver[1] + tokenver[2]
        sha1str = hashlib.sha1(tmpstr).hexdigest()
        if sha1str == reqdict['signature']:
            return True
        else:
            return False
    def do_POST(self):


        dictmp = self.do_GET()

        isOK = False
        if dictmp:
            isOK = self.verifyMsg(dictmp)

        if isOK:
            length = self.headers.getheader('content-length');
            nbytes = int(length)
            data = self.rfile.read(nbytes)
            wxtool.getWXMsg(data, self)
        else:
            self.send_error(404,'File Not Found: %s' % self.path)  


        """Serve a POST request."""
        # form = cgi.FieldStorage(
        #     fp=self.rfile,
        #     headers=self.headers,
        #     environ={'REQUEST_METHOD': 'POST',
        #              'CONTENT_TYPE': self.headers['Content-Type'],
        #              })
        # filename = form['file'].filename
        # print filename
        # path = self.translate_path(self.path)
        # print path
        # filepath = os.path.join(path, filename)
        # print filepath
        # if os.path.exists(filepath):
        #     self.log_error('File %s exist!', filename)
        #     filepath += '.new'

        # with open(filepath, 'wb') as f:
        #     f.write(form['file'].value)

        

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write('''<form action="" enctype="multipart/form-data" method="post">\n
                    <input name="file" type="file" />
                    <input value="upload" type="submit" />
                </form>''')
        f.write("<hr>\n<ul>\n")
        for name in list:
            if name.startswith('.'):
                continue
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def log_error(self, format, *args):
        """Log an error.

        Display error message in red color.
        """

        format = '\033[0;31m' + format + '\033[0m'
        self.log_message(format, *args)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""



serverAddr = ('127.0.0.1',4443)

def runHttpServer(ptemp):
    server = ThreadedHTTPServer(serverAddr, myHandler)
    print 'https server is running....'
    print 'Starting server, use <Ctrl-C> to stop'
    
    server.socket = ssl.wrap_socket (server.socket, certfile='server.pem', server_side=True)
    server.serve_forever()
def startServer(ltctool,btctool):

    wxtool.setBTCTool(btctool)
    wxtool.setLTCTool(ltctool)

    thr = threading.Thread(target=runHttpServer,args=(None,))
    thr.setDaemon(True)
    thr.start()

    return wxtool


if __name__ == '__main__':
    # server = ThreadedHTTPServer(serverAddr, myHandler)
    # print 'https server is running....'
    # print 'Starting server, use <Ctrl-C> to stop'
    # server.socket = ssl.wrap_socket (server.socket, certfile='server.pem', server_side=True)
    # server.serve_forever()
    startServer()
    while True:
        pass
        time.sleep(10)


# # 生成rsa密钥
# $ openssl genrsa -des3 -out server.key 2048
# # 去除掉密钥文件保护密码
# $ openssl rsa -in server.key -out server.key
# # 生成ca对应的csr文件
# $ openssl req -new -key server.key -out server.csr
# # 自签名
# $ openssl x509 -req -days 2048 -in server.csr -signkey server.key -out server.crt
# $ cat server.crt server.key > server.pem
