#!/usr/bin/env python
import sys
from functools import reduce
from operator import add
import yaml
import cv2
import tensorflow as tf
import numpy as np
from tqdm import tqdm


def random_choice(count, size):
    return np.random.choice(count, size, replace=False)


def random_selection(size, *arrays):
    indices = random_choice(len(arrays[0]), size)
    result = tuple(np.take(array, indices, axis=0) for array in arrays)
    return result[0] if len(result) == 1 else result


class Scale:
    def __init__(self, features, max_scale=10.0):
        self.average = np.average(features, axis=0)
        self.deviation = np.maximum(np.std(features, axis=0), 1.0 / max_scale)

    def __call__(self, values):
        return np.subtract(values, self.average) / self.deviation


iterations = 100000
p = 10
w, h = 320 // p, 240 // p
s = 1
n = 1951 // s
n_train = n * 6 // 10
n_validation = n * 2 // 10
b = 20
n_div = 5
n_out = n_div * 2 + 1
regularize = 0.016 # validation: 0.991732
regularize = 0.032 # validation: 0.9249
regularize = 0.064 # validation: 0.891654
regularize = 0.128 # validation: 0.85049
alpha = 0.05
data = np.zeros((n, h, w))
label = np.zeros((n, n_out))
for i in range(n):
    data[i] = cv2.imread("data/image%04d.jpg" % (i * s), cv2.IMREAD_GRAYSCALE)[::p, ::p]
    left_drive, right_drive = yaml.load(open("data/image%04d.yml" % (i * s)))
    label[i, round(left_drive / 100.0 * n_div + n_div)] = 1
#data = data.reshape((n, w * h))
data, label = random_selection(n, data, label)
training = data[:n_train], label[:n_train]
validation = data[n_train:n_train+n_validation], label[n_train:n_train+n_validation]
testing = data[n_train+n_validation:], label[n_train+n_validation:]
scale = Scale(training[0], 1000.0)
n_hidden = 4
x = tf.placeholder(tf.float32, [None, h, w], name='x')
y = tf.placeholder(tf.float32, [None, n_out])
avg = tf.constant(scale.average.astype(np.float32))
dev = tf.constant(scale.deviation.astype(np.float32))
xs = tf.reshape((x - avg) / dev, [-1, h * w])
m1 = tf.Variable(tf.truncated_normal([h * w, n_hidden], stddev=1.0/(h * w)))
b1 = tf.Variable(tf.truncated_normal([n_hidden]))
m2 = tf.Variable(tf.truncated_normal([n_hidden, n_out], stddev=1.0/n_hidden))
b2 = tf.Variable(tf.truncated_normal([n_out]))
theta = [m1, b1, m2, b2]
reg_candidates = [m1, m2]

# nearest neighbour?

a0 = tf.sigmoid(xs)
z1 = tf.add(tf.matmul(a0, m1), b1)
a1 = tf.sigmoid(z1)
z2 = tf.add(tf.matmul(a1, m2), b2)
a2 = tf.sigmoid(z2)
h = a2
prediction = tf.argmax(h, axis=-1)
#prediction = (tf.cast(tf.argmax(h, axis=-1), tf.float32) - n_div) * 100 / n_div

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
    c = c * 0.99 + 0.01 * session.run(cost, feed_dict=batch)
    progress.set_description('cost: %8.6f' % c)
    session.run(step, feed_dict=batch)

print('training:', session.run(cost, feed_dict=train))
print('validation:', session.run(cost, feed_dict=validate))
print('error:', np.average(np.abs(session.run(prediction, feed_dict=validate) - session.run(tf.argmax(y, axis=-1), feed_dict = validate))))
print('test:', np.average(np.abs(session.run(prediction, feed_dict=test) - session.run(tf.argmax(y, axis=-1), feed_dict = test))))
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
