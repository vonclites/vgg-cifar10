from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from tensorflow.contrib.layers.python.layers import utils

slim = tf.contrib.slim

#TODO I changed tensorflow so that convolution2d uses a device parameter...
def inference(inputs,
              num_classes=10,
              is_training=True,
              dropout_keep_prob=0.5,
              spatial_squeeze=True,
              scope='vgg_16'):
    """Customized Oxford Net VGG 16-Layers for CIFAR10-size images.

    Note: All the fully_connected layers have been transformed to conv2d layers

    Args:
        inputs: a tensor of size [batch_size, height, width, channels].
        num_classes: number of predicted classes.
        is_training: whether or not the model is being trained.
        dropout_keep_prob: the probability that activations are kept in the
            dropout layers during training.
        spatial_squeeze: whether or not should squeeze the spatial dimensions
            of the outputs. Useful to remove unnecessary dimensions for
            classification.
        scope: Optional scope for the variables.

    Returns:
        the last op containing the log predictions and end_points dict.
    """
    with slim.arg_scope(vgg_arg_scope()):
        with tf.variable_scope(scope, 'vgg_16', [inputs]) as sc:
            net = slim.repeat(inputs, 2, slim.conv2d, 64, [3, 3], scope='conv1')
            net = slim.max_pool2d(net, [3, 3], scope='pool1')
            net = slim.repeat(net, 2, slim.conv2d, 128, [3, 3], scope='conv2')
            net = slim.max_pool2d(net, [3, 3], scope='pool2')
            net = slim.repeat(net, 3, slim.conv2d, 256, [3, 3], scope='conv3')
            net = slim.max_pool2d(net, [3, 3], scope='pool3')
            net = slim.repeat(net, 3, slim.conv2d, 512, [3, 3], scope='conv4')
            net = slim.max_pool2d(net, [2, 2], scope='pool4')
            net = slim.repeat(net, 3, slim.conv2d, 512, [3, 3], scope='conv5')
            net = slim.max_pool2d(net, [2, 2], scope='pool5')
            # Use conv2d instead of fully_connected layers.
            net = slim.conv2d(net, 600, [1, 1], padding='VALID', scope='fc6')
            net = slim.dropout(net, dropout_keep_prob, is_training=is_training,
                               scope='dropout6')
            net = slim.conv2d(net, 300, [1, 1], scope='fc7')
            net = slim.dropout(net, dropout_keep_prob, is_training=is_training,
                               scope='dropout7')
            net = slim.conv2d(net, num_classes, [1, 1],
                              activation_fn=None,
                              normalizer_fn=None,
                              scope='fc8')
        # Convert end_points_collection into a end_point dict.
        end_points = utils.convert_collection_to_dict('end_points')
        if spatial_squeeze:
            net = tf.squeeze(net, [1, 2], name='fc8/squeezed')
            end_points[sc.name + '/fc8'] = net
        return net, end_points


def vgg_arg_scope(variables_device, weight_decay=0.0005):
    """Defines the VGG arg scope.

    Args:
        variables_device: The device on which to store variables
            e.g. '/device:CPU:0'
        weight_decay: The l2 regularization coefficient.

    Returns:
        An arg_scope.
    """
    with slim.arg_scope([slim.conv2d, slim.max_pool2d],
                        padding='SAME',
                        outputs_collections='end_points'):
        with slim.arg_scope([slim.conv2d],
                            activation_fn=tf.nn.relu,
                            weights_regularizer=slim.l2_regularizer(
                                weight_decay),
                            normalizer_fn=slim.batch_norm,
                            device=variables_device) as arg_sc:
            return arg_sc
