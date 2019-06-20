#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 15:00:22 2019

@author: zubarei1
"""
import tensorflow as tf


class Optimizer(object):
    def __init__(self, params):
        self.params = params
        # TODO : add cost function options,
        # TODO : class balance
        # TODO : regularization options,
        # TODO : performance metric options

    def _set_optimizer(self, y_pred, y_true):
        """Initializes the optimizer part of the computational graph

        This method can be overriden a for custom optimizer

        Inputs:
        -------
        y_pred : tf.Tensor
                        predictions of the target varible, output of the
                        computational graph

        y_true : tf.Tensor
                        target_variable, output of dataset.iterator

        Returns:
        --------
        train_step : tf.Operation
                    training operation


        performance : tf.Tensor
                    performance metric

        cost : tf.Tensor
                    cost (objective) function output

        prediciton : tf.Tensor
                    model output
        """
        # Define cost, and performance metric, treat prediction if needed
        if self.params['task'] == 'classification':
            cost_function = tf.nn.sparse_softmax_cross_entropy_with_logits

            prediction = tf.nn.softmax(y_pred)
            cost = tf.reduce_mean(cost_function(labels=y_true, logits=y_pred))
            correct_prediction = tf.equal(tf.argmax(y_pred, 1), y_true)
            performance = tf.reduce_mean(tf.cast(correct_prediction,
                                                 tf.float32), name='accuracy')

        elif self.params['task'] == 'ae':
            cost = tf.reduce_sum((y_true-y_pred)**2)
            var = tf.reduce_sum(y_true**2)
            performance = 1 - cost/var
            prediction = y_pred

        #  Regularization
        if self.params['l1_lambda'] > 0:
            coef = self.params['l1_lambda']
            reg = [tf.reduce_sum(tf.abs(var))
                   for var in tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
                   if 'weights' in var.name]
        elif self.params['l2_lambda'] > 0:
            coef = self.params['l2_lambda']
            reg = [tf.nn.l2_loss(var) for var in
                   tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
                   if 'weights' in var.name]
        else:
            coef = 0
            reg = 0

        weight_penalty = coef * tf.add_n(reg)
        cost = cost + weight_penalty

        #  Optimizer
        backprop = tf.train.AdamOptimizer
        train_step = backprop(self.params['learn_rate']).minimize(cost)

        return train_step, performance, cost, prediction
