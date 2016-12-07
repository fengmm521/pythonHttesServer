#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-12-07 09:28:00
# @Link    : http://fengmm521.blog.163.com
# @Version : $Id$
#https服务器
import os
import BaseHTTPServer, SimpleHTTPServer
import ssl
from SimpleHTTPServer import SimpleHTTPRequestHandler as HTTPSHandler

curdir = '.'

class myHandler(HTTPSHandler):  
      
    def do_GET(self):  
    	print self.path
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
  
    def do_POST(self):  
    	print 'do post'
        logging.warning(self.headers)  
        form = cgi.FieldStorage(  
            fp=self.rfile,  
            headers=self.headers,  
            environ={'REQUEST_METHOD':'POST',  
                    'CONTENT_TYPE':self.headers['Content-Type'],  
                    })  
  
        file_name = self.get_data_string()  
        path_name = '%s/%s.log' % (RES_FILE_DIR,file_name)  
        fwrite = open(path_name,'a')  
  
        fwrite.write("name=%s\n" % form.getvalue("name",""))  
        fwrite.write("addr=%s\n" % form.getvalue("addr",""))  
        fwrite.close()  
  
        self.send_response(200)  
        self.end_headers()  
        self.wfile.write("Thanks for you post")  
  
    def get_data_string(self):  
        now = time.time()  
        clock_now = time.localtime(now)  
        cur_time = list(clock_now)  
        date_string = "%d-%d-%d-%d-%d-%d" % (cur_time[0],  
                cur_time[1],cur_time[2],cur_time[3],cur_time[4],cur_time[5])  
        return date_string  
print 'https server is running....'


serverAddr = ('127.0.0.1',4443)


httpd = BaseHTTPServer.HTTPServer(serverAddr, myHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='server.pem', server_side=True)
httpd.serve_forever()


# except KeyboardInterrupt:  
#     print '^C received, shutting down the web server'  
#     server.socket.close() 


# # 生成rsa密钥
# $ openssl genrsa -des3 -out server.key 1024
# # 去除掉密钥文件保护密码
# $ openssl rsa -in server.key -out server.key
# # 生成ca对应的csr文件
# $ openssl req -new -key server.key -out server.csr
# # 自签名
# $ openssl x509 -req -days 1024 -in server.csr -signkey server.key -out server.crt
# $ cat server.crt server.key > server.pem
