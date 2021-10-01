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
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        split_data = data.split(" ")
        #https://stackoverflow.com/questions/23086383/how-to-test-nonetype-in-python to test for none
        if split_data[1] is not None: #test to make sure we got the code as expected
            code = int((split_data)[1])
        else:
            print("Error getting the status code")
            exit
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        split_data = data.split("\r\n\r\n")
        #https://stackoverflow.com/questions/23086383/how-to-test-nonetype-in-python to test for none
        if split_data[1] is not None: #test to see if there is a body ie. data after our CRLF of the reponse
            body = (split_data)[1]
        else:
            body = ""
        return body
    
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
        code = 500 #inital value will be changed by our response
        body = "" #inital value will be changed by our response
        #https://docs.python.org/3/library/urllib.parse.html and https://pymotw.com/3/urllib.parse/ used to parse URLs
        host = urllib.parse.urlparse(url).hostname #get the hostname of the server
        port = urllib.parse.urlparse(url).port #get the port of the server
        #https://stackoverflow.com/questions/23086383/how-to-test-nonetype-in-python to test for none
        if (port is None): #use the default port ie. 80
            port = 80
        if (host is None): #reuturn our defaults as we need a hostname
            return HTTPResponse(code, body)
        self.connect(host,port) #connect to our server
        
        host_and_port = urllib.parse.urlparse(url).netloc
        #https://docs.python.org/3/library/urllib.parse.html and https://pymotw.com/3/urllib.parse/ used to parse URLs
        query = urllib.parse.urlparse(url).query #get the query parameters from our URL
        path = urllib.parse.urlparse(url).path #get the path from our URL
        if path == "": #if no path supplied in the URL then use the default path ie /
            path = "/"
        if query == "" and args is not None: #no query but we do have args that we would like to have in the path for our reuqest
            path = path + "?" #indicates that this is first query parameter
        if query != "": #we do have query parameters
            path = path +"?"+ query #add in ? to signify we have query parameters and add our query parameters from the URL given (not yet args)
            if args is not None: #we have more parameters to add so we need to append an &
                path = path + "&"
        firstParameter = True #used to indicate that our first parameter does not need to have an & added
        if (args is not None):
            #https://www.w3schools.com/python/python_for_loops.asp for the idea to do a for loop here
            for arg in args:
                #https://stackoverflow.com/questions/5607551/how-to-urlencode-a-querystring-in-python to get correct formatting for our parameters
                formatted_arg_key = urllib.parse.quote_plus(arg)
                if firstParameter == True:
                    path = path + formatted_arg_key
                else:
                    path = path + "&"+formatted_arg_key
                #https://www.geeksforgeeks.org/python-accessing-key-value-in-dictionary/ to access the vale stored in agrs for our current parmater
                formatted_arg_value = urllib.parse.quote_plus(args[arg])
                path = path + "="+formatted_arg_value
                firstParameter = False
        #add all of the required headers
        GetInfo = "GET "+path+ " HTTP/1.1\r\n"
        GetInfo = GetInfo + "Host: " + host_and_port + "\r\n"
        GetInfo = GetInfo + "Connection: close\r\n"
        GetInfo = GetInfo + "Accept: application/octet-stream\r\n"
        GetInfo = GetInfo + "User-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0\r\n" #this is what I use. Got it by 
        #using the network view in the inspect page of my web browser
        GetInfo = GetInfo + "\r\n" #demonstrates end of the header
        self.sendall(GetInfo)
        responseInfo = self.recvall(self.socket)
        body = self.get_body(responseInfo)
        code = self.get_code(responseInfo)
        print(code)
        print(body)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500 #inital value will be changed by our response
        body = "" #inital value will be changed by our response
        #https://docs.python.org/3/library/urllib.parse.html and https://pymotw.com/3/urllib.parse/ used to parse URLs
        host = urllib.parse.urlparse(url).hostname #get the hostname of the server
        port = urllib.parse.urlparse(url).port #get the port of the server
        #https://stackoverflow.com/questions/23086383/how-to-test-nonetype-in-python to test for none
        if (port is None):
            port = 80 #default port
        if (host is None):
            return HTTPResponse(code, body) #need host
        self.connect(host,port) #connect to server
        #https://docs.python.org/3/library/urllib.parse.html and https://pymotw.com/3/urllib.parse/ used to parse URLs
        host_and_port = urllib.parse.urlparse(url).netloc #get the host and port
        path = urllib.parse.urlparse(url).path
        #basic headers that are unchanged is there are or are not args
        PostInfo = "POST "+path+ " HTTP/1.1\r\n"
        PostInfo = PostInfo + "Host: " + host_and_port + "\r\n"
        PostInfo = PostInfo + "User-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0\r\n"
        PostInfo = PostInfo + "Content-type: application/x-www-form-urlencoded \r\n"
        if (args is not None): #test to see if there are any paramters
            total_length = 0
            request_body = ""
            #https://www.w3schools.com/python/python_for_loops.asp
            for arg in args:
                if (total_length == 0): #we need this if statement as our first parameter should not start with &
                    #https://stackoverflow.com/questions/5607551/how-to-urlencode-a-querystring-in-python to get correct formatting for our parameters
                    formatted_arg_key = urllib.parse.quote_plus(arg) #get the key correctly formatted
                    request_body = request_body + formatted_arg_key #add & to indicate a query parameter
                    #https://www.tutorialkart.com/python/how-to-find-length-of-bytes-in-python/ #add to the total legnth of the body the length of key
                    total_length = total_length + len(formatted_arg_key)
                else:
                    #https://stackoverflow.com/questions/5607551/how-to-urlencode-a-querystring-in-python to get correct formatting for our parameters
                    formatted_arg_key = urllib.parse.quote_plus(arg) #get the key correctly formatted
                    request_body = request_body + "&"+formatted_arg_key #add & to indicate a query parameter
                
                
                    #https://www.tutorialkart.com/python/how-to-find-length-of-bytes-in-python/ #add to the total legnth of the body the length of key + length of &
                    total_length = total_length + len(formatted_arg_key)+1
                
                #https://www.geeksforgeeks.org/python-accessing-key-value-in-dictionary/ to access the vale stored in agrs for our current parmater
                formatted_arg_value = urllib.parse.quote_plus(args[arg])
                request_body = request_body + "="+formatted_arg_value
                total_length = total_length + len(formatted_arg_value)+1 #add to the total legnth of the body the length of value + length of =
            PostInfo = PostInfo + "Content-length: "+str(total_length)+ "\r\n" #add our content length
            PostInfo = PostInfo + "\r\n" #add the CRLF
            PostInfo = PostInfo + request_body #add the body
        else:
            PostInfo = PostInfo + "Content-length: 0\r\n" #no query paramters
            PostInfo = PostInfo + "\r\n" #add CRLF
        self.sendall(PostInfo)
        responseInfo = self.recvall(self.socket)
        body = self.get_body(responseInfo)
        code = self.get_code(responseInfo)
        print(code)
        print(body)
        self.close()
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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
