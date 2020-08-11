class PortManager:
    def __init__(self, min_port, max_port):
        self.port_resource = list(range(min_port, max_port))

    def get(self):
        return self.port_resource.pop(0)

    def put(self, port):
        self.port_resource.append(port)

