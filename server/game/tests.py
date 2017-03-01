#  from channels.tests import ChannelTestCase, HttpClient, apply_routes
#  from .consumers import MyConsumer

#  class MyTests(ChannelTestCase):

    #  def test_my_consumer(self):
        #  client = HttpClient()

        #  with apply_routes([MyConsumer.as_route(path=r"^/playsolo/"),]):
            #  client.send_and_consume('websocket.connect', '/playsolo/')
            #  self.assertEqual(client.receive(), {'key': 'value'})
