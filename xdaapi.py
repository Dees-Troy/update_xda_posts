import xmlrpclib


API_URL="http://forum.xda-developers.com/mobiquo/mobiquo.php"


# from http://www.lunch.org.uk/wiki/xmlrpccookies - edited
class CookieTransport(xmlrpclib.Transport):
    """A Transport request method that retains cookies over its lifetime.

    The regular xmlrpclib transports ignore cookies. Which causes
    a bit of a problem when you need a cookie-based login, as with
    the Bugzilla XMLRPC interface.

    So this is a helper for defining a Transport which looks for
    cookies being set in responses and saves them to add to all future
    requests.
    """
    # Inspiration drawn from
    # http://blog.godson.in/2010/09/how-to-make-python-xmlrpclib-client.html
    # http://www.itkovian.net/base/transport-class-for-pythons-xml-rpc-lib/
    #
    # Note this must be an old-style class so that __init__ handling works
    # correctly with the old-style Transport class. If you make this class
    # a new-style class, Transport.__init__() won't be called.

    cookies = []
    def send_cookies(self, connection):
        if self.cookies:
            cookies_str= "; ".join(self.cookies)
            connection.putheader("Cookie", cookies_str)

    def request(self, host, handler, request_body, verbose=0):
        self.verbose = verbose

        # issue XML-RPC request
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.send_cookies(h)
        self.send_user_agent(h)
        self.send_content(h, request_body)

        # Deal with differences between Python 2.4-2.6 and 2.7.
        # In the former h is a HTTP(S). In the latter it's a
        # HTTP(S)Connection. Luckily, the 2.4-2.6 implementation of
        # HTTP(S) has an underlying HTTP(S)Connection, so extract
        # that and use it.
        try:
            response = h.getresponse()
        except AttributeError:
            response = h._conn.getresponse()

        # Add any cookie definitions to our list.
        for header in response.msg.getallmatchingheaders("Set-Cookie"):
            val = header.split(": ", 1)[1]
            cookie = val.split(";", 1)[0]
            self.cookies.append(cookie)

        if response.status != 200:
            raise xmlrpclib.ProtocolError(host + handler, response.status,
                                          response.reason, response.msg.headers)

        return self.parse_response(response)

class XdaTransport(CookieTransport):
    # from python2.7 version of xmlrpclib - we have to ignore whitespace before <?xml, cause
    # one the these things sux and don't do what they are supposed to do: XDA, xmlrpclib, xml parsing lib
    def parse_response(self, response):
        # read response data from httpresponse, and parse it

        # Check for new http response object, else it is a file object
        if hasattr(response,'getheader'):
            if response.getheader("Content-Encoding", "") == "gzip":
                stream = xmlrpclib.GzipDecodedResponse(response)
            else:
                stream = response
        else:
            stream = response

        p, u = self.getparser()

        # CHANGE-START
        first=True
        # CHANGE-END

        while 1:
            data = stream.read(1024)
            if not data:
                break
            if self.verbose:
                print "body:", repr(data)

            # CHANGE-START
            if first:
                first=False
                if data[0] == "\n":
                    data = data[1:]
            # CHANGE-END
            p.feed(data)

        if stream is not response:
            stream.close()
        p.close()

        return u.close()

class XdaApi():
    def __init__(self):
        self.api = xmlrpclib.ServerProxy(API_URL, XdaTransport(), "UTF-8", False)

    def __getattr__(self, name):
        return self.api.__getattr__(name)

    def login(self, user, password):
        res = self.api.login(xmlrpclib.Binary(user), xmlrpclib.Binary(password))
        if not res["result"]:
            raise Exception("Failed to log-in with \"" + res["result_text"].data + "\"")

    def logout_user(self):
        self.api.logout_user()

    def get_raw_post(self, post_id):
        res = self.api.get_raw_post(str(post_id))
        if "result" in res and not res["result"]:
            raise Exception("Failed to get post: \"" + res["result_text"].data + "\"")
        return res

    def save_raw_post(self, post_id, post_title, post_content):
        res = self.api.save_raw_post(str(post_id), xmlrpclib.Binary(post_title), xmlrpclib.Binary(post_content))
        if not res["result"]:
            raise Exception("Failed to save post: \"" + res["result_text"].data + "\"")

    def reply_post(self, forum_id, topic_id, post_title, post_content):
        res = self.api.reply_post(str(forum_id), str(topic_id), xmlrpclib.Binary(post_title), xmlrpclib.Binary(post_content))
        if not res["result"]:
            raise Exception("Failed to reply to the post: \"" + res["result_text"].data + "\"")
