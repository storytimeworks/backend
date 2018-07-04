from PIL import Image
import numpy as np
import tensorflow as tf

x = keep_prob = prediction = None

def load_session():
    global x, keep_prob, prediction

    x = tf.placeholder(tf.float32, shape=[None, 784])

    def conv2d(x, W):
        return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding="SAME")

    def max_pool_2x2(x):
        return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")

    W_conv1 = tf.get_variable("W_conv1", shape=[5, 5, 1, 32])
    b_conv1 = tf.get_variable("b_conv1", shape=[32])

    x_image = tf.reshape(x, [-1, 28, 28, 1])

    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    W_conv2 = tf.get_variable("W_conv2", shape=[5, 5, 32, 64])
    b_conv2 = tf.get_variable("b_conv2", shape=[64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = tf.get_variable("W_fc1", shape=[7 * 7 * 64, 1024])
    b_fc1 = tf.get_variable("b_fc1", shape=[1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    W_fc2 = tf.get_variable("W_fc2", shape=[1024, 10])
    b_fc2 = tf.get_variable("b_fc2", shape=[10])

    y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
    prediction = tf.argmax(y_conv, 1)

    saver = tf.train.Saver()

    sess = tf.Session()
    saver.restore(sess, "./model/model.ckpt")

    return sess

def make_prediction(sess, image):
    global x, keep_prob, prediction

    image_data = (255 - np.asarray(image.getdata())[:,0].reshape(1, 784).astype(np.float32)) / 255
    result = sess.run(prediction, {x: image_data, keep_prob: 1.0})[0] + 1

    return result
