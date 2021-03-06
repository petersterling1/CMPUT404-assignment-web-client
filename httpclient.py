#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    #Make socket class wide
    c_socket = None

    def connect(self, host, port=80):

        #Remove any directory info from the host (eg. www.google.com/test becomes www.google.com) 
        host = host.split("/")
        host = host[0]

        #Parse for hte port if there is one
        host_split = host.split(":")
        try:
            host = host_split[0]
            port = host_split[1]
        except:
            port = 80

        #Make a new socket and connect to it via the host and port
        self.c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.c_socket.connect((str(host), int(port)))

    def get_code(self, data):
        #Parse the HTTP response code from the message
        try:
            code = data.split(" ")
            code = int(code[1])
        except:
            code = 404
        

        return code

    def get_headers(self,data):
        #Unused? Doesn't really seem like it's needed... may add this in later
        return None

    def get_body(self, data):
        #Return the body of the message
        try:
            body = data.split("\r\n\r\n", 1)
            body = body[1]
        except:
            body = ""

        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        
        #Strip out http:// if it's there
        url = url.replace("http://", "")

        #Call connect function
        self.connect(url)
        
        #Get everything after .com/. If there isn't, set file wanted to '/'
        url_split = url.split('/', 1)
        try:
            file = url_split[1]
        except:
            file = "/"

        #Edge cases here depending on various server configurations
        if file == "":
            file = "/"
        if len(file) > 1 and file[0] != "/":
            file = "/" + file

        #Get the host, necessary for HTTP header
        host = url_split[0]

        #Convert querues to an encoded string
        try:
            queries = "?" + urllib.urlencode(args)
        except:
            queries = ""

        #HTTP request for GET.
        request = "GET " + file + queries + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n"

        #Send via socket
        self.c_socket.send(request)

        #Returned value
        returned = self.recvall(self.c_socket)

        #Return, set code/body, end socket
        print returned
        
        code = self.get_code(returned)
        body = self.get_body(returned)

        self.c_socket.shutdown(socket.SHUT_RDWR)
        self.c_socket.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        #Strip out http:// if it's there
        url = url.replace("http://", "")

        #Call connect function
        self.connect(url)
        
        #Get everything after .com/. If there isn't, set file wanted to '/'
        url_split = url.split('/', 1)
        try:
            file = url_split[1]
        except:
            file = "/"

        #Edge cases here depending on various server configurations
        if file == "":
            file = "/"
        if len(file) > 1 and file[0] != "/":
            file = "/" + file

        #Get the host, necessary for HTTP header
        host = url_split[0]

        #Convert querues to an encoded string
        try:
            data = urllib.urlencode(args)
        except:
            data = ""

        #HTTP request for POST
        request = "POST " + file + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: " + str(len(data)) + "\r\n\r\n" + data

        #Send via socket
        self.c_socket.send(request)

        #Returned value
        returned = self.recvall(self.c_socket)

        #Return, set code/body, end socket
        print returned

        code = self.get_code(returned)
        body = self.get_body(returned)

        self.c_socket.shutdown(socket.SHUT_RDWR)
        self.c_socket.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):

        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
