# system imports
import magic
import os
import random
import sys
import time
import treq
import txtorcon
import unicodedata
from termcolor import colored

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import (
    defer,
    endpoints,
    protocol,
    reactor,
    ssl,
    task,
    threads,
)
from twisted.python import log

#
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import deferLater, react
from twisted.internet.endpoints import UNIXClientEndpoint

from ..config.Config import Config


class ListBotIRCProtocol(irc.IRCClient):
    """
    Description:
    ------------

    Attributes:
    ----------

    Methods:
    --------
    """

    def __init__(self, logger, description):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        self.deferred = defer.Deferred()
        self.hostname = description["network"]["server"]
        self.nickname = description["network"]["nickname"]  # nickname
        self.password = description["network"]["password"]  # server pass
        self.messages = description["messages"]
        self.logger = logger
        self._names_callback = {}
        self._list_callback = {}
        # validate message length
        for message in self.messages:
            if len(message) > 500:
                print(
                    "{} message length {}, pls rephrase to avoid flood".format(
                        message,
                        len(message)
                    )
                )
                exit(1)

    def _sendMessage(self, msg, target, nick=None):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        if nick:
            msg = "%s, %s" % (nick, msg)
        self.msg(target, msg)

    def _showError(self, failure):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        return failure.getErrorMessage()

    def action(self, user, channel, msg):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        user = user.split("!", 1)[0]
        self.logger.log("* {} {}".format(user, msg))

    def alterCollidedNick(self, nickname):
        """
        Description:
        ------------

        Parameters:
        -----------

        """
        
        return nickname + "^"

    def command_ping(self, rest):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        return "Pong."

    def command_saylater(self, rest):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        when, sep, msg = rest.partition(" ")
        when = int(when)
        d = defer.Deferred()
        # A small example of how to defer the reply from a command. callLater
        # will callback the Deferred with the reply after so many seconds.
        reactor.callLater(when, d.callback, msg)
        # Returning the Deferred here means that it'll be returned from
        # maybeDeferred in privmsg.
        return d

    def connectionMade(self):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        irc.IRCClient.connectionMade(self)
        print("connectionMade")
        
        print(
            colored(
                "{} [connected to {}]".format(
                    time.asctime(time.localtime(time.time())),
                    self.hostname,
                ),
                "white",
                "on_green",
            )
        )

    def connectionLost(self, reason):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(reason)
        print(
            colored(
                "{} [disconnected from {}]".format(
                    time.asctime(time.localtime(time.time())),
                    self.hostname,
                ),
                "white",
                "on_red",
            )
        )
        self.deferred.errback(reason)

    def lineReceived(self, line):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        if bytes != str and isinstance(line, bytes):
            # decode bytes from transport
            m = magic.Magic(mime_encoding=True)
            encoding = m.from_buffer(line)
            print(">>> encoding ", encoding)
            if encoding in ["binary", "unknown-8bit"]:
                return
            line = line.decode(encoding)

        line = irc.lowDequote(line)

        try:
            prefix, command, params = irc.parsemsg(line)
            if command in irc.numeric_to_symbolic:
                command = irc.numeric_to_symbolic[command]
            self.handleCommand(command, prefix, params)
        except irc.IRCBadMessage:
            self.badMessage(line, *sys.exc_info())

    def joined(self, channel):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        self.logger.log("[Joined {}]".format(channel))

    def left(self, channel):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        self.logger.log("[Left {}]".format(channel))

    def get_names(self, server):
        """ """

        d = defer.Deferred()
        server_tag = server.split(".")[-2]
        if server_tag not in self._names_callback:
            self._names_callback[server_tag] = ([], [])

        self._names_callback[server_tag][0].append(d)
        self.sendLine("NAMES")
        return d

    def get_channels(self, server):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        d = defer.Deferred()
        server_tag = server.split(".")[-2]
        if server_tag not in self._list_callback:
            self._list_callback[server_tag] = ([], [])

        self._list_callback[server_tag][0].append(d)
        self.sendLine("LIST")
        return d

    def got_channels(self, channel_list):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        def channel_action(channel, channel_ndx, num_channels):
            """
            Description:
            ------------

            Parameters:
            -----------

            """

            self.join(channel)
            for message in self.messages:
                print(
                    colored(
                        ">>> channel:{}@{} {}/{} - {}: ".format(
                            channel,
                            self.hostname,
                            channel_ndx,
                            num_channels,
                            message
                        ),
                        "cyan",
                    )
                )
                self.msg(channel, message)
                time.sleep(1)

            self.leave(channel)

        print(
            colored(
                ">>> server: {} channels: {}".format(
                    self.hostname, channel_list
                ),
                "yellow",
            )
        )
        for channel_ndx, channel in enumerate(channel_list, start=1):
            reactor.callInThread(channel_action, channel, channel_ndx, len(channel_list))

    def got_names(self, nick_list):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        def nick_action(nick, nick_ndx, num_nicks):
            """
            Description:
            ------------

            Parameters:
            -----------

            """

            for message in self.messages:
                print(
                    colored(
                        ">>> message to user: {}@{} {}/{} - {}".format(
                            nick,
                            self.hostname,
                            nick_ndx,
                            num_nicks,
                            message
                        ),
                        "cyan",
                    )
                )
                self.msg(nick, message)
                time.sleep(1)

        operator_tags = ["@", "%", "+", "~", "&", "]", " "]
        nick_list = [
            nick
            for nick in nick_list
            if not any(nick.startswith(ch) for ch in operator_tags)
            and not nick.endswith("Serv")
        ]
        print(
            colored(
                ">>> server: {} names: {}".format(self.hostname, nick_list),
                "yellow",
            )
        )
        for nick_ndx, nick in enumerate(nick_list, start=1):
            reactor.callInThread(nick_action, nick, nick_ndx, len(nick_list))

    def privmsg(self, user, channel, message):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        nick, _, host = user.partition("!")
        message = message.strip()
        if not message.startswith("!"):  # not a trigger command
            return  # so do nothing
        command, sep, rest = message.lstrip("!").partition(" ")

        # Get the function corresponding to the command given.
        func = getattr(self, "command_" + command, None)

        # Or, if there was no function, ignore the message.
        if func is None:
            return

        # maybeDeferred will always return a Deferred. It calls func(rest), and
        # if that returned a Deferred, return that. Otherwise, return the
        # return value of the function wrapped in
        # twisted.internet.defer.succeed. If an exception was raised, wrap the
        # traceback in twisted.internet.defer.fail and return that.
        d = defer.maybeDeferred(func, rest)

        # Add callbacks to deal with whatever the command results are.
        # If the command gives error, the _show_error callback will turn the
        # error into a terse message first:
        d.addErrback(self._showError)

        # Whatever is returned is sent back as a reply:
        if channel == self.nickname:
            # When channel == self.nickname, the message was sent to the bot
            # directly and not to a channel. So we will answer directly too:
            d.addCallback(self._sendMessage, nick)
        else:
            # Otherwise, send the answer to the channel, and use the nick
            # as addressing in the message itself:
            d.addCallback(self._sendMessage, channel, nick)

    # callbacks for events
    def signedOn(self):
        """
        Description:    Called when bot has succesfully signed on to server.
        """

        self.get_channels(self.hostname).addCallback(self.got_channels)
        self.get_names(self.hostname).addCallback(self.got_names)

    # irc callbacks
    def irc_unknown(self, prefix, command, params):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(
            colored(
                ">>> irc_unknown {} - {} - {}".format(command, prefix, params),
                "blue",
            )
        )

    def irc_NICK(self, prefix, params):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        old_nick = prefix.split("!")[0]
        new_nick = params[0]
        self.logger.log("{} is now known as {}".format(old_nick, new_nick))

    def irc_RPL_LISTSTART(self, prefix, params):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(
            colored(
                ">>> irc_RPL_LISTSTART {} - {}".format(prefix, params), "white"
            )
        )

    def irc_RPL_LIST(self, prefix, params):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(
            colored(">>> irc_RPL_LIST {} - {}".format(prefix, params), "grey")
        )
        server_tag = prefix.split(".")[-2]
        channel = params[1]

        if server_tag not in self._list_callback:
            return

        n = self._list_callback[server_tag][1]
        n.append(channel)

    def irc_RPL_LISTEND(self, prefix, params):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(
            colored(
                ">>> irc_RPL_LISTEND {} - {}".format(prefix, params), "white"
            )
        )
        server_tag = prefix.split(".")[-2]

        if server_tag not in self._list_callback:
            return

        callbacks, server_channels_list = self._list_callback[server_tag]
        for cb in callbacks:
            defer.maybeDeferred(cb.callback, server_channels_list)

        del self._list_callback[server_tag]

    def irc_RPL_NAMESSTART(self, prefix, params):
        """ """

        print(
            colored(
                ">>> irc_RPL_NAMESSTART {} - {}".format(prefix, params), "white"
            )
        )

    def irc_RPL_NAMREPLY(self, prefix, params):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(
            colored(
                ">>> irc_RPL_NAMREPLY {} - {}".format(prefix, params), "grey"
            )
        )
        server_tag = prefix.split(".")[-2]
        channel = params[2]
        nick_list = params[3].split(" ")

        if server_tag not in self._names_callback:
            return

        n = self._names_callback[server_tag][1]
        n += nick_list

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(
            colored(
                ">>> irc_RPL_ENDOFNAMES {} - {}".format(prefix, params), "white"
            )
        )
        server_tag = prefix.split(".")[-2]
        channel = params[1]

        if server_tag not in self._names_callback:
            print(
                colored(
                    "Error: {} not in _names_callback".format(server_tag),
                    "white",
                    "on_red",
                )
            )
            return

        callbacks, server_names_list = self._names_callback[server_tag]
        for cb in callbacks:
            defer.maybeDeferred(cb.callback, set(server_names_list))

        del self._names_callback[server_tag]


