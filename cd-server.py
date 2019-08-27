#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import syslog
import threading
import subprocess
import requests
import time
from threading import Thread
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

notification_max_tries = 4
notification_delay = 5

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()

    def do_POST(self):
        self._set_headers()
        self.wfile.write(json.dumps(self.process()).encode("utf-8"))

    def process(self):

        content_len = int(self.headers.get("Content-Length"))
        post_body = self.rfile.read(content_len)
        payload = json.loads(post_body.decode("utf-8"))

        if "ref" not in payload or "repository" not in payload:
            return {
                "error": "Incorrect payload"
            }

        branch = payload["ref"].split("/", 2)[2]
        name = payload["repository"]["name"] if "repository" in payload else None

        it = 0
        while "TASK_%i" % it in os.environ:
            repo = "TASK_%i" % it
            if (os.environ[repo] == "%s/%s" % (name, branch)):
                prnt("Matched task %s" % os.environ[repo])
                p = Thread(target = run_task, args=[repo])
                p.start()
            it += 1

        return {
            "tasks_processed": it
        }

def run_task(repo):
    try:
        output = subprocess.check_output(os.environ["%s_CMD" % repo] , stderr=subprocess.STDOUT, shell=True)
        prnt(notify(os.environ[repo], output.decode("utf-8"), 0))
    except Exception as e:
        prnt(notify(os.environ[repo], str(e), 0))


def notify(repo, output, notification_tries):
    global notification_max_tries, notification_delay
    url = os.environ["CD_NOTIFY_URL"]
    response = "Failed to notify"
    try:
        data = requests.post(url, json = {
            "parse_mode": "Markdown",
            "text": "*Automatic build completed*\nRepository: %s\nOutput:\n\n```bash\n%s\n```" % (repo, output)
        })
        response = data.json()
    except Exception as e:
        if (notification_tries <= notification_max_tries):
            notification_tries += 1
            time.sleep(notification_tries * notification_delay)
            return notify(repo, output, notification_tries)

    return response

def import_env():
    filepath = os.path.dirname(os.path.realpath(__file__)) + "/.env"
    with open(filepath) as fp:
        for cnt, line in enumerate(fp):
            parts = line.split("=", 2)
            if len(parts) == 2:
                os.environ[parts[0].strip()] = parts[1].strip()

def prnt(text, log_level=None):
    print(text)
    if (log_level == None):
        log_level = syslog.LOG_NOTICE

    syslog.syslog(log_level, text)

def get_interface():
    parts = urlparse(os.environ["CD_REMOTE_SERVER"] if "CD_REMOTE_SERVER" in os.environ else os.environ["CD_LOCAL_SERVER"])

    return (parts.hostname, parts.port)

def main():
    import_env()
    httpd = ThreadingHTTPServer(get_interface(), Server)

    prnt("Starting CD server...")
    httpd.serve_forever()

main()
