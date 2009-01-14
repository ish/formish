import logging

import os, signal, urllib, socket, time
from ConfigParser import ConfigParser
import subprocess
import unittest
from selenium import selenium

log = logging.getLogger(__name__)

def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    s.connect(('google.com', 0))
    return str(s.getsockname()[0])


def http_available(url):
    try:
        urllib.urlopen(url)
        return True
    except IOError:
        return False

def wait_for_http_to_stop(url, timeout=5):
    time_step = 0.01
    time_so_far = 0
    if http_available(url):
        while http_available(url):
            time.sleep(time_step)
            time_so_far += time_step
            if time_so_far > timeout:
                raise Exception("HTTP server didn't stop within %rs" % timeout)


def wait_for_http_to_start(url, timeout=5):
    time_step = 0.01
    time_so_far = 0
    if not http_available(url):
        while not http_available(url):
            time.sleep(time_step)
            time_so_far += time_step
            if time_so_far > timeout:
                raise Exception("HTTP server didn't start within %rs" % timeout)


def load_config(**defaults):
    defaults = dict(defaults)
    defaults['here'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../') )
    config = ConfigParser(defaults)
    config.read( os.path.abspath(os.path.join(os.path.dirname(__file__), '../../development.ini') ) )
    config.read( os.path.abspath(os.path.join(os.path.dirname(__file__), '../../testish.ini') ) )
    return config

class TestCase(unittest.TestCase):

    http_port = os.environ.get('HTTP_PORT', '8891')

    config = load_config(HTTP_PORT=http_port)
    
    _server_cmd = ['paster', 'serve', '--log-file','test.log','development.ini']
    _server_process = None
    server_url = 'http://%s:%s' % (local_ip(), http_port)

    _selenium_host = os.environ.get('SELENIUM_HOST', 'localhost')
    _selenium_port = int(os.environ.get('SELENIUM_PORT', 4444))
    _selenium_browser = os.environ.get('SELENIUM_BROWSER', '*firefox')
    selenium = None

    def dataFilePath(self, filename):
        if 'SELENIUM_BROWSER' in os.environ and os.environ['SELENIUM_BROWSER'] == '*chrome':
            return '/Volumes/testdata/%s'%filename
        else:
            return os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                'data',
                filename))

    def setUp(self):

        class verificationErrors(list):
            def append(self,item):
                if item == '':
                    import traceback
                    item = 'line number %s'%str(traceback.extract_stack()[-2][1]-1)
                list.append(self, item)

        self.__start_app_server()
        try:
            self.__start_selenium()
        except:
            self.__stop_app_server()
            raise
        self.verificationErrors = verificationErrors([])

    def tearDown(self):
        self.__stop_app_server()
        self.__stop_selenium()
        self.assertEqual([], self.verificationErrors)

    def __start_app_server(self):
        wait_for_http_to_stop(self.server_url)
        self._server_process = subprocess.Popen(self._server_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        wait_for_http_to_start(self.server_url)

    def __stop_app_server(self):
        os.kill(self._server_process.pid, signal.SIGKILL)
        wait_for_http_to_stop(self.server_url)

    def __start_selenium(self):
        self.selenium = selenium(self._selenium_host, self._selenium_port, self._selenium_browser, self.server_url)
        self.selenium.start()

    def __stop_selenium(self):
        self.selenium.stop()


