#!/usr/bin/env python
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import pytest
from functools import reduce
from operator import add
import yaml
import cv2
import tensorflow as tf
import numpy as np
from tqdm import tqdm
from data import random_selection, count_files, FeatureScale, Reshape, ReLU, Sigmoid, Weights, Bias
from IPython import embed


if __name__ == '__main__':
    iterations = 10000
    p = 10
    w, h = 320 // p, 240 // p
    n = count_files("images/image%04d.jpg")
    n_train = n * 6 // 10
    n_validation = n * 2 // 10
    batch_size = 20
    n_div = 5
    n_out = n_div * 2 + 1
    regularize = 0.256
    sigma = 1
    alpha = 0.1
    n_hidden = 40
    # training error: 21.67, validation error: 26.11
    data = np.zeros((n, h, w))
    label = np.zeros((n, 2, n_out))
    drive = np.zeros((n, 2))
    r = np.float32(np.arange(-n_div, n_div + 1) * 100.0 / n_div)
    for i in range(n):
        data[i] = cv2.imread("images/image%04d.jpg" % i, cv2.IMREAD_GRAYSCALE)[::p, ::p]
        drive[i] = yaml.load(open("images/image%04d.yml" % i))
        label[i, 0] = np.exp(-((drive[i, 0] - r) / 100.0 * n_div / sigma) ** 2)
        label[i, 1] = np.exp(-((drive[i, 1] - r) / 100.0 * n_div / sigma) ** 2)
    np.random.seed(0)
    data, label, drive = random_selection(n, data, label, drive)
    training = data[:n_train], label[:n_train], drive[:n_train]
    validation = data[n_train:n_train+n_validation], label[n_train:n_train+n_validation], drive[n_train:n_train+n_validation]
    testing = data[n_train+n_validation:], label[n_train+n_validation:], drive[n_train+n_validation:]
    y = tf.placeholder(tf.float32, [None, 2, n_out])

    a0 = ReLU(Reshape([-1, h * w], FeatureScale(data)))
    m1 = Weights(np.random.normal(np.full((h * w, n_hidden), 1.0 / (h * w))), a0)
    a1 = ReLU(Bias(np.random.normal(np.full(n_hidden, 1.0)), m1))
    m2 = Weights(np.random.normal(np.full((n_hidden, 2 * n_out), 1.0 / n_hidden)), a1)
    a2 = Reshape([-1, 2, n_out], Sigmoid(Bias(np.random.normal(np.full(2 * n_out, 1.0)), m2)))
    x, h = a2.x, a2.operation
    prediction = tf.reduce_sum(r * h, axis=-1) / tf.reduce_sum(h, axis=-1)

    theta = a2.variables()
    reg_candidates = a2.regularisation_candidates()

    m = tf.cast(tf.size(y) / n_out, tf.float32)
    reg_term = reduce(add, [tf.reduce_sum(tf.square(parameter)) for parameter in reg_candidates]) / (m * 2)
    safe_log = lambda v: tf.log(tf.clip_by_value(v, 1e-10, 1.0))
    error_term = -tf.reduce_sum(y * safe_log(h) + (1 - y) * safe_log(1 - h)) / m
    cost = error_term + regularize * reg_term
    rmsd = tf.reduce_sum(tf.square(h - y)) / (2 * m)
    dtheta = tf.gradients(cost, theta)
    step = [tf.assign(value, tf.subtract(value, tf.multiply(alpha, dvalue))) for value, dvalue in zip(theta, dtheta)]

    train = {x: training[0], y: training[1]}
    validate = {x: validation[0], y: validation[1]}
    test = {x: testing[0], y: testing[1]}

    saver = tf.train.Saver()
    session = tf.InteractiveSession()
    session.run(tf.global_variables_initializer())
    c = 0
    progress = tqdm(range(iterations))
    for i in progress:
        selection = random_selection(batch_size, train[x], train[y])
        batch = {x: selection[0], y: selection[1]}
        c = c * (1 - 100.0 / iterations) + 100.0 / iterations * session.run(cost, feed_dict=batch)
        progress.set_description('cost: %8.6f' % c)
        session.run(step, feed_dict=batch)

    print('training error:', np.sqrt(np.average((session.run(prediction, feed_dict=train) - training[2]) ** 2)))
    print('validation error:', np.sqrt(np.average((session.run(prediction, feed_dict=validate) - validation[2]) ** 2)))
    print('test error:', np.sqrt(np.average((session.run(prediction, feed_dict=test) - testing[2]) ** 2)))
    tf.add_to_collection('prediction', prediction)
    saver.save(session, './model')
    embed()


#import cv2
#import tensorflow as tf
#from camera import Camera
#session = tf.InteractiveSession()
#saver = tf.train.import_meta_graph('model.meta')
#saver.restore(session, 'model')
#prediction = tf.get_collection('prediction')[0]
#camera = Camera()
#session.run(prediction, feed_dict={'x:0': cv2.cvtColor(camera.capture(), cv2.COLOR_BGR2GRAY)[::10, ::10]})
