import pandas as pd
import numpy as np
import itertools

def grouper(iterable, n, fillvalue=None):
        # from itertools
        # "Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
        args = [iter(iterable)] * n
        return itertools.zip_longest(*args, fillvalue=fillvalue)

class DataProcessing:
    def __init__(self, emg_signal_length): 
        self.keypoints = []
        self.emg_signal = []
        self.anotations = [
            'palmBase',
            'thumb1',
            'thumb2',
            'thumb3',
            'thumb4',
            'indexFinger1',
            'indexFinger2',
            'indexFinger3',
            'indexFinger4',
            'middleFinger1',
            'middleFinger2',
            'middleFinger3',
            'middleFinger4',
            'ringFinger1',
            'ringFinger2',
            'ringFinger3',
            'ringFinger4',
            'pinky1',
            'pinky2',
            'pinky3',
            'pinky4']
        self.emg_signal_length = emg_signal_length
        # self.emg_signal_anotations = ["e" + str(i) for i in range(emg_signal_length)]
        #  pd.DataFrame(columns=[self.anotations + self.emg_signal_anotations])
        self.batches = []
    
    def process(self, dtype, data):
        if dtype == "k":
            self.keypoints = list(grouper(data, 3))
        elif dtype == "e":
            # self.emg_signal.append(list(np.array(data).flatten()))
            self.emg_signal = self.emg_signal + list(np.array(data).flatten())
            # print("In process: ", list(np.array(data).flatten()))
            # print("EMG: ", list(np.array(self.emg_signal).flatten()))

    def cleanup(self):
        self.keypoints = []
        self.emg_signal = []

    def make_batch(self,):
        # print("Len in make_batch: ", len(self.keypoints[0]), len(self.emg_signal))
        if len(self.keypoints) == 0 or len(self.emg_signal) == 0:
            return
        flat_emg = list(np.array(self.emg_signal).flatten())[-self.emg_signal_length:]
        for _ in range(self.emg_signal_length - len(flat_emg)):
            flat_emg.append(0)
        
        self.batches.append(
            list(np.array(self.keypoints).flatten()) +
            list(np.array(flat_emg).flatten())
            )
        # 
        self.keypoints = []
        self.emg_signal = []

    def write_to_file(self, dataset_name):
        emg_signal_anotations = ["e" + str(i) for i in range(self.emg_signal_length)]
        full_keypoints_anotations = list(np.array([[anot + "_x", anot + "_y", anot + "_z"] for anot in self.anotations]).flatten())
        to_df = self.batches
        print("len to_df: ", len(to_df), len(to_df[0]))
        print("len anot_: ", len(full_keypoints_anotations + emg_signal_anotations))
        df = pd.DataFrame(to_df ,columns=full_keypoints_anotations + emg_signal_anotations)
        df.to_csv("./tmp_data/" + dataset_name + ".csv")
        print("Dataset saved: ", "./tmp_data/" + dataset_name + ".csv")
