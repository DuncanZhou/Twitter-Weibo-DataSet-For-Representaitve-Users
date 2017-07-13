#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

# 使用Affinity Propagation方法
import numpy as np
import Distance as dist
import DataPrepare as datapre

# 设置迭代次数
Max_iteration = 5

# 数据初始化为矩阵形式
def Pre(features):
    '''

    :param features: features为全局特征向量集
    :return: 返回相似性矩阵
    '''
    # 开始构造S矩阵
    S = []
    distances = []
    for rowid in features.keys():
        row = []
        for colid in features.keys():
            if rowid == colid:
                # 每个点都可能成为exemplar,取其他所有数的中位数
                row.append(0)
            else:
                temp = -dist.distance(features[rowid],features[colid])
                distances.append(temp)
                row.append(temp)
        S.append(row)
    S = np.array(S)
    distances.sort()
    # 得到中位数
    median = (distances[len(distances) / 2] + distances[len(distances) / 2 - 1]) / 2
    print median
    for rowid in range(len(features.keys())):
        for colid in range(len(features.keys())):
            # 对角线元素等于其余元素中位数
            if rowid == colid:
                S[rowid,colid] = median
    return S

# 删除某一元素
def delete(lt,index):
    lt = lt[:index] + lt[index + 1:]
    return lt

def isNonNegative(x):
    return x >= 0

# 开始迭代,计算矩阵R和A以及代表性向量E
def AP(S,features,lamda):
    userid = {}
    # 建立一个字典,对应{i,userid}
    for i,key in zip(range(len(features.keys())),features.keys()):
        userid[i] = key
    # 初始化A矩阵,初始为0
    row_n = S.shape[0]
    A = np.zeros_like(S,dtype=np.int)
    R = np.zeros_like(S,dtype=np.int)
    # 初始化代表性向量
    E = set()
    for key in features.keys():
        E.add(key)
    iteration = 0
    # 开始迭代计算
    while iteration < Max_iteration:
        #　更新R矩阵
        for i in range(row_n):
            # 计算a[i,j] + s[i,j] 之和
            kSum = [s + a for s,a in zip(S[i],A[i])]
            # print i
            for j in range(row_n):
                kfit = delete(kSum,j)
                new_responsibility = S[i,j] - max(kfit)
                R[i,j] = lamda * R[i,j] + (1 - lamda) * new_responsibility
        print "R矩阵更新完成"

        # 更新A矩阵
        for rowIndex in range(row_n):
            for colIndex in range(row_n):
                # 对角线情况
                if colIndex == rowIndex:
                    asum = 0
                    for j in range(row_n):
                        if j != colIndex:
                            # 只加入非负的数
                            asum += max(0,R[j,colIndex])
                    new_availbility = asum
                else:
                    asum = 0
                    for j in range(row_n):
                        if j != rowIndex and j != colIndex:
                            asum += max(0,R[j,colIndex])
                    result = asum + R[colIndex,colIndex]
                    new_availbility = min(result,0)
                A[rowIndex,colIndex] = lamda * A[rowIndex,colIndex] + (1 - lamda) * new_availbility

        print "A矩阵更新完成"
        # 计算A[i,j] + R[i,j]
        Result = A + R
        seeds = set()
        for i in range(row_n):
            # 计算A[i,j] + R[i,j]的最大值的j
            fit = list(Result[i])
            key = fit.index(max(fit))
            seeds.add(userid[key])

        # 如果新的和老的代表性向量一样,可以终止迭代
        if seeds == E:
            break
            # 停止迭代
        else:
            E = seeds
        iteration += 1
        print "迭代%d次" % iteration
        print "代表向量个数%d" % len(seeds)

    s_current = {}
    for seed in seeds:
        s_current[seed] = features[seed]
    return s_current

def run(features):
    return AP(Pre(features),features,0.5)
