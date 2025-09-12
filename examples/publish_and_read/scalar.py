
from ni.datastore.client import Client

def test_publish_and_read_bool(value: bool):
    client = Client()
    stored_data_value = client.publish_bool(value)
    print(f"Published boolean value {value}, stored data value: {stored_data_value}")
    read_value = client.read_bool(stored_data_value)
    print(f"Read boolean value: {read_value}")
    assert read_value == value, f"Expected {value}, got {read_value}"

if __name__ == "__main__":
    test_publish_and_read_bool(True)
    test_publish_and_read_bool(False)