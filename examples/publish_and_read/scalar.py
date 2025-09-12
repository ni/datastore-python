from ni.datastore.client import Client
from ni.datastore.types import Measurement, PassFailStatus, Moniker

if __name__ == "__main__":
    client = Client()
    client.publish_bool()
