from channels.routing import route
from . import  consumers

channel_routing = [
    consumers.ConsumerSolo.as_route(path=r"^/playsolo/"),
    consumers.ConsumerMultiLobby.as_route(path=r"^/playmulti/lobby/"),
]
