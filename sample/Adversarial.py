from __future__ import print_function

import os,sys
import numpy as np
import scipy.io as scio
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
import json

import matplotlib.pyplot as plt  
import numpy as np

# GPU setup
physical_devices = tf.config.list_physical_devices('GPU')
print(physical_devices)
if len(physical_devices) > 0:
    for device in physical_devices:
        try:
            tf.config.experimental.set_memory_growth(device, True)
            print(f'Memory growth enabled for GPU device: {device}')
        except RuntimeError as e:
            print(f'Error setting memory growth: {e}')
else:
    print('No GPU devices found. Running on CPU.')

# Rest of imports
import keras
from keras.layers import Input, GRU, Dense, Flatten, Dropout, Conv2D, Conv3D, MaxPooling2D, MaxPooling3D, TimeDistributed, Bidirectional, Multiply, Permute, RepeatVector, Concatenate, Dot, Lambda
from keras.models import Model, load_model
import keras.backend as K
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split


# Parameters remain unchanged
use_existing_model = False
fraction_for_test = 0.1
data_dir = '/home/alex/Work_Team/Work2025/synthetic_csi_data'
ALL_MOTION = [1,2,3,4,5]  # 5 height classes
N_MOTION = len(ALL_MOTION)
N_LOCATION = 15  # 15 x position
N2_LOCATION = 18 # 18 y position
T_MAX = 0
n_epochs = 500
f_dropout_ratio = 0.5
n_gru_hidden_units = 64
n_batch_size = 32
f_learning_rate = 0.001
loss_weight_domain = 1

# All existing functions remain exactly the same
def normalize_data(data_1):
    data_1_max = np.amax(data_1,(0,1),keepdims=True)
    data_1_min = np.amin(data_1,(0,1),keepdims=True)
    data_1_max_rep = np.tile(data_1_max,(data_1.shape[0],data_1.shape[1],1))
    data_1_min_rep = np.tile(data_1_min,(data_1.shape[0],data_1.shape[1],1))
    data_1_norm = (data_1 - data_1_min_rep) / (data_1_max_rep - data_1_min_rep + sys.float_info.min)
    return  data_1_norm

def zero_padding(data, T_MAX):
    data_pad = []
    for i in range(len(data)):
        t = np.array(data[i]).shape[2]
        data_pad.append(np.pad(data[i], ((0,0),(0,0),(T_MAX - t,0)), 'constant', constant_values = 0).tolist())
    return np.array(data_pad)

def onehot_encoding(label, num_class):
    label = np.array(label).astype('int32')
    label = np.squeeze(label)
    _label = np.eye(num_class)[label-1]
    return _label

def load_data(path_to_data):
    global T_MAX
    data = []
    label = []
    domain = []
    domain2 = []
    for data_root, data_dirs, data_files in os.walk(path_to_data):
        for data_file_name in data_files:
            file_path = os.path.join(data_root, data_file_name)
            try:
                parts = data_file_name.replace('.mat', '').split('-')
                if len(parts) >= 5:
                    height = int(parts[1])
                    x_pos = int(parts[2])
                    y_pos = int(parts[3])
                    repetition = int(parts[4])
                    
                    mat_data = scio.loadmat(file_path)
                    data_1 = mat_data['doppler_spectrum']
                    
                    data_padded = np.pad(data_1, ((0,3), (0,0), (0,0)), 'constant', constant_values=0)
                    data_upsampled = np.zeros((6, 121, 5))
                    for ch in range(6):
                        for t in range(5):
                            x_original = np.linspace(0, 1, 12)
                            x_upsampled = np.linspace(0, 1, 121)
                            data_upsampled[ch,:,t] = np.interp(x_upsampled, x_original, data_padded[ch,:,t])
                    
                    data_1 = data_upsampled

                    if height not in ALL_MOTION:
                        continue

                    data_normed_1 = normalize_data(data_1)

                    if T_MAX < np.array(data_1).shape[2]:
                        T_MAX = np.array(data_1).shape[2]

                    data.append(data_normed_1.tolist())
                    label.append(height)
                    domain.append(x_pos)
                    domain2.append(y_pos)

            except Exception as e:
                print(f"Skipping file {file_path} due to error: {e}")
                continue

    if len(data) == 0:
        raise ValueError("No valid data found, exiting load_data.")

    data = zero_padding(data, T_MAX)

    if len(data) > 0 and data[0].ndim == 3:
        data = np.swapaxes(np.swapaxes(data, 1, 3), 2, 3)
        data = np.expand_dims(data, axis=-1)
    else:
        raise ValueError(f"Unexpected data shape after padding: {np.array(data).shape}. Expected 4 dimensions.")

    label = np.array(label)
    domain = np.array(domain)
    domain2 = np.array(domain2)

    return data, label, domain, domain2

