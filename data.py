import os.path
import numpy as np
import tensorflow as tf


def random_choice(count, size):
    return np.random.choice(count, size, replace=False)


def random_selection(size, *arrays):
    indices = random_choice(len(arrays[0]), size)
    result = tuple(np.take(array, indices, axis=0) for array in arrays)
    return result[0] if len(result) == 1 else result


def multi_class_label(labels, num_classes):
    index = np.arange(len(labels) * num_classes).reshape(len(labels), num_classes)
    return np.where(np.equal(index % num_classes, np.expand_dims(labels, -1)), 1, 0)


def count_files(pattern, multiplier=1000, exist=os.path.exists):
    count = -1
    while multiplier > 0:
        while exist(pattern % (count + multiplier)):
            count += multiplier
        multiplier //= 10
    return count + 1


class Operation(object):
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
        with tf.Session() as session:
            session.run(tf.global_variables_initializer())
            return session.run(self.operation, feed_dict={self.x: value})

    def variables(self):
        return self.variables_

    def regularisation_candidates(self):
        return self.regularisation_candidates_


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


class Bias(Operation):
    def __init__(self, bias, operand=None):
        self.bias = tf.Variable(np.float32(bias))
        super(Bias, self).__init__(lambda x: tf.add(x, self.bias), operand)

    def variables(self):
        return super(Bias, self).variables() + [self.bias]
