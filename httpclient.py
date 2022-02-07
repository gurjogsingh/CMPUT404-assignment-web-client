#!/usr/bin/env python3
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
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        print(f"Connected to {host} on port {port}")
        return None

    def get_code(self, data):
        #parsing code from the response (data) recieved from server
        header = data.split('\r\n\r\n')[0]
        first_line = header.split('\r\n')[0]
        code = first_line.split()[1]
        self.code = code

        return self.code

    def get_headers(self,data):
        #parsing and printing headers from the response (data) recieved from server
        header_block = data.split('\r\n\r\n')[0]
        headers = header_block.split('\r\n')
        
        for header in headers:
            print(header)
        print('\r\n')

    def get_body(self, data):
        
        body_block = data.split('\r\n\r\n')[1]
        self.body = body_block
        print(body_block)
        return self.body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        self.code = 500
        self.body = ""

        self.port = None
        self.host = None
        self.path = None

        #BREAKING DOWN URL
        parsed_url = urllib.parse.urlparse(url)

        self.host = parsed_url.hostname
        self.path = parsed_url.path
        if parsed_url.query != "":
            self.path = self.path + "?" + parsed_url.query
        if parsed_url.fragment != "":
            self.path = self.path + "#" + parsed_url.fragment
        if self.path == "":
            self.path = "/"
        if parsed_url.port == None:
            self.port = 80
        else:
            self.port = parsed_url.port

        #CREATING PAYLOAD   
        if self.port == 80:
            payload = f"GET {self.path} HTTP/1.1\r\nHost: {self.host}\r\nUser-Agent: Gurjog client\r\nConnection:close\r\nAccept: */*\r\n\r\n"
        else:
            payload = f"GET {self.path} HTTP/1.1\r\nHost: {parsed_url.netloc}\r\nUser-Agent: Gurjog client\r\nConnection:close\r\nAccept: */*\r\n\r\n"

        ##SENDING PAYLOAD
        
        #print(payload, "PAYLOAD")
        self.connect(self.host, self.port)
    
        print(payload)
        self.sendall(payload)

        #RECEIVING AND DISPLAYING RESPONSE
        data = self.recvall(self.socket) 
        self.get_headers(data)
        self.code = int(self.get_code(data))
        self.body = self.get_body(data)
    
        #CLOSING 
        self.close()
        return HTTPResponse(self.code, self.body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        self.port = None
        self.host = None
        self.path = None
        
        if args == None or "":
            self.is_request_body = False
        else:
            self.request_body = urllib.parse.urlencode(args)
            self.content_length = len(bytearray(self.request_body, 'utf-8'))
            self.is_request_body = True
        
        print(args, "ARGUMENTS BEING SENT")

        #BREAKING DOWN URL
        parsed_url = urllib.parse.urlparse(url)

        self.host = parsed_url.hostname
        self.path = parsed_url.path
        if parsed_url.query != "":
            self.path = self.path + "?" + parsed_url.query
        if parsed_url.fragment != "":
            self.path = self.path + "#" + parsed_url.fragment
        if self.path == "":
            self.path = "/"
        if parsed_url.port == None:
            self.port = 80
        else:
            self.port = parsed_url.port

        #CREATING PAYLOAD 
        if self.is_request_body == True:
            if self.port == 80:
                payload = f"POST {self.path} HTTP/1.1\r\nHost: {self.host}\r\nUser-Agent: Gurjog client\r\nConnection:close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {self.content_length}\r\nAccept: */*\r\n\r\n{self.request_body}"
            else:
                payload = f"POST {self.path} HTTP/1.1\r\nHost: {parsed_url.netloc}\r\nUser-Agent: Gurjog client\r\nConnection:close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {self.content_length}\r\nAccept: */*\r\n\r\n{self.request_body}"
        else:

            if self.port == 80:
                payload = f"POST {self.path} HTTP/1.1\r\nHost: {self.host}\r\nUser-Agent: Gurjog client\r\nConnection:close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 0\r\nAccept: */*\r\n\r\n"
            else:
                payload = f"POST {self.path} HTTP/1.1\r\nHost: {parsed_url.netloc}\r\nUser-Agent: Gurjog client\r\nConnection:close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 0\r\nAccept: */*\r\n\r\n"

        ##SENDING PAYLOAD
    
        self.connect(self.host, self.port)
    
        print(payload)
        self.sendall(payload)

        #RECEIVING AND DISPLAYING RESPONSE
        data = self.recvall(self.socket) 
        self.get_headers(data)
        self.code = int(self.get_code(data))
        self.body = self.get_body(data)
    
        #CLOSING 
        self.close() 
        return HTTPResponse(self.code, self.body)

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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
