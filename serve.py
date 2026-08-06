import sys
import http.server
import socket
import webbrowser
from threading import Timer

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_PORT = 8000
MAX_PORT_ATTEMPTS = 100

def find_free_port(start_port):
    """Finds the first available port starting from start_port."""
    for port in range(start_port, start_port + MAX_PORT_ATTEMPTS):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Set SO_REUSEADDR so port is reusable quickly
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("localhost", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Could not find an available port in range {start_port} to {start_port + MAX_PORT_ATTEMPTS - 1}")

def open_browser(port):
    """Opens the system web browser to the dashboard URL."""
    url = f"http://localhost:{port}/dashboard/"
    print(f"\n[INFO] System web browser opening: {url}\n")
    webbrowser.open(url)

def main():
    try:
        port = find_free_port(DEFAULT_PORT)
    except RuntimeError as e:
        print(f"[ERROR] Error: {e}")
        return

    # Set up the request handler and server
    handler = http.server.SimpleHTTPRequestHandler
    
    # Python 3.7+ has ThreadingHTTPServer which handles requests concurrently
    if hasattr(http.server, "ThreadingHTTPServer"):
        server_class = http.server.ThreadingHTTPServer
    else:
        server_class = http.server.HTTPServer

    try:
        server = server_class(("0.0.0.0", port), handler)
    except OSError as e:
        # Fallback to localhost if 0.0.0.0 is not allowed/working on the environment
        try:
            server = server_class(("127.0.0.1", port), handler)
        except OSError as e:
            print(f"[ERROR] Failed to bind to port {port}: {e}")
            return

    print("=" * 60)
    print(f"[SERVER] Univers Knowledge Dashboard Server")
    print(f"Serving directory: .")
    print(f"Local Address:      http://localhost:{port}/")
    print(f"Dashboard Link:     http://localhost:{port}/dashboard/")
    if port != DEFAULT_PORT:
        print(f"[WARN] Note: Port {DEFAULT_PORT} was already in use. Switched to {port}.")
    print("=" * 60)
    print("Press Ctrl+C to stop the server.\n")

    # Open browser slightly after server boots
    Timer(1.0, open_browser, args=[port]).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Univers Knowledge Dashboard Server. Goodbye!")

if __name__ == "__main__":
    main()
