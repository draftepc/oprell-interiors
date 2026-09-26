"""Local dev server for the OPRELL site — serves fresh files, never lets the browser cache."""
import http.server, functools

PORT = 8123

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == '__main__':
    http.server.ThreadingHTTPServer(
        ('', PORT), functools.partial(Handler)
    ).serve_forever()
