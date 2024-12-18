import mne
import pandas as pd
import numpy as np
from sklearn import preprocessing

from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense, LSTM, Activation
from tensorflow import keras
import tensorflow as tf 

import pybullet as p
import pybullet_data
from time import sleep

dfs = []
for i in range(10):
    dfs.append((mne.io.read_raw_gdf('level-1/S02_ME/motorexecution_subject2_run'+str(i+1)+'.gdf').to_data_frame()))
S02_ME = pd.concat(dfs)

S02_ME = S02_ME.drop(['eog-l', 'eog-m', 'eog-r', 'thumb_near', 'thumb_far', 'thumb_index', 
                      'index_near', 'index_far', 'index_middle', 'middle_near', 'middle_far', 
                      'middle_ring', 'ring_near', 'ring_far', 'ring_little', 'litte_near', 'litte_far',
                      'thumb_palm', 'wrist_bend', 'roll', 'pitch', 'gesture'], axis=1)
S02_ME = S02_ME.dropna()

scaler = preprocessing.MinMaxScaler()
S02_ME_scaled = pd.DataFrame(scaler.fit_transform(S02_ME.values), columns=S02_ME.columns, index=S02_ME.index)

print(S02_ME_scaled.columns)
print(S02_ME_scaled.columns[1:62])
print(S02_ME_scaled.columns[71:75])

X = S02_ME_scaled.iloc[:, 1:62].values
y = S02_ME_scaled.iloc[:, 71:75].values

X = X[:1000]
y = y[:1000]
# X = X[9000:10000]
# y = y[9000:10000]

opt = keras.optimizers.Adam(learning_rate=0.0001)
model = Sequential()
model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(10, 61)))
model.add(LSTM(50, activation='relu'))
model.add(Dense(4))
model.add(Activation('linear'))
model.compile(loss='mse', optimizer=opt)

model = keras.models.load_model('level-1/trial_1_model.h5')

class DataGenerator2D(Sequence):
    def __init__(self, X, y, n_steps_in, batch_size=64, shuffle=True):
        self.X = X
        self.y = y
        self.n_steps_in = n_steps_in
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.on_epoch_end()
    
    def __len__(self):
        return int(np.ceil((self.X.shape[0]-self.n_steps_in)/float(self.batch_size)))

    def get_seq(self, i):
        end_ix = i+10
        seq_x, seq_y = self.X[i:end_ix], self.y[end_ix-1:end_ix]
        return seq_x, seq_y

    def __getitem__(self, index):
        if (index+1)*self.batch_size > self.X.shape[0]:
            batch = self.indexes[index*self.batch_size:]
        else:
            batch = self.indexes[index*self.batch_size:(index+1)*self.batch_size]

        X, y = [], []
        for i in batch:
            X_item, y_item = self.get_seq(i)
            X.append(X_item)
            y.append(y_item)

        X, y = np.array(X), np.array(y)
        y = np.reshape(y, (y.shape[0], y.shape[1]*y.shape[2]))

        return X, y

    def on_epoch_end(self):
        self.indexes = np.arange(self.X.shape[0]-self.n_steps_in)
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

test_generator = DataGenerator2D(X, y, n_steps_in=10, batch_size=64, shuffle=False)
op = model.predict(test_generator)
print(op.shape)

# print(max(op[:,3]))
# print(min(op[:,3]))
# print(np.mean(op[:,3]))

physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
# p.setGravity(0,0,0)

startPos = [0,0,0]
startOrientation = p.getQuaternionFromEuler([0,0,0])
simulationId = p.loadURDF("level-1/2f1t.urdf", startPos, startOrientation)

# Grab = p.addUserDebugParameter('Grab', 0, 30.0, 0)
# Elbow = p.addUserDebugParameter('Elbow', -1.5, 1.5, 0)
grab_indices = [2,3,4]
elbow_indices = [0]
wrist_indices = [1]

for i in op:
    user_grab = i[3]*30
    user_elbow = i[0]*2.617
    user_wrist = i[1]*9
    if user_wrist == 9:
        user_elbow = 0
    # user_grab = 30
    # user_elbow = 3

    print("Grab: {:.9f}, Elbow: {:.9f}, Wrist: {:.9f}".format(user_grab, user_elbow, user_wrist))

    for joint_index in grab_indices:
        p.setJointMotorControl2(simulationId, joint_index,
                                p.POSITION_CONTROL,
                                targetVelocity=user_grab)
    
    for joint_index in wrist_indices:
        p.setJointMotorControl2(simulationId, joint_index,
                                p.POSITION_CONTROL,
                                targetPosition=user_wrist)
    
    for joint_index in elbow_indices:
        p.setJointMotorControl2(simulationId, joint_index,
                                p.POSITION_CONTROL, 
                                targetPosition=user_elbow)

    p.stepSimulation()
    sleep(0.8)
p.disconnect()
