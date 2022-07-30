# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
An example IRC log bot - logs a channel's events to a file.

If someone says the bot's name in the channel followed by a ':',
e.g.

  <foo> logbot: hello!

the bot will reply:

  <logbot> foo: I am a log bot

Run this script with two arguments, the channel name the bot should
connect to, and file to log to, e.g.:

  $ python ircLogBot.py test test.log

will log channel #test to the file 'test.log'.
"""
# system imports
import magic
import random
import sys
import time
import treq
import txtorcon
import unicodedata

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log
from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks, ensureDeferred
from twisted.internet.endpoints import UNIXClientEndpoint

from .Send import Send


class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """

    def __init__(self, file):
        """ """
        self.file = file

    def log(self, message):
        """
        Write a message to the file.
        """
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        print(f"{timestamp} {message}\n")
        self.file.write(f"{message}\n")
        self.file.flush()

    def close(self):
        self.file.close()


class ListBot(irc.IRCClient):
    """ """

    nickname = ""  # nickname
    password = ""  # server pass

    def __init__(self, irc_network, message, log_filename):
        """ """
        self.nickname = irc_network["nickname"]  # nickname
        self.password = irc_network["password"]  # server pass
        self.messages = message.split(".")
        self.filename = log_filename
        self.channels = []
        self.users = []
        self.irc_network = irc_network
        self._namescallback = {}
        self._listcallback = {}

    def action(self, user, channel, msg):
        """
        This will get called when the bot sees someone do an action.
        """
        user = user.split("!", 1)[0]
        self.logger.log("* {} {}".format(user, msg))

    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + "^"

    def connectionMade(self):
        """ """
        irc.IRCClient.connectionMade(self)
        print("connectionMade")
        self.logger = MessageLogger(open(self.filename, "w"))
        print("{} [connected to {}]".format(time.asctime(time.localtime(time.time())), self.irc_network["server"]))

    def connectionLost(self, reason):
        """ """
        irc.IRCClient.connectionLost(self, reason)
        print(reason)
        print("{} [disconnected from {}]".format(time.asctime(time.localtime(time.time())), self.irc_network["server"]))
        self.logger.close()

    # callbacks for events
    def signedOn(self):
        """
        Called when bot has succesfully signed on to server.
        """
        #
        self.names

    def joined(self, channel):
        """
        This will get called when the bot joins the channel.
        """
        self.logger.log("[Joined {}]".format(channel))

    def left(self, channel):
        """
        This will get called when the bot joins the channel.
        """
        self.logger.log("[Left {}]".format(channel))

    def names(self, channel):
        """ """
        d = defer.Deferred()
        if channel not in self._namescallback:
            self._namescallback[channel] = ([], [])

        self._namescallback[channel][0].append(d)
        self.sendLine("NAMES {}".format(channel))
        return d

    def channels(self):
        """ """
        d = defer.Deferred()
        self._listcallback[0].append(d)
        self.sendLine("LIST")
        return d

    def lineReceived(self, line):
        """ """
        if bytes != str and isinstance(line, bytes):
            # decode bytes from transport
            m = magic.Magic(mime_encoding=True)
            encoding = m.from_buffer(line)
            print(">>> encoding ", encoding)
            if encoding in ["binary", "unknown-8bit"]:
                return
            line = line.decode(encoding)
        #
        line = irc.lowDequote(line)
        try:
            prefix, command, params = irc.parsemsg(line)
            if command in irc.numeric_to_symbolic:
                command = irc.numeric_to_symbolic[command]
            self.handleCommand(command, prefix, params)
        except irc.IRCBadMessage:
            self.badMessage(line, *sys.exc_info())

    # irc callbacks
    def irc_unknown(self, prefix, command, params):
        """
        Called by L{handleCommand} on a command that doesn't have a defined
        handler. Subclasses should override this method.
        """
        print(">>> irc_unknown", command, prefix, params)

    def irc_NICK(self, prefix, params):
        """
        Called when an IRC user changes their nickname.
        """
        old_nick = prefix.split("!")[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))

    def irc_RPL_LISTSTART(self, prefix, params):
        """ """
        print(">>> irc_RPL_LISTSTART", prefix, params)

    def irc_RPL_LIST(self, prefix, params):
        """ """
        print(">>> irc_RPL_LIST", prefix, params)
        self.logger.log(params[1])
        self.channels.append(params[1])

    def irc_RPL_LISTEND(self, prefix, params):
        print("irc_RPL_LISTEND", prefix, params)
        # self.list_finished = True
        for channel in self.channels:
            print(channel)
            super(irc.IRCClient, self).join(channel)
            for message in self.messages:
                super(irc.IRCClient, self).msg(channel, message)
                print(">>> {} - {}".format(channel, message))
                time.sleep(1)
            super(irc.IRCClient, self).leave(channel)
            time.sleep(1)

    def irc_RPL_NAMESSTART(self, prefix, params):
        """ """
        print(">>> irc_RPL_NAMESSTART", prefix, params)

    def irc_RPL_NAMREPLY(self, prefix, params):
        """ """
        channel = params[2].lower()
        nicklist = params[3].split(" ")
        #
        if channel not in self._namescallback:
            return
        #
        n = self._namescallback[channel][1]
        n += nicklist

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        """ """
        print(">>> irc_RPL_NAMESEND", prefix, params)
        channel = params[1].lower()
        #
        if channel not in self._namescallback:
            return
        #
        callbacks, namelist = self._namescallback[channel]
        for cb in callbacks:
            cb.callback(namelist)
        #
        del self._namescallback[channel]

    """
    def got_names(nicklist):
        log.msg(nicklist)

    self.names("#some channel").addCallback(got_names)
    """

    """
    def irc_RPL_NAMESEND(self, prefix, params):
        self.users = [u for u in set(self.users) if u not in ["NickServ", "FloodServ", "*"]]
        for user in self.users:
            print(user)
            for message in self.messages:
                super(irc.IRCClient, self).msg(user, self.message)
                time.sleep(1)
            print(">>> {} - {}".format(user, self.message))
            time.sleep(1)
    """


