#!/usr/bin/env python3

"""
Server which lets you upload files securely over https.

On your server (after having installed cherrypy and edited conf.json):

    $ nohup python3 bottle_filebucket.py &

On your client:

    $ curl -i -X PUT -F token=BLS4G66XHBGOI -F filename=Test.pdf -F \
filedata=@SomeFile.pdf --insecure "https://localhost:8081/upload"

Bottle/HTTPS solution based on:
http://dgtool.blogspot.se/2011/12/ssl-encryption-in-python-bottle.html
"""

import json
import os
import subprocess
from bottle import route, run, request, Bottle, server_names, ServerAdapter

config = json.load(open('config.json'))
secret_token = config['secret_token']
cert_path = config['certificate_path']
priv_key_path = config['private_key_path']
destdir = config['destdir']
host = config['host']
port = config['port']


class MySSLCherryPy(ServerAdapter):
    def run(self, handler):
        from cherrypy import wsgiserver
        from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter
        server = wsgiserver.CherryPyWSGIServer((self.host, self.port), handler)
        server.ssl_adapter = BuiltinSSLAdapter(cert_path, priv_key_path)
        try:
            server.start()
        finally:
            server.stop()

server_names['mysslcherrypy'] = MySSLCherryPy

app = Bottle()


@app.route("/upload", method='PUT')
def upload():
    given_token = request.forms.get("token")
    if given_token != secret_token:
        return {'success': False, 'error': "Invalid token."}
    fileobj = request.files['filedata']

    if fileobj:
        filename = request.forms.get("filename", fileobj.filename)
        for char in r"^[^<>/{}[\]~`]*$":
            if char in fileobj.filename:
                return {"success": False,
                        "error": "Invalid characters in filename"}
        open(os.path.join(destdir, filename), 'wb').write(fileobj.file.read())

    return {"success": True}


if __name__ == '__main__':
    if not os.path.exists(cert_path) and\
       not os.path.exists(priv_key_path):
        subprocess.check_call(
            'openssl req -new -x509 -keyout %s -out %s -days 3650 -nodes -subj'
            ' "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com"' % (
                priv_key_path, cert_path), shell=True)
    run(app, host=host, port=port, debug=True, server='mysslcherrypy')
