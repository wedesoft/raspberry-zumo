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


class Operation:
    def __init__(self, operation):
        self.x = tf.placeholder(tf.float32, name='x')
        self.operation = operation(self.x)

    def __call__(self, value):
        with tf.Session() as session:
            return session.run(self.operation, feed_dict={self.x: value})


class Offset(Operation):
    def __init__(self, offset):
        super(Offset, self).__init__(lambda x: tf.add(x, offset))


class Scale(Operation):
    def __init__(self, scale):
        super(Scale, self).__init__(lambda x: tf.multiply(x, scale))
