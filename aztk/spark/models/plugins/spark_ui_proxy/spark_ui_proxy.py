#!/usr/bin/env python
# MIT License
# 
# Copyright (c) 2016 Alexis Seigneurin
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
from urllib.request import urlopen
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer

BIND_ADDR = os.environ.get("BIND_ADDR", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "80"))
URL_PREFIX = os.environ.get("URL_PREFIX", "").rstrip('/') + '/'
SPARK_MASTER_HOST = ""


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # redirect if we are hitting the home page
        if self.path in ("", URL_PREFIX):
            self.send_response(302)
            self.send_header("Location", URL_PREFIX + "proxy:" + SPARK_MASTER_HOST)
            self.end_headers()
            return
        self.proxyRequest(None)

    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        postData = self.rfile.read(length)
        self.proxyRequest(postData)

    def proxyRequest(self, data):
        targetHost, path = self.extractUrlDetails(self.path)
        targetUrl = "http://" + targetHost + path

        print("get: %s  host: %s  path: %s  target: %s" % (self.path, targetHost, path, targetUrl))

        proxiedRequest = urlopen(targetUrl, data)
        resCode = proxiedRequest.getcode()

        if resCode == 200:
            page = proxiedRequest.read()
            page = self.rewriteLinks(page, targetHost)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(page)
        elif resCode == 302:
            self.send_response(302)
            self.send_header("Location", URL_PREFIX + "proxy:" + SPARK_MASTER_HOST)
            self.end_headers()
        else:
            raise Exception("Unsupported response: " + resCode)

    def extractUrlDetails(self, path):
        if path.startswith(URL_PREFIX + "proxy:"):
            start_idx = len(URL_PREFIX) + 6  # len('proxy:') == 6
            idx = path.find("/", start_idx)
            targetHost = path[start_idx:] if idx == -1 else path[start_idx:idx]
            path = "" if idx == -1 else path[idx:]
        else:
            targetHost = SPARK_MASTER_HOST
            path = path
        return (targetHost, path)

    def rewriteLinks(self, page, targetHost):
        target = "{0}proxy:{1}/".format(URL_PREFIX, targetHost).encode()
        page = page.replace(b'href="/', b'href="' + target)
        page = page.replace(b"'<div><a href=' + logUrl + '>'",
                            b"'<div><a href=' + location.origin + logUrl.replace('http://', '/proxy:') + '>'")
        page = page.replace(b'href="log', b'href="' + target + b'log')
        page = page.replace(b'href="http://', b'href="' + URL_PREFIX.encode() + b'proxy:')
        page = page.replace(b'src="/', b'src="' + target)
        page = page.replace(b'action="', b'action="' + target)
        page = page.replace(b'"/api/v1/', b'"' + target + b'api/v1/')
        return page


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: <proxied host:port> [<proxy port>]")
        sys.exit(1)

    SPARK_MASTER_HOST = sys.argv[1]

    if len(sys.argv) >= 3:
        SERVER_PORT = int(sys.argv[2])

    print("Starting server on http://{0}:{1}".format(BIND_ADDR, SERVER_PORT))

    class ForkingHTTPServer(socketserver.ForkingMixIn, HTTPServer):
        def finish_request(self, request, client_address):
            request.settimeout(30)
            HTTPServer.finish_request(self, request, client_address)

    server_address = (BIND_ADDR, SERVER_PORT)
    httpd = ForkingHTTPServer(server_address, ProxyHandler)
    httpd.serve_forever()