def custom_loss_label():
    def lossfn(y_true, y_pred):
        myloss_batch = -1 * tf.reduce_sum(y_true * tf.math.log(y_pred + tf.keras.backend.epsilon()), axis=-1, keepdims=False)
        myloss = tf.reduce_mean(myloss_batch, axis=-1, keepdims=False)  # ใช้ tf.reduce_mean แทน K.mean
        return myloss
    return lossfn

def custom_loss_domain():
    def lossfn(y_true, y_pred):
        myloss_batch = -1 * tf.reduce_sum(y_true * tf.math.log(y_pred + tf.keras.backend.epsilon()), axis=-1, keepdims=False)
        myloss = tf.reduce_mean(myloss_batch, axis=-1, keepdims=False)  # ใช้ tf.reduce_mean แทน K.mean
        return myloss
    return lossfn

def assemble_model(input_shape, n_class, n_location, n2_location):
    with tf.device('/GPU:0'):  # Explicitly use GPU
        model_input = Input(shape=input_shape, dtype='float32', name='name_model_input')
        
        x = TimeDistributed(Conv2D(32, kernel_size=(3,6), activation='relu'))(model_input)
        x = TimeDistributed(MaxPooling2D(pool_size=(2,2)))(x)
        x = TimeDistributed(Conv2D(64, kernel_size=(2,4), activation='relu'))(x)
        
        x = TimeDistributed(Flatten())(x)
        x = TimeDistributed(Dense(256, activation='relu'))(x)
        x = TimeDistributed(Dropout(f_dropout_ratio))(x)
        
        x = Bidirectional(GRU(n_gru_hidden_units, return_sequences=True))(x)
        x = Bidirectional(GRU(n_gru_hidden_units, return_sequences=False))(x)
        x_feat = Dropout(f_dropout_ratio)(x)
        
        x_1 = Dense(64, activation='relu')(x_feat)
        model_output_label = Dense(n_class, activation='softmax', name='name_model_output_label')(x_1)
        
        x_2 = Dense(128, activation='relu')(x_feat)
        model_output_domain = Dense(n_location, activation='softmax', name='name_model_output_domain')(x_2)
        
        x_3 = Dense(256, activation='relu')(x_feat)
        x_3 = Dense(128, activation='relu')(x_3)
        model_output_domain2 = Dense(n2_location, activation='softmax', name='name_model_output_domain2')(x_3)
        
        model = Model(inputs=model_input, outputs=[model_output_label, model_output_domain, model_output_domain2])
        model.compile(optimizer=tf.keras.optimizers.RMSprop(learning_rate=f_learning_rate),

                loss = {
                    'name_model_output_label': custom_loss_label(),
                    'name_model_output_domain': custom_loss_domain(),
                    'name_model_output_domain2': custom_loss_domain()
                },
                loss_weights={
                    'name_model_output_label': 1,
                    'name_model_output_domain': 1,
                    'name_model_output_domain2': 2
                },
                metrics={
                    'name_model_output_label': 'accuracy',
                    'name_model_output_domain': 'accuracy',
                    'name_model_output_domain2': 'accuracy'
                }
                )
        
        return model
        
