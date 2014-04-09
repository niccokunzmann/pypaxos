
class Message:
    def __init__(self, medium, source, destination, content, on_failure = None):
        self.medium = medium
        self.source = source
        self.content = content
        self.destination = destination
        self.on_failure = on_failure

    def reply(self, content):
        reply = Message(self.medium, self.destination, self.source, content)
        self.medium._send_message(reply)

    def delivery_failed(self):
        if self.on_failure:
            self.on_failure(self)

    def __repr__(self):
        return "<{} from: {} to: {} with: {}>".format(self.__class__.__name__,
                                                      self.source,
                                                      self.destination,
                                                      self.content)

