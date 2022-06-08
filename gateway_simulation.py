import paho.mqtt.client as mqtt
import json
import sys
from time import sleep

server_address = "127.0.0.1"
req_len_datapoints = 50

message_num = 0
gateway_topic_name = "from/gateway"

sum_of_lengths = 0
message_queue = []
latest_elements = dict()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("gateway connected to mqtt server")
        sys.stdout.flush()


def on_disconnect(client, userdata, rc):
    print("gateway disconnected from mqtt server")
    sys.stdout.flush()


def publish_data():
    global message_queue
    global latest_elements
    row_list = []
    count = 0
    for each_message in message_queue:
        latest_elements[each_message[0]] = each_message[1]
        if count == 0:
            row_list.append(list(latest_elements.values())[0][0])
            count = 1
        row_list.append(list(latest_elements.values())[0][1])
    message_queue = []

    json_format_data = json.dumps(row_list)
    mqtt_sub_pub.publish(gateway_topic_name, json_format_data)
    # sleep(0.3)
    sys.stdout.flush()


# can create separate callbacks for each topic using client.message_callback_add("topicname", callback_function_name)
def on_message(client, userdata, message):
    global message_queue
    global latest_elements

    topic = ""
    try:
        topic = str(message.topic.decode("utf-8"))  # type: str
    except:
        topic = str(message.topic)
    # print "received topic: ", topic, " ", len(message_queue)
    if topic == "from/zcu":
        mqtt_sub_pub.publish("from/gateway/control", message.payload)
    else:
        sensor_data = json.loads(message.payload)
        # print "sensor_data:", sensor_data
        if topic not in latest_elements:
            print("adding topic to latest_elements ")
            latest_elements[topic] = -1
        message_queue.append((topic, sensor_data))
        if len(message_queue) == req_len_datapoints:
            # print("printing the size of message queue", len(message_queue) )
            # print("prinitng the message queue", message_queue)
            publish_data()


mqtt_sub_pub = mqtt.Client("gateway")
mqtt_sub_pub.on_message = on_message
print("connecting to broker")
mqtt_sub_pub.connect(server_address)

print("Subscribing to all topics")
mqtt_sub_pub.subscribe("from/sensor/#")
mqtt_sub_pub.subscribe("from/zcu")

try:
    mqtt_sub_pub.loop_forever()
except KeyboardInterrupt:
    mqtt_sub_pub.disconnect()
    sys.exit(0)
