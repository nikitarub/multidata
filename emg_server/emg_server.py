import asyncio
import websockets
import time
from get_serial import read_for_sec_to_array

async def send_emg():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            signal = read_for_sec_to_array(0.1)
            sa = str(signal).replace('[', '').replace(']', '').replace(' ', '') 
            # print(len(sa))
            await websocket.send("de" + sa)

        # for i in range(50):
        #     time.sleep(0.1)
        #     a = [i for i in range(100, 110)]
        #     sa = str(a).replace('[', '').replace(']', '').replace(' ', '') 
        #     dtype = "e"
        #     # if i % 5 == 0:
        #     #     dtype = "k"
        #     await websocket.send("d" + dtype + sa)
        # await websocket.recv()



asyncio.get_event_loop().run_until_complete(send_emg())


async def hello_2():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        for i in range(1):
            time.sleep(0.1)
            a = [i for i in range(100, 120)]
            sa = str(a).replace('[', '').replace(']', '').replace(' ', '') 
            dtype = "k"
            # if i % 5 == 0:
            #     dtype = "k"
            await websocket.send("d" + dtype + sa)
        # await websocket.recv()

# asyncio.get_event_loop().run_until_complete(hello_2())

# def on_open(ws):
#     def run(*args):
#         for i in range(3):
#             time.sleep(1)
#             a = [1,2,3]
#             sa = str(a)
#             ws.send("de" + sa.replace('[', '').replace(']', ''))
#         time.sleep(1)
#         ws.close()
#         print("thread terminating...")
#     thread.start_new_thread(run, ())


# if __name__ == "__main__":
#     websocket.enableTrace(True)
#     ws = websockets.WebSocketApp("ws://localhost:8765/",
#                               on_message = on_message,
#                               on_error = on_error,
#                               on_close = on_close)
#     ws.on_open = on_open
#     ws.run_forever()