class LogBotFactory(protocol.ClientFactory):
    """
    A factory for LogBots.
    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, irc_network, message, log_filename):
        """ """
        self.irc_network = irc_network
        self.message = message
        self.filename = log_filename

    def buildProtocol(self, addr):
        """ """
        p = ListBot(self.irc_network, self.message, self.filename)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """
        If we get disconnected, reconnect to server.
        """
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print(
            "{}[connection to {} failed] {}".format(
                time.asctime(time.localtime(time.time())), self.irc_network["server"], reason
            )
        )
        if reactor.running:
            reactor.stop()


class SendIRC(Send):
    """
    A class used to represent a Configuration object

    Attributes
    ----------
    key : str
        a encryption key
    data : dict
        configuration data
    encrypted_config : bool
        use an encrypted configuration file
    config_file_path : str
        path to the configuration file
    key_file_path : str
        path to encryption key file
    gpg : gnupg.GPG
        python-gnupg gnupg.GPG

    Methods
    -------
    generate_key()
        Generates a new encryption key from a password + salt
    """

    def __init__(self, encrypted_config=True, config_file_path="auth.json", key_file_path=None):
        """
        Class init

        Parameters
        ----------
        encrypted_config : bool
            use an encrypted configuration file
        config_file_path : str
            path to the configuration file
        key_file_path : str
            path to encryption key file
        """
        super().__init__(encrypted_config, config_file_path, key_file_path)
        self.irc = self.data["irc"]
        # self.active_irc_network = self.data["irc"]["active_network"]
        # self.irc_network = self.data["irc"]["networks"][self.active_irc_network]

    async def tor_run(reactor):
        """ """
        tor = await txtorcon.connect(reactor, UNIXClientEndpoint(reactor, "/var/run/tor/control"))

        print("Connected to Tor version {}".format(tor.version))

        url = "https://www.torproject.org:443"
        print("Downloading {}".format(repr(url)))
        resp = await treq.get(url, agent=tor.web_agent())

        print("   {} bytes".format(resp.length))
        data = await resp.text()
        print(
            "Got {} bytes:\n{}\n[...]{}".format(
                len(data),
                data[:120],
                data[-120:],
            )
        )

        print("Creating a circuit")
        state = await tor.create_state()
        circ = await state.build_circuit()
        await circ.when_built()
        print("  path: {}".format(" -> ".join([r.ip for r in circ.path])))

        print("Downloading meejah's public key via above circuit...")
        config = await tor.get_config()
        resp = await treq.get(
            "https://meejah.ca/meejah.asc",
            agent=circ.web_agent(reactor, config.socks_endpoint(reactor)),
        )
        data = await resp.text()
        print(data)

    def run(self, message):
        # initialize logging
        log.startLogging(sys.stdout)
        print(message)
        #
        irc_networks = [net for net in self.irc["networks"] if net["active"]]
        for network in irc_networks:
            print(network)
            # create factory protocol and application
            network_name = network["server"].split(".")[1]
            factory = LogBotFactory(network, message, "log/{}.log".format(network_name))
            # connect factory to this host and port
            # reactor.connectSSL(network["server"], network["port"], factory, ssl.ClientContextFactory())
            reactor.connectTCP(network["server"], 6667, factory)
        # run bot
        reactor.run()
