from sciope.inference import abc_inference
from sciope.models.cnn_regressor import CNNModel
# from sciope.models.cnn_regressor_normal import CNNModel

from sciope.models.pen_regressor_beta import PEN_CNNModel
from sciope.models.dnn_regressor import ANNModel
from load_data_from_julia import load_data
import numpy as np
from AutoRegressive_model import simulate, prior
# from MovingAverage_model import simulate, prior
from sklearn.metrics import mean_absolute_error
import pickle
import time
from normalize_data import normalize_data
from load_data import load_spec



num_timestamps=401
endtime=200
modelname = "vilar_ACR_prior3_" + str(endtime) + "_" + str(num_timestamps)

dmin = [35, 200,  0,  30, 30, 2,  5,  0,  0.9,   0, 0.5, 0.5, 1.8, 30, 80]
dmax = [55, 550, 0.1, 55, 55, 6, 12, 0.7, 1.4, 0.3, 1.1, 1.2, 2.2, 60, 110]

#Load data
train_thetas, train_ts = load_spec(modelname=modelname, type = "train")
validation_thetas = pickle.load(open('datasets/' + modelname + '/validation_thetas.p', "rb" ) )
validation_ts = pickle.load(open('datasets/' + modelname + '/validation_ts.p', "rb" ) )


print("dmin:", dmin)
print("train thetas min: ", np.min(train_thetas, axis=0))
print("dmax:", dmax)
print("train thetas max: ", np.max(train_thetas, axis=0))

#Normalize parameter values
train_thetas = normalize_data(train_thetas,dmin,dmax)
validation_thetas = normalize_data(validation_thetas,dmin,dmax)


ts_len = train_ts.shape[1]
# choose neural network model
nnm = CNNModel(input_shape=(ts_len,3), output_shape=(15), con_len=2, con_layers=[25,50,100])
# nnm = PEN_CNNModel(input_shape=(ts_len,3), output_shape=(15), pen_nr=10)
# nnm = ANNModel(input_shape=(ts_len, 3), output_shape=(15))

# nnm.load_model()
start_time = time.time()
nnm.train(inputs=train_ts, targets=train_thetas,validation_inputs=validation_ts,validation_targets=validation_thetas,
          batch_size=32, epochs=40, plot_training_progress=False)

nnm.train(inputs=train_ts, targets=train_thetas,validation_inputs=validation_ts,validation_targets=validation_thetas,
          batch_size=4096, epochs=5, plot_training_progress=False)
end_time = time.time()
training_time = end_time - start_time
validation_pred = nnm.predict(validation_ts)
validation_pred = np.reshape(validation_pred,(-1,15))
print("training time: ", training_time)
print("mean square error: ", np.mean((validation_thetas-validation_pred)**2))
print("mean absolute error: ", np.mean(abs(validation_thetas-validation_pred)))


# nnm.load_model()
#validation_pred = np.array([nnm.predict(validation_ts[i*100:(i+1)*100]) for i in range(500)])


# test_thetas = pickle.load(open('datasets/' + modelname + '/test_thetas.p', "rb" ) )
# test_ts = pickle.load(open('datasets/' + modelname + '/test_ts.p', "rb" ) )
# test_thetas = normalize_data(test_thetas,dmin,dmax)
# test_pred = nnm.predict(test_ts)
# test_pred = np.reshape(test_pred,(-1,15))
#
# test_mse = np.mean((test_thetas-test_pred)**2)
# test_mae = np.mean(abs(test_thetas-test_pred))
# test_ae = np.mean(abs(test_thetas-test_pred),axis=0)
#
# print("Model name: ", nnm.name)
# print("mean square error: ", test_mse)
# print("mean square error: ", test_mae)
#
# test_results = {"model name": nnm.name, "training_time": training_time, "mse": test_mse, "mae": test_mae, "ae": test_ae}
# pickle.dump(test_results, open('results/training_results_' + modelname + '.p', "wb"))
#