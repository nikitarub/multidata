import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from scipy.signal import argrelmin, argrelmax


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

def concat_signals_lables(data, lables_data, bias=400):
    result = []
    lables_res = []
    for i, batch in enumerate(data):
        try:
            first_zero_index = list(batch).index(0)
        except:
            first_zero_index = -1
        for r in batch[:first_zero_index]:
            lables_res.append((lables_data[i] * 50) + bias)
            result.append(r)
    return result, lables_res

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

def create_binary_dataset():
    pass

def create_regression_dataset():
    pass 
