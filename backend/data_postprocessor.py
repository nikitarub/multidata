import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from scipy.signal import argrelmin, argrelmax
import sys


def read_data(filename):
    pass

# working with handpose data
def get_anotations(number):
    anotations_short = {
            -1: "palmBase",
            0: "thumb",
            1: "indexFinger",
            2: "middleFinger",
            3: "ringFinger",
            4: "pinky"
        }
    return anotations_short[number]

def get_hand_data(ds):
    palmBase_x = ds.palmBase_x.tolist()
    palmBase_y = ds.palmBase_y.tolist()
    thumb_x = ds.thumb4_x.tolist()
    thumb_y = ds.thumb4_y.tolist()
    indexFinger_x = ds.indexFinger4_x.tolist()
    indexFinger_y = ds.indexFinger4_y.tolist()
    middleFinger_x = ds.middleFinger4_x.tolist()
    middleFinger_y = ds.middleFinger4_y.tolist()
    ringFinger_x = ds.ringFinger4_x.tolist()
    ringFinger_y = ds.ringFinger4_y.tolist()
    pinky_x = ds.pinky4_x.tolist()
    pinky_y = ds.pinky4_y.tolist()
    return palmBase_x,palmBase_y, thumb_x,thumb_y, indexFinger_x,indexFinger_y, middleFinger_x,middleFinger_y, ringFinger_x,ringFinger_y, pinky_x,pinky_y

def get_dist_base_index(base_x, base_y, indexFinger_x, indexFinger_y):
    base_indexFinger = []
    for i in range(len(base_x)):
        base_indexFinger.append( euclidean([base_x[i], base_y[i]], [indexFinger_x[i], indexFinger_y[i]]) )
    return base_indexFinger

def save_hand_plot(pb_x, pb_y, t_x, t_y, if_x, if_y, mf_x, mf_y, rf_x, rf_y, pf_x, pf_y, filename):
    plt.scatter(pb_x, pb_y, c="r")
    plt.scatter(t_x, t_y, c="g")
    plt.scatter(if_x, if_y, c="blue")
    plt.scatter(mf_x, mf_y, c="black")
    plt.scatter(rf_x, rf_y, c="y")
    plt.scatter(pf_x, pf_y, c="pink")
    plt.title("Точки пальцев руки во времени")
    plt.savefig(filename)


# working with signals
def collect_signals(data_frame, amount=100,  prefix="e"):
    result = data_frame.loc[:,'e0':'e'+str(amount-1)]
    return result.to_numpy()

def concat_signals(data):
    result = []
    for i, batch in enumerate(data):
        try:
            first_zero_index = list(batch).index(0)
        except:
            first_zero_index = -1
        for r in batch[:first_zero_index]:
            result.append(r)
    return result

def concat_signals_lables(data, lables_data, bias=0):
    result = []
    lables_res = []
    lables_base = []
    for i, batch in enumerate(data):
        try:
            first_zero_index = list(batch).index(0)
        except:
            first_zero_index = -1
        for r in batch[:first_zero_index]:
            lables_res.append((lables_data[i] * 50) + bias)
            lables_base.append(lables_data[i])
            result.append(r)
    return result, lables_res, lables_base

def concat_signals_lables_ground(data, lables_data):
    result = []
    lables_res = []
    for i, batch in enumerate(data):
        try:
            first_zero_index = list(batch).index(0)
        except:
            first_zero_index = -1
        for r in batch[:first_zero_index]:
            lables_res.append(lables_data[i])
            result.append(r)
    return result, lables_res

def is_bend(data_bend, threshold=200, bias=25):
    result = []
    for d in data_bend:
#         result.append(d > threshold)
        if d > (threshold + bias):
            result.append(1)
        elif d < (threshold - bias):
            result.append(-1)
        else:
            result.append(0)
    return result

def get_bend_not_bend_index_lables(lables_data, bias=0): # works with not ground lables
    current = lables_data[0]
    start = 0
    left_bias = 0
    right_bias = bias
    bend_index = []
    not_bend_index = []
    for i,each in enumerate(lables_data[1:]):
        if each != current:
            if (len(lables_data[1:]) - i) < bias:
                right_bias = 0
            if each > current:
                not_bend_index.append((start - left_bias, i + right_bias))
            else:
                bend_index.append((start - left_bias, i + right_bias))
            start = i
            left_bias = bias
        current = each
    return bend_index, not_bend_index

def get_bend_indexes_lables(lables_data, bias=0): # for ground dist
    current = lables_data[0]
    start = 0
    left_bias = 0
    right_bias = bias
    bend_indexes = []
    for i,each in enumerate(lables_data[1:]):
        if each != current:
            if (len(lables_data[1:]) - i) < bias:
                right_bias = 0
            bend_indexes.append((start - left_bias, i + right_bias, current))
            start = i
            left_bias = bias
        current = each
    return bend_indexes