def plot_sample(data_sample, label, domain, domain2, sample_index):
    """
    data_sample: รูปแบบ (N, T, 6, 121, 1)
    label: ความสูง (class)
    domain: x position
    domain2: y position
    sample_index: index ของตัวอย่างที่ต้องการแสดง
    """
    d = data_sample[sample_index]  # (T, 6, 121, 1)
    d = np.squeeze(d)  # รูป (T, 6, 121)

    T = d.shape[0]  # จำนวน time steps
    fig, axs = plt.subplots(2, 3, figsize=(18, 8))
    fig.suptitle(f"Sample #{sample_index}\nLabel (Height Class): {label[sample_index]}, X-Position: {domain[sample_index]}, Y-Position: {domain2[sample_index]}", fontsize=16)

    for i in range(6):
        ax = axs[i // 3][i % 3]
        ax.imshow(d[:, i, :], aspect='auto', cmap='jet', origin='lower')
        ax.set_title(f'Channel {i}')
        ax.set_xlabel("Frequency Bins (121)")
        ax.set_ylabel("Time (T={})".format(T))
        
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.show()
    
# Main execution
if __name__ == "__main__":
    # Load data
    data, label, domain, domain2 = load_data(data_dir)
    print('\nLoaded dataset of ' + str(label.shape[0]) + ' samples, each sized ' + str(data[0,:,:,:,:].shape) + '\n')
    '''print("==================================")
    for data_root, data_dirs, data_files in os.walk(data_dir):
     for data_file_name in data_files:
      file_path = os.path.join(data_root, data_file_name)
      tata = scio.loadmat(file_path)
      data_2 = tata['doppler_spectrum']
      print(f"{data_file_name}: shape={data_2.shape}")
      
      plot_sample(data, label, domain, domain2, sample_index=5)'''


    for data_root, data_dirs, data_files in os.walk(data_dir):
     for data_file_name in data_files:
      if data_file_name.endswith('.mat'):
          file_path = os.path.join(data_root, data_file_name)
          tata = scio.loadmat(file_path)
          data_2 = tata['doppler_spectrum']
          if data_2.shape == (3, 12, 5):
          
             print(f"{data_file_name}: shape={data_2.shape}")
             
             heatmap = data_2[:, :, 0]  # Shape = (3, 12)

             plt.figure(figsize=(6, 4))
             plt.imshow(heatmap, aspect='auto', cmap='viridis')
             plt.colorbar(label='Amplitude')
             plt.title(f"{data_file_name}")
             plt.xlabel("Bin Index")
             plt.ylabel("Time Index")
             plt.tight_layout()
             plt.show()
             
	  
    exit(0)

    
    
    
    
    
    # Split train and test
    [data_train, data_test, label_train, label_test, domain_train, domain_test, domain2_train, domain2_test] = \
        train_test_split(data, label, domain, domain2, test_size=fraction_for_test)
    print('\nTrain on ' + str(label_train.shape[0]) + ' samples\n' +\
        'Test on ' + str(label_test.shape[0]) + ' samples\n')

    # One-hot encoding for train data
    label_train = onehot_encoding(label_train, N_MOTION)
    domain_train = onehot_encoding(domain_train, N_LOCATION)
    domain2_train = onehot_encoding(domain2_train, N2_LOCATION)

    # Train Model
    model = assemble_model(input_shape=(T_MAX, 6, 121, 1), n_class=N_MOTION, n_location=N_LOCATION, n2_location=N2_LOCATION)
    model.summary()
    
    with tf.device('/GPU:0'):  # Ensure training happens on GPU
        model.fit({'name_model_input': data_train},
                {'name_model_output_label': label_train, 
                'name_model_output_domain': domain_train,
                'name_model_output_domain2': domain2_train},
                batch_size=n_batch_size,
                epochs=n_epochs,
                verbose=1,
                validation_split=0.1, 
                shuffle=True)

    # Save model and test as before
    model_save_path = os.path.join(data_dir, 'saved_models')
    if not os.path.exists(model_save_path):
        os.makedirs(model_save_path)

    model_name = '/home/alex/Work_Team/Work-3/motion_classification_model.h5'
    model.save(os.path.join(model_save_path, model_name))
    print(f'\nModel saved to: {os.path.join(model_save_path, model_name)}\n')

    model_params = {
        'T_MAX': T_MAX,
        'N_MOTION': N_MOTION,
        'N_LOCATION': N_LOCATION,
        'N2_LOCATION': N2_LOCATION
    }
    params_name = '/home/alex/Work_Team/Work-3/save_model_500/model_params.json'
    with open(os.path.join(model_save_path, params_name), 'w') as f:
        json.dump(model_params, f)
    print(f'Model parameters saved to: {os.path.join(model_save_path, params_name)}\n')

    # Testing
    print('Testing...')
    with tf.device('/GPU:0'):  # Ensure prediction happens on GPU
        [label_test_pred, domain_test_pred, domain2_test_pred] = model.predict(data_test)
    
    label_test_pred = np.argmax(label_test_pred, axis=-1) + 1
    domain_test_pred = np.argmax(domain_test_pred, axis=-1) + 1
    domain2_test_pred = np.argmax(domain2_test_pred, axis=-1) + 1

    # Calculate and display metrics
    print('\nLabel Confusion Matrix:')
    cm = confusion_matrix(label_test, label_test_pred)
    print(cm)
    cm = cm.astype('float')/cm.sum(axis=1)[:, np.newaxis]
    cm = np.around(cm, decimals=2)
    print(cm)

    print('\nX Position Confusion Matrix:')
    cm_domain = confusion_matrix(domain_test, domain_test_pred)
    print(cm_domain)
    cm_domain = cm_domain.astype('float')/cm_domain.sum(axis=1)[:, np.newaxis]
    cm_domain = np.around(cm_domain, decimals=2)
    print(cm_domain)

    print('\nY Position Confusion Matrix:')
    cm_domain2 = confusion_matrix(domain2_test, domain2_test_pred)
    print(cm_domain2)
    cm_domain2 = cm_domain2.astype('float')/cm_domain2.sum(axis=1)[:, np.newaxis]
    cm_domain2 = np.around(cm_domain2, decimals=2)
    print(cm_domain2)

    label_accuracy = np.sum(label_test == label_test_pred) / (label_test.shape[0])
    domain_accuracy = np.sum(domain_test == domain_test_pred) / (domain_test.shape[0])
    domain2_accuracy = np.sum(domain2_test == domain2_test_pred) / (domain2_test.shape[0])

    print('\nTest Accuracies:')
    print('Label (Height) Accuracy:', label_accuracy)
    print('X Position Accuracy:', domain_accuracy)
    print('Y Position Accuracy:', domain2_accuracy)
