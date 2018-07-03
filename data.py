import os.path
import cv2
import numpy as np
import tensorflow as tf
from functools import reduce
from operator import add


def random_choice(count, size):
    return np.random.choice(count, size, replace=False)


def random_selection(size, *arrays):
    indices = random_choice(len(arrays[0]), size)
    result = tuple(np.take(array, indices, axis=0) for array in arrays)
    return result[0] if len(result) == 1 else result


def down_sample(value, amount):
    return value[::amount, ::amount]


def to_gray(value):
    return cv2.cvtColor(np.uint8(value), cv2.COLOR_BGR2GRAY)


def multi_class_label(labels, num_classes):
    index = np.arange(len(labels) * num_classes).reshape(len(labels), num_classes)
    return np.where(np.equal(index % num_classes, np.expand_dims(labels, -1)), 1, 0)


def count_files(pattern, multiplier=100000, exist=os.path.exists):
    count = -1
    while multiplier > 0:
        while exist(pattern % (count + multiplier)):
            count += multiplier
        multiplier //= 10
    return count + 1


class Operation(object):
    session = tf.Session()

    def __init__(self, operation, operand=None):
        if operand:
            self.x = operand.x
            self.variables_ = operand.variables()
            self.regularisation_candidates_ = operand.regularisation_candidates()
            operand = operand.operation
        else:
            self.x = tf.placeholder(tf.float32, name='x')
            self.variables_ = []
            self.regularisation_candidates_ = []
            operand = self.x
        self.operation = operation(operand)

    def __call__(self, value):
        return self.session.run(self.operation, feed_dict={self.x: value})

    def save(self, file_name):
        saver = tf.train.Saver()
        tf.add_to_collection('prediction', self.operation)
        saver.save(self.session, file_name)

    @classmethod
    def restore(cls, file_name):
        saver = tf.train.import_meta_graph(file_name + '.meta')
        saver.restore(cls.session, file_name)
        prediction = tf.get_collection('prediction')[0]
        return LoadedModel(prediction)

    def variables(self):
        return self.variables_

    def regularisation_candidates(self):
        return self.regularisation_candidates_


class LoadedModel(Operation):
    def __init__(self, prediction):
        self.x = 'x:0'
        self.operation = prediction


class FeatureScale(Operation):
    def __init__(self, data, operand=None, maximum=1):
        data = np.float32(data)
        self.average = tf.Variable(np.average(data, axis=0))
        self.std = tf.Variable(1.0 / np.maximum(np.std(data, axis=0), 1.0 / maximum))
        self.session.run(tf.global_variables_initializer())
        super(FeatureScale, self).__init__(lambda x: tf.multiply(tf.subtract(x, self.average), self.std), operand)


class Offset(Operation):
    def __init__(self, offset, operand=None):
        super(Offset, self).__init__(lambda x: tf.add(x, -offset), operand)


class Scale(Operation):
    def __init__(self, scale, operand=None):
        super(Scale, self).__init__(lambda x: tf.multiply(x, 1.0 / scale), operand)


class Reshape(Operation):
    def __init__(self, shape, operand=None):
        super(Reshape, self).__init__(lambda x: tf.reshape(x, shape), operand)


class Sigmoid(Operation):
    def __init__(self, operand=None):
        super(Sigmoid, self).__init__(lambda x: tf.sigmoid(x), operand)


class ReLU(Operation):
    def __init__(self, operand=None):
        super(ReLU, self).__init__(lambda x: tf.nn.relu(x), operand)


class Weights(Operation):
    def __init__(self, weights, operand=None):
        self.weights = tf.Variable(np.float32(weights))
        self.session.run(tf.global_variables_initializer())
        super(Weights, self).__init__(lambda x: tf.matmul(x, self.weights), operand)

    def __call__(self, value):
        value = np.float32(value)
        if len(value.shape) < 2:
            return super(Weights, self).__call__([value])[0]
        else:
            return super(Weights, self).__call__(value)

    def variables(self):
        return super(Weights, self).variables() + [self.weights]

    def regularisation_candidates(self):
        return super(Weights, self).regularisation_candidates() + [self.weights]

    def shape(self):
        return self.weights.shape


class Bias(Operation):
    def __init__(self, bias, operand=None):
        self.bias = tf.Variable(np.float32(bias))
        self.session.run(tf.global_variables_initializer())
        super(Bias, self).__init__(lambda x: tf.add(x, self.bias), operand)

    def variables(self):
        return super(Bias, self).variables() + [self.bias]

    def shape(self):
        return self.bias.shape


class Softmax(Operation):
    def __init__(self, operand=None):
        super(Softmax, self).__init__(lambda x: tf.nn.softmax(x), operand)


class Regularisation(Operation):
    def __init__(self, model):
        candidates = model.regularisation_candidates()
        term = reduce(add, [tf.reduce_sum(tf.square(candidate)) for candidate in candidates])
        super(Regularisation, self).__init__(lambda x: term / (2 * tf.cast(tf.shape(x)[0], tf.float32)), model)
