from channels import Channel
from channels.tests import ChannelTestCase

from myapp.consumers import MyConsumer

class MyTests(ChannelTestCase):

    def test_a_thing(self):
        # Inject a message onto the channel to use in a consumer
        Channel("input").send({"value": 33})
        # Run the consumer with the new Message object
        message = self.get_next_message("input", require=True)
        MyConsumer(message)
        # Verify there's a reply and that it's accurate
        result = self.get_next_message(message.reply_channel.name, require=True)
        self.assertEqual(result['value'], 1089)
