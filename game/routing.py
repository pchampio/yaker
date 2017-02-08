from channels.routing import route
from . import  consumers

channel_routing = [
    consumers.MyConsumer.as_route(path=r"^/playsolo/"),
]
