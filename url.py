class InvalidRequest(Exception):
    pass


class HTTPRequest:
    def __init__(self, request_line) -> None:
        """Separate an HTTP request line in its elements.
        :param bytes request_line: the complete HTTP request line
        :return Request: instance containing
                method      the request method ("GET", "PUT", ...)
                url         the request URL, including the query string (if any)
                path        the request path from the URL
                query       the query string from the URL (if any, else "")
                version     the HTTP version
                parameters  dictionary with key-value pairs from the query string
                header      empty dict, placeholder for key-value pairs from request header fields
        :raises InvalidRequest: if line does not contain exactly 3 components separated by spaces
                                if method is not in IETF standardized set
                                aside from these no other checks done here
        """
        try:
            self.method, self.url, self.version = request_line.decode("utf-8").split()
            # note that method, url and version are str, not bytes
        except ValueError:
            raise InvalidRequest(f"Expected 3 elements in {request_line}")

        if self.version.find("/") != -1:
            self.version = self.version.split("/", 1)[1]

        if self.method not in [
            "GET",
            "HEAD",
            "POST",
            "PUT",
            "DELETE",
            "CONNECT",
            "OPTIONS",
            "TRACE",
        ]:
            raise InvalidRequest(f"Invalid method {self.method} in {request_line}")

        if self.url.find("?") != -1:
            self.path, self.query = self.url.split("?", 1)
            self.parameters = query(self.query)
        else:
            self.path = self.url
            self.query = ""
            self.parameters = dict()

        self.header = dict()


def query(query):
    """Place all key-value pairs from a request URLs query string into a dict.
    Example: request b"GET /page?key1=0.07&key2=0.03&key3=0.13 HTTP/1.1\r\n"
    yields dictionary {'key1': '0.07', 'key2': '0.03', 'key3': '0.13'}.
    :param str query: the query part (everything after the '?') from an HTTP request line
    :return dict: dictionary with zero or more entries
    """
    d = dict()
    if len(query) > 0:
        for pair in query.split("&"):
            try:
                key, value = pair.split("=", 1)
                if key not in d:  # only first occurrence taken into account
                    d[key] = value
            except ValueError:  # skip malformed parameter (like missing '=')
                pass

    return d