def create_bend_batches(signal_full, bend_index):
    signal_bend_batches = []
    for each in bend_index:
        d = signal_full[each[0] : each[1]]
        signal_bend_batches.append(d)
    return signal_bend_batches


def create_bend_batches_regression(signal_full, bend_index):
    # NOTE: regression ads bend distance at the end of the signal vector
    signal_bend_batches = []
    indexes = []
    for each in bend_index:
        d = signal_full[each[0] : each[1]]
        signal_bend_batches.append(d)
        indexes.append(each[2])
    return signal_bend_batches, indexes

def norm_batches_length(signal_batches, length, na_value=0, pass_lower=True):
    res = []
    for each in signal_batches:
        if pass_lower:
            d = each[:length]
            res.append(d + [na_value] * (length - len(d)))
        else:
            if len(each) >= length:
                d = each[:length]
                res.append(d)
    return res

def create_binary_dataset(signal_full, bend_index, not_bend_index, batch_len, bend_label=1, not_bend_label=0, pass_lower=True):
    # pandas dataset creation 
    signal_bend_batches = create_bend_batches(signal_full, bend_index)
    signal_not_bend_batches = create_bend_batches(signal_full, not_bend_index)
    signal_bend_batches = norm_batches_length(signal_bend_batches, batch_len, pass_lower=pass_lower)
    signal_not_bend_batches = norm_batches_length(signal_not_bend_batches, batch_len, pass_lower=pass_lower)
    to_df = []
    for batch in signal_bend_batches:
        to_df.append(batch + [bend_label])
    for batch in signal_not_bend_batches:
        to_df.append(batch + [not_bend_label])
    column_names = ["e_"+str(i) for i in range(batch_len)]
    column_names.append("label")    
    df = pd.DataFrame(to_df ,columns=column_names)
    return df

def create_ternary_dataset(signal_full, bend_indexes, batch_len, pass_lower=True):
    signal_bend_batches, lables = create_bend_batches_regression(signal_full, bend_indexes)
    # lables = [i[-1] for i in signal_bend_batches]
    for s in signal_bend_batches:
        if -1 in s[:-1]:
            print("-1 in sign:", s[:-1])
    signal_bend_batches = norm_batches_length(signal_bend_batches[:-1], batch_len, pass_lower=pass_lower)
    to_df = []
    for i, batch in enumerate(signal_bend_batches):
        if -1 in batch:
            print("-1 in :", batch)
        to_df.append(batch + [lables[i]])
    column_names = ["e_"+str(i) for i in range(batch_len)]
    column_names.append("label")    
    df = pd.DataFrame(to_df ,columns=column_names)
    return df

def create_regression_dataset():
    pass

def create_dataset_image(signal_full, lables_full, filename="", start=0, end=-1):
    plt.plot(signal_full[start:end], c="b")
    plt.plot(lables_full[start:end], c="r")
    plt.savefig(filename)

def save_batches_fig(batches, filename):
    avg = 0
    plt.clf()
    avg_diff = 0
    for each in batches:
        avg += len(each)
        avg_diff += each[-1] - each[0]
        plt.plot(each)
    print("avg_diff: ", avg_diff/len(batches))
    print("AVG: ", avg/len(batches))
    plt.savefig(filename)
    return avg

if __name__ == '__main__':
    # read data,
    # prepare data 
    #   get signals
    #   get bend data
    # create dataset
    # write data
    df = pd.read_csv("tmp_data/dataset_2.csv")
    palmBase_x,palmBase_y, thumb_x,thumb_y, indexFinger_x,indexFinger_y, middleFinger_x,middleFinger_y, ringFinger_x,ringFinger_y, pinky_x,pinky_y = get_hand_data(df)
    dist_base_index = get_dist_base_index(palmBase_x, palmBase_y, ringFinger_x, ringFinger_y)
    signals = collect_signals(df)
    bend_base_index = is_bend(dist_base_index)
    signal_full, lables_full = concat_signals_lables_ground(signals, dist_base_index)
    _, lables_bend_full, lables_bend_base_full = concat_signals_lables(signals, bend_base_index)
    create_dataset_image(signal_full, lables_bend_full, "../datasets/binary_regression/ds_backup_5/pics/dataset_graph", 0, 50000)
    bend_index, not_bend_index = get_bend_not_bend_index_lables(lables_bend_full, 10)

    bend_indexes = get_bend_indexes_lables(lables_bend_base_full, 10)
    
    signal_bend_batches = create_bend_batches(signal_full, bend_index)
    save_batches_fig(signal_bend_batches, "../datasets/binary_regression/ds_backup_5/pics/batches_bend.png")
    signal_not_bend_batches = create_bend_batches(signal_full, not_bend_index)
    save_batches_fig(signal_not_bend_batches, "../datasets/binary_regression/ds_backup_5/pics/batches_not_bend.png")

    
    res_df = create_ternary_dataset(signal_full[:50000], bend_indexes[:50000], 200)
    # print(res_df.describe())
    res_df.to_csv("../datasets/binary_regression/ds_backup_5/dataset.csv")