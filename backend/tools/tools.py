from scipy.signal import argrelmin, argrelmax

def local_max_min(data, threshold=30):
    # нахождение 
    res_min = np.array(data)
    res_max = np.array(data)
    cnt = len(res_min)
    indexes = [i for i in range(len(data))]
    indexes_max = np.array(indexes)
    indexes_min = np.array(indexes)
    def f(res_min, res_max, indexes_min, indexes_max):
        while len(indexes_min) > threshold:
            minInd = argrelmin(res_min)
            res_min = res_min[minInd]
            indexes_min = indexes_min[minInd]
        while len(indexes_max) > threshold:
            maxInd = argrelmax(res_max)
            res_max = res_max[maxInd]
            indexes_max = indexes_max[maxInd]
        return res_min, res_max, indexes_min, indexes_max
    res_min, res_max, indexes_min, indexes_max = f(res_min, res_max, indexes_min, indexes_max)
    return res_min, res_max, indexes_min, indexes_max


# works with local_max_min data
def local_avg(data_max, data_min):
    res = []
    length = min(len(list(data_max)), len(list(data_min)))
    for i in range(length):
        t = (data_max[i] + data_min[i])/2
        res.append(t)
    return res