import errno
import socket
from url import HTTPRequest, InvalidRequest



class HTTPServer:
    def __init__(self, host="0.0.0.0", port=80, backlog=5):
        self.host = host
        self.port = port
        self.backlog = backlog
        self._routes = (
            dict()
        )  # stores link between (method, path) and function to execute

    def route(self, method="GET", path="/"):
        """Decorator which connects method and path to the decorated function."""

        if (method, path) in self._routes:
            raise HTTPServerError(f"route{(method, path)} already registered")

        def wrapper(function):
            self._routes[(method, path)] = function

        return wrapper


    def start(self):
        print("server listening on 0.0.0.0:80")
        s = socket.socket()
        s.bind(('0.0.0.0', 80))
        s.listen(self.backlog)

        while True:
            conn, addr = s.accept()
            print('Connect from %s' % str(addr))


            request_line = conn.readline()
            print(f"{request_line=}")

            if request_line is None:
                raise OSError(errno.ETIMEDOUT)
            elif request_line in [b"", b"\r\n"]:
                print(f"empty request line from {addr[0]}")
                conn.close()
                continue


            try:
                print("initialising request object")
                request = HTTPRequest(request_line)
            except InvalidRequest as e:
                print("invalid request")
                while True:
                    # read and discard header fields
                    line = conn.readline()
                    if line is None:
                        raise OSError(errno.ETIMEDOUT)
                    if line in [b"", b"\r\n"]:
                        break

                conn.write('HTTP/1.1 400 OK\r\n')
                conn.write('Connection: close\r\n')
                conn.write("Content-Type: text/plain\r\n")
                conn.write(repr(e).encode("utf-8"))
                conn.close()
                continue



            print("parsing remaining headers")
            while True:
                # read header fields and add name / value to dict 'header'
                line = conn.readline()
                print(f"{line=}")
                if line is None:
                    print("No line. Raising error")
                    raise OSError(errno.ETIMEDOUT)

                if line in [b"", b"\r\n"]:
                    break
                else:
                    if line.find(b":") != 1:
                        name, value = line.split(b":", 1)
                        request.header[name] = value.strip()


            print("finished reading headers")
            print("checking for body")
            if request.header.get(b"Content-Length"):
                print("request has body")
                length = int(str(request.header[b"Content-Length"], "utf-8"))
                request.body = conn.recv(length)
                print(f"{request.body=}")


            func = self._routes.get((request.method, request.path))
            if func:
                func(conn, request)
            else:
                conn.write('HTTP/1.1 404 Not Found\r\n')
                conn.write('Connection: close\r\n')
                conn.write("Content-Type: text/plain\r\n")


            print("closing connection")
            conn.close()
