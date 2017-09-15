##################################################################################
# 2017 01.16 Created by Shichen Liu                                              #
# Residual Transfer Network implemented by tensorflow                            #
#                                                                                #
#                                                                                #
##################################################################################

import os
import sys
import numpy as np
import scipy.io as sio
import scipy as sp
import random
import cv2
import caffe
import os.path as opath
from multiprocessing import Pool
IMAGE_SIZE = 227

def save_code_and_label(params):
    database_code = np.sign(params['database_code'])
    validation_code = np.sign(params['validation_code'])
    database_labels = params['database_labels']
    validation_labels = params['validation_labels']
    path = params['path']
    np.save(opath.join(path, params["prefix"]+"database_code.npy"), database_code)
    np.save(opath.join(path, params["prefix"]+"database_label.npy"), database_labels)
    np.save(opath.join(path, params["prefix"]+"validation_code.npy"), validation_code)
    np.save(opath.join(path, params["prefix"]+"validation_label.npy"), validation_labels)

def get_codes_and_labels(params):
    caffe.set_device(params['gpu_id'])
    caffe.set_mode_gpu()
    model_file = params['model_file']
    pretrained_model = params['pretrained_model']
    dims = params['image_dims']
    scale = params['scale']
    database = open(params['database'], 'r').readlines()
    validation = open(params['validation'], 'r').readlines()
    batch_size = params['batch_size']

    if 'mean_file' in params:
        mean_file = params['mean_file']
        net = caffe.Classifier(model_file, pretrained_model, channel_swap=(2,1,0), image_dims=dims, mean=np.load(mean_file).mean(        1).mean(1), raw_scale=scale)
    else:
        net = caffe.Classifier(model_file, pretrained_model, channel_swap=(2,1,0), image_dims=dims, raw_scale=scale)

    database_code = []
    validation_code = []
    database_labels = []
    validation_labels = []
    cur_pos = 0

    while 1:
        lines = database[cur_pos : cur_pos + batch_size]
        if len(lines) == 0:
            break;
        cur_pos = cur_pos + len(lines)
        images = [caffe.io.load_image(line.strip().split(" ")[0]) for line in lines]
        labels = [[int(i) for i in line.strip().split(" ")[1:]] for line in lines]
        codes = net.predict(images, oversample=False)
        [database_code.append(c) for c in codes]
        [database_labels.append(l) for l in labels]

        print str(cur_pos) + "/" + str(len(database))
        if len(lines) < batch_size:
            break;

    cur_pos = 0
    while 1:
        lines = validation[cur_pos : cur_pos + batch_size]
        if len(lines) == 0:
            break;
        cur_pos = cur_pos + len(lines)
        images = [caffe.io.load_image(line.strip().split(" ")[0]) for line in lines]
        labels = [[int(i) for i in line.strip().split(" ")[1:]] for line in lines]

        codes = net.predict(images, oversample=False)
        [validation_code.append(c) for c in codes]
        [validation_labels.append(l) for l in labels]

        print str(cur_pos) + "/" + str(len(validation))
        if len(lines) < batch_size:
            break;

    return dict(database_code=database_code, database_labels=database_labels, validation_code=validation_code, validation_labels=validation_labels)
 

def load_code_and_label(params):
    path = params['path']
    params['database_code'] = np.load(opath.join(path, params["prefix"]+"database_code.npy"))
    params['database_labels'] = np.load(opath.join(path, params["prefix"]+"database_label.npy"))
    params['validation_code'] = np.load(opath.join(path, params["prefix"]+"validation_code.npy"))
    params['validation_labels'] = np.load(opath.join(path, params["prefix"]+"validation_label.npy"))

def hamming_radius2(params):
    database_code = np.array(params['database_code'])
    validation_code = np.array(params['validation_code'])
    database_labels = np.array(params['database_labels'])
    validation_labels = np.array(params['validation_labels'])
    R = params['R']
    query_num = validation_code.shape[0]
    
    database_code = np.sign(database_code)
    validation_code = np.sign(validation_code)

    sim = np.dot(validation_code, database_code.T)
    ground_truth = np.dot(validation_labels, database_labels.T)
    ground_truth[ground_truth>0] = 1.0 
    length_of_code = database_code.shape[1]
    radius2 = sim >= (length_of_code - 4)
    not_radius2 = sim < (length_of_code - 4)
    sim[radius2] = 1.0
    sim[not_radius2] = 0.0
    ground_truth[not_radius2] = 0.0
    count_radius2 = np.sum(sim, axis=1)
    for i in xrange(count_radius2.shape[0]):
        if count_radius2[i] == 0:
            count_radius2[i] = 1.0
    return np.mean(np.divide(np.sum(ground_truth, axis=1), count_radius2))

nthreads = 4
ndevices = 3
params = []

for gpu_id in range(ndevices):
    for i in range(nthreads):
        params.append(dict(model_file="./deploy2.prototxt",
                      pretrained_model="../an/train/code16/tsne_train_nogrl_64.caffemodel",
                      image_dims=(256,256),
                      scale=255,
                      database="../../../data/challenge/parallel1/database" + str(nthreads*gpu_id+i) + ".txt",
                      validation="../../../data/challenge/parallel1/test" + str(nthreads*gpu_id+i) + ".txt",
                      batch_size=50,
                      mean_file="./ilsvrc_2012_mean.npy",
                      gpu_id=gpu_id))

loading_files = True
code_and_label = {}
if loading_files:
	code_and_label['path']="../an/train/code48"
	code_and_label['prefix']="code_48_new"
	load_code_and_label(code_and_label)
else:
	pool = Pool(nthreads*ndevices)
	results = pool.map(get_codes_and_labels, params)

	code_and_label = results[0]
	for i in range(1, nthreads*ndevices):
    	    [code_and_label['database_code'].append(c) for c in results[i]['database_code']]
    	    [code_and_label['database_labels'].append(c) for c in results[i]['database_labels']]
    	    [code_and_label['validation_code'].append(c) for c in results[i]['validation_code']]
    	    [code_and_label['validation_labels'].append(c) for c in results[i]['validation_labels']]
         
	code_and_label['path']="../an/train/code64"
        code_and_label['prefix']="code_64"
        save_code_and_label(code_and_label)

code_and_label['R'] = 5000
mAP = hamming_radius2(code_and_label)

aaa = open('./result', 'w')
aaa.write(str(mAP))
print mAP

