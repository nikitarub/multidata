#!/usr/bin/env python
import os
import time
from multiprocessing import Process, Queue, Lock

from data_processing import DataProcessing

import asyncio
import websockets

s = time.time()

can_collect = False

collect_threashold = 2
collect_time_to_wait = 2 # seconds
collect_count = 0
collect_last_time = time.time()
make_batch_countdown = 0

def start_collect():
    print("Starting collector")
    global can_collect
    can_collect = True
    print("can_collect: ", can_collect)

def end_collect():
    print("Ending collector")
    global can_collect
    can_collect = False

def save_collected(dp):
    # dp.write
    dp.write_to_file()
    print("Saving data")

def fit():
    # send ws to fit
    print("Fitting")

def start_predict():
    print("Starting predicting")

def end_predict():
    print("Ending predicting")

def save_model():
    print("Saving model")

def got_data(data, dp):
    global collect_count
    global collect_last_time
    global make_batch_countdown
    if not can_collect:
        return
    if collect_count < collect_threashold:
        collect_count += 1
        dp.cleanup()
        return
    if (time.time() - collect_last_time) > collect_time_to_wait:
        dp.cleanup()
        collect_last_time = time.time()
        return
    
    data_type = data[1]
    data_points = [float(d) for d in data[2:].split(",")]
    dp.process(data_type, data_points)
    if data_type == "k":
        if make_batch_countdown == 3:
            dp.make_batch()
            make_batch_countdown = 0
        else: 
            make_batch_countdown += 1
        print("Batch: ", len(dp.batches))
    # добавить первый (старт) и последний (стоп) фреймы

    # make_batch
    # сначала создается batch
    # в файл пишется по нажатию кнопки окнчить сбор
    # сбор ЭМГ происходит между 1,2-ым и последним "кадром" руки
    # если n времени не было кадров сбор ЭМГ останавливается и чистится аккумулятор ЭМГ


    # по приходу типа keypoint – запись всего в файл: эта логика тут
    collect_last_time = time.time()
    collect_count += 1
    print("Got data: ", time.time() - s, len(data_points)) #, keypoints

dp = DataProcessing(100)


async def send_data(data, connected):
    try:
        # Implement logic here.
        print("Sending: ", data)
        await asyncio.wait([ws.send(data) for ws in connected])
        print("Sent")
    finally:
        pass

connected = set()

async def listener(websocket, path):
    print("Starting to listen websocket")
    # ws_web = websocket
    connected.add(websocket)
    async for message in websocket:
        if "ping_test" in message:
            print("ping: ")
            await send_data("Hello!", connected)
        if message == "start_collect":
            start_collect()
        elif message == "end_collect":
            end_collect()
        elif message == "fit":
            fit()
        elif message == "start_predict":
            start_predict()
        elif message == "end_predict":
            end_predict()
        elif message == "save_model":
            save_model()
        elif "save_collected" in message:
            save_collected(dp)
        elif message[0] == "d":
            got_data(message, dp)
        elif message == "fitted":
            print("Done fitting")
        else:
            print("Unknown message: ", message)
            # flag = False

asyncio.get_event_loop().run_until_complete(
    websockets.serve(listener, 'localhost', 8765))
asyncio.get_event_loop().run_forever()

