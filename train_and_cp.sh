./build/tools/caffe train -solver models/DHN/nus_wide/solver.prototxt -weights models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel -gpu 2 2>&1 | tee train_log.log $@
cp tanhout0.txt qlossout.txt qdiffout.txt ~/tensorflow
