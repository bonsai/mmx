import http.server
import socketserver
import threading
import time
import urllib.request

PORT = 8080
DIRECTORY = "C:/Users/0501JP/mmx"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def test():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()
        time.sleep(1)
        try:
            resp = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=5)
            print(resp.read()[:500].decode())
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test()
