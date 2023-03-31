import treq
import txtorcon


from twisted.internet import (
    defer,
    endpoints,
    protocol,
    reactor,
    ssl,
    task,
    threads,
)
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import deferLater, react
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.python import log

async def tor_run(reactor):
    """
    Description:
    ------------

    Parameters:
    -----------

    """
    
    tor = await txtorcon.connect(
        reactor, UNIXClientEndpoint(reactor, "/var/run/tor/control")
    )

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
