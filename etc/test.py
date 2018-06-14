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
from data import random_selection, count_files, Scale, Offset, Reshape, Sigmoid, Weights, Bias


if __name__ == '__main__':
    iterations = 100000
    p = 10
    w, h = 320 // p, 240 // p
    n = count_files("images/image%04d.jpg")
    n_train = n * 6 // 10
    n_validation = n * 2 // 10
    b = 20
    n_div = 5
    n_out = n_div * 2 + 1
    regularize = 0.032 # validation error: 2.055
    regularize = 0.016 # validation error: 1.951
    regularize = 0.008 # validation error: 2.375
    alpha = 0.05
    n_hidden = 10
    data = np.zeros((n, h, w))
    label = np.zeros((n, n_out))
    for i in range(n):
        data[i] = cv2.imread("images/image%04d.jpg" % i, cv2.IMREAD_GRAYSCALE)[::p, ::p]
        left_drive, right_drive = yaml.load(open("images/image%04d.yml" % i))
        label[i, round(left_drive / 100.0 * n_div + n_div)] = 1
    data, label = random_selection(n, data, label)
    training = data[:n_train], label[:n_train]
    validation = data[n_train:n_train+n_validation], label[n_train:n_train+n_validation]
    testing = data[n_train+n_validation:], label[n_train+n_validation:]
    y = tf.placeholder(tf.float32, [None, n_out])

    a0 = Sigmoid(Reshape([-1, h * w], Scale(64, Offset(128))))
    m1 = Weights(np.random.normal(np.full((h * w, n_hidden), 1.0 / (h * w))), a0)
    z1 = Bias(np.random.normal(np.full(n_hidden, 1.0)), m1)
    a1 = Sigmoid(z1)
    m2 = Weights(np.random.normal(np.full((n_hidden, n_out), 1.0 / n_hidden)), a1)
    z2 = Bias(np.random.normal(np.full(n_out, 1.0)), m2)
    a2 = Sigmoid(z2)
    x = a2.x
    h = a2.operation
    prediction = tf.argmax(h, axis=-1)
    #prediction = (tf.cast(tf.argmax(h, axis=-1), tf.float32) - n_div) * 100 / n_div

    theta = [m1.weights, z1.bias, m2.weights, z2.bias]
    reg_candidates = [m1.weights, m2.weights]

    m = tf.cast(tf.size(y) / n_out, tf.float32)
    reg_term = reduce(add, [tf.reduce_sum(tf.square(parameter)) for parameter in reg_candidates]) / (m * 2)
    safe_log = lambda v: tf.log(tf.clip_by_value(v, 1e-10, 1.0))
    error_term = -tf.reduce_sum(y * safe_log(h) + (1 - y) * safe_log(1 - h)) / m
    if regularize > 0:
        cost = error_term + regularize * reg_term
    else:
        cost = error_term
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
        selection = random_selection(b, train[x], train[y])
        batch = {x: selection[0], y: selection[1]}
        c = c * 0.999 + 0.001 * session.run(cost, feed_dict=batch)
        progress.set_description('cost: %8.6f' % c)
        session.run(step, feed_dict=batch)

    print('training error:', np.sqrt(np.average((session.run(prediction, feed_dict=train) - session.run(tf.argmax(y, axis=-1), feed_dict = train)) ** 2)))
    print('validation error:', np.sqrt(np.average((session.run(prediction, feed_dict=validate) - session.run(tf.argmax(y, axis=-1), feed_dict = validate)) ** 2)))
    print('test error:', np.sqrt(np.average((session.run(prediction, feed_dict=test) - session.run(tf.argmax(y, axis=-1), feed_dict = test)) ** 2)))
    tf.add_to_collection('prediction', prediction)
    saver.save(session, './model')


#import cv2
#from camera import Camera
#session = tf.InteractiveSession()
#saver = tf.train.import_meta_graph('model.meta')
#saver.restore(session, 'model')
#prediction = tf.get_collection('prediction')[0]
#camera = Camera()
#session.run(prediction, feed_dict={'x:0': cv2.cvtColor(camera.capture(), cv2.COLOR_BGR2GRAY)[::10, ::10].reshape(1, 24, 32)})