class IRCFactory(protocol.ReconnectingClientFactory):
    """
    Description:    A factory for LogBots.
    ------------    A new protocol instance will be created each time we connect to the server.

    Attributes:
    ----------

    Methods:
    --------
    """

    def __init__(self, logger, description):
        """ """
        self.description = description
        self.logger = logger

    def buildProtocol(self, addr):
        """ """
        p = ListBotIRCProtocol(self.logger, self.description)
        p.factory = self
        return p


class SendIRC(Config):
    """
    Description:
    ------------

    Attributes:
    ----------

    Methods:
    --------
    """

    def __init__(
        self,
        encrypted_config=True,
        config_file_path="auth.json",
        key_file_path=None,
    ):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        super().__init__(encrypted_config, config_file_path, key_file_path)
        self.load_config(config_file_path)
        self.irc = self.data["irc"]

    def cleanup(self):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        if reactor.running:
            reactor.stop()

    def connect(self, description):
        """
        Description:
        ------------

        Parameters:
        -----------

        """
        endpoint = endpoints.clientFromString(
            reactor,
            "tcp:{}:{}".format(description["network"]["server"], 6667),
        )
        factory = IRCFactory(self.logger, description)
        d = endpoint.connect(factory)
        d.addCallback(lambda protocol: protocol.deferred)
        return d

    def send(self, message):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        log.startLogging(sys.stdout)

        if message:
            messages = message.split(". ")
        else:
            messages = self.irc["messages"][0]

        print(messages)

        irc_networks = [net for net in self.irc["networks"] if net["active"]]
        reactor.suggestThreadPoolSize(len(irc_networks))
        reactor.addSystemEventTrigger('before', 'shutdown', self.cleanup)

        for network in irc_networks:
            print(network)
            # create factory protocol and application
            description = {"network": network, "messages": messages}
            reactor.callInThread(self.connect, description)

        reactor.run()
