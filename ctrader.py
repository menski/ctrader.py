import base64
import httplib
import urllib
import json
import os
import argparse
import ConfigParser
import getpass
import multiprocessing
import logging

# create logger
log = logging.getLogger('ctrader.py')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)5s - %(message)s'))
log.addHandler(ch)


class CaptchaWindow():
    """Window to input the answer for the captcha"""

    captcha_path = 'captcha.jpg'

    def __init__(self, image):
        with open(CaptchaWindow.captcha_path, 'wb') as f:
            f.write(base64.b64decode(image.split(',', 1)[1]))
        self.window = None
        self.entry = None
        self.finish = False
        self.answer = None
        self.gui()

    def gui(self):
        import pygtk
        import gtk
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('ctrader.py')
        self.window.connect("destroy", lambda w: gtk.main_quit())
        table = gtk.Table(3, 2, False)
        self.window.add(table)
        image = gtk.Image()
        image.set_from_file(CaptchaWindow.captcha_path)
        table.attach(image, 0, 2, 0, 1)
        image.show()
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.entry = gtk.Entry()
        table.attach(self.entry, 0, 2, 1, 2)
        self.entry.show()
        self.entry.connect("activate", self.quit)
        self.entry.connect("key_press_event", self.key_pressed)
        button = gtk.Button("Next")
        table.attach(button, 0, 1, 2, 3)
        button.show()
        button.connect("clicked", self.quit)
        button = gtk.Button("Stop")
        table.attach(button, 1, 2, 2, 3)
        button.show()
        button.connect("clicked", self.stop)
        table.show()
        self.window.show()
        self.escape = gtk.keysyms.Escape
        gtk.main()

    def key_pressed(self, widget, event, data=None):
        if event.keyval == self.escape:
            self.stop(widget)

    def stop(self, widget, data=None):
        self.finish = True
        self.quit(widget)

    def quit(self, widget, data=None):
        if self.entry.get_text():
            self.answer = self.entry.get_text()
        self.window.destroy()


class CaptchaTrader(object):
    """CaptchaTrader API"""

    def __init__(self, username, password):
        self.conn = httplib.HTTPConnection("api.captchatrader.com")
        self.username = username
        self.password = password
        self.ticket = None
        self.user_url = "username:{0}/password:{1}".format(
                urllib.quote(self.username),
                urllib.quote(self.password))

    def close(self):
        self.conn.close()

    def get(self, url):
        self.conn.request("GET", url)
        return self.response()

    def post(self, url, params):
        self.conn.request("POST", url, params,
                {"Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"})
        return self.response()

    def response(self):
        """Get response"""
        res = self.conn.getresponse()
        j = json.loads(res.read())
        log.debug('Response %s %s %s', res.status, res.reason, j[0])
        if j[0] == -1:
            log.error(j[1])
            return None
        else:
            return j

    def enqueue(self):
        """Enqueue user"""
        log.debug('Enqueue user %s', self.username)
        res = self.get("/enqueue/" + self.user_url)
        if res is None:
            return None
        else:
            self.ticket = res[0]
            return res[1]

    def credits(self):
        """Get credits of user"""
        log.debug('get credits for user %s', self.username)
        res = self.get("/get_credits/" + self.user_url)
        if res is None:
            return -1
        else:
            return res[1]

    def answer(self, value):
        """Answer captcha"""
        log.debug('Send answer for user %s: %s', self.username, value)
        if self.ticket is None:
            log.error('Invalid ticket number')
        else:
            params = urllib.urlencode({
                'username': self.username,
                'password': self.password,
                'ticket': self.ticket,
                'value': value})
            self.post("/answer/", params)
            self.ticket = None

    def dequeue(self):
        """Dequeue user"""
        log.debug('Dequeue user: %s', self.username)
        params = urllib.urlencode({
                'username': self.username,
                'password': self.password})
        self.post("/dequeue/", params)


def options():
    """Get options from commandline"""
    parser = argparse.ArgumentParser(
            description='Answer captchas from www.captchatrader.com')
    parser.add_argument('-u', '--username', default=None)
    parser.add_argument('-p', '--password', default=None)
    parser.add_argument('-c', '--config', default='~/.ctrader')
    return parser.parse_args()


def config(file):
    """Get user credentials from configfile"""
    path = os.path.expanduser(file)
    if os.path.exists(path):
        cp = ConfigParser.SafeConfigParser()
        cp.read([path])
        users = []
        for sec in cp.sections():
            users.append([cp.get(sec, "username"), cp.get(sec, "password")])
        return users
    else:
        return None


def userinput():
    """Get username and password from user"""
    username = raw_input('Username: ')
    password = getpass.getpass('Password/Passkey: ')
    return [username, password]


def run(creds):
    """Start requesting captchas for user"""
    log.info('start event loop for user %s', creds[0])
    finish = False
    ct = CaptchaTrader(creds[0], creds[1])
    while(not finish):
        captcha = ct.enqueue()
        if captcha is not None:
            try:
                frame = CaptchaWindow(captcha)
                finish = frame.finish
                if frame.answer is not None:
                    ct.answer(frame.answer)
                    credits = ct.credits()
                    log.info('Credits for %s: %d', creds[0], credits)
                elif not finish:
                    log.debug('No answer given')
                    ct.dequeue()
            except Exception, err:
                log.error(err)
                break
    log.info('stop event loop for user %s', creds[0])
    ct.dequeue()
    ct.close()


def main():
    """Main function"""
    opts = options()
    if opts.username is None or opts.password is None:
        users = config(opts.config)
        if users is None or not users:
            log.info('use user input')
            run(userinput())
        else:
            log.info('use configuration file')
            pool = multiprocessing.Pool(len(users))
            job = pool.map_async(run, users)
            job.wait()
    else:
        log.info('use commandline options')
        run([opts.username, opts.password])


if __name__ == '__main__':
    main()
