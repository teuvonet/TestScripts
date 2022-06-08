import paho.mqtt.client as client
from time import sleep
import json
import sys
import random
import os

the_control_flag = 0

server_address = "127.0.0.1"
mqtt_client = client.Client("ECG")
data_directory = '/home/asim/ssriva59/setup-stuff/gateway_and_dataset'


def prepare_data(data_dir, dataset, seed):
    # train_data_file = open('ECG-Train.csv')
    train_data_file = open(os.path.join(data_dir, dataset, "Train", dataset + '_Train_seed' + str(seed) + '_modified.csv'))
    # train_data_file = open(
    #     os.path.join(data_dir, '%s_train_overall_modified.csv' % dataset))
    train_data = []

    for each_line in train_data_file:
        each_line = each_line.strip().split(',')[1:]

        # Only XOR
        # each_line = each_line.strip().split(',')
        train_data.append(each_line)

    # test_data_file = open('ECG-Test.csv')
    test_data_file = open(os.path.join(data_dir, dataset, "Test", dataset + '_Test_seed' + str(seed) + '_modified.csv'))
    # test_data_file = open(
    #     os.path.join(data_dir, '%s_test_modified.csv' % dataset))
    test_data = []

    for each_line in test_data_file:
        each_line = each_line.strip().split(',')[1:]

        # Only for XOR
        # each_line = each_line.strip().split(',')
        test_data.append(each_line)

    list_of_feature_names = []
    for i in range(len(train_data[0])):
        list_of_feature_names.append(train_data[0][i])
    print(list_of_feature_names)
    train_data.pop(0)
    test_data.pop(0)
    return train_data, test_data, list_of_feature_names


def shuffle_the_rows(rows):
    random.shuffle(rows)


def connect_to_client():
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(server_address)
    mqtt_client.on_disconnect = on_disconnect


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("ECG connected")
        sys.stdout.flush()


def disconnect_from_client():
    mqtt_client.disconnect()
    sys.exit(0)


def on_disconnect(client, userdata, rc):
    print("ECG disconnected")
    sys.stdout.flush()
    client.connected_flag = False
    client.disconnect_flag = True


def publish(data_to_send):
    try:
        json_data = json.dumps(data_to_send)
        # print "json_data", json_data
        mqtt_client.publish("from/sensor/ECG", json_data)

    except KeyboardInterrupt:
        mqtt_client.disconnect()
        sys.exit(0)


def send_data():
    if the_control_flag == 1:
        random.shuffle(train_data)
        for i in range(0, 50):
            data_to_send = [list_of_feature_names, train_data[i]]
            publish(data_to_send)
            # print("train packet sent")

    elif the_control_flag == 2:
        random.shuffle(test_data)
        for i in range(0, 50):
            data_to_send = [list_of_feature_names, test_data[i]]
            publish(data_to_send)
            # print("test packet sent")


def on_message(client, userdata, message):
    global the_control_flag
    print("received message: ", message.payload.decode("utf-8"))
    msg = str(message.payload.decode("utf-8"))
    if msg == "send_train_data":
        the_control_flag = 1

    elif msg == "send_test_data":
        the_control_flag = 2

    if the_control_flag == 1 or the_control_flag == 2:
        send_data()
    else:
        print("not sending data yet")


connect_to_client()
mqtt_client.on_message = on_message
mqtt_client.subscribe("from/gateway/control")

chunk_size = 50
seed = sys.argv[2]
dataset = sys.argv[1]
train_data, test_data, list_of_feature_names = prepare_data(data_directory, dataset, seed)

try:
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    print("ending ECG_streaming....")
    disconnect_from_client()
