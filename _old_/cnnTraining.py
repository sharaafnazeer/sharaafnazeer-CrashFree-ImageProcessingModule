import matplotlib.pyplot as plt
import seaborn as sns
from keras.models import *
from keras.layers import *
from keras.preprocessing.image import *
from keras.optimizers import *

from sklearn.metrics import classification_report, confusion_matrix

import tensorflow as tf

# Sequential()
import cv2
import os

import numpy as np

labels = ['alert', 'drowsy']
img_size = 32


def get_data(data_dir):
    data = []
    for label in labels:
        path = os.path.join(data_dir, label)
        class_num = labels.index(label)
        for img in os.listdir(path):
            try:
                img_arr = cv2.imread(os.path.join(path, img))[..., ::-1]  # convert BGR to RGB format
                resized_arr = cv2.resize(img_arr, (img_size, img_size))  # Reshaping images to preferred size
                data.append([resized_arr, class_num])
            except Exception as e:
                print(e)
    return np.array(data)


train = get_data('data/images/train')
val = get_data('data/images/test')

# l = []
# for i in train:
#     print(i[1])
#     if i[1] == 1:
#         l.append("Drowsy")
#     elif i[1] == 0:
#         l.append("Alert")
# sns.set_style('darkgrid')
# sns.countplot(l)
#
# plt.figure(figsize=(5, 5))
# plt.imshow(train[1][0])
# plt.title(labels[train[0][1]])
# plt.show()
#
# plt.figure(figsize=(5, 5))
# plt.imshow(train[-1][0])
# plt.title(labels[train[-1][1]])
# plt.show()

x_train = []
y_train = []
x_val = []
y_val = []

for feature, label in train:
    x_train.append(feature)
    y_train.append(label)

for feature, label in val:
    x_val.append(feature)
    y_val.append(label)

# Normalize the data
x_train = np.array(x_train) / 255
x_val = np.array(x_val) / 255

x_train.reshape(-1, img_size, img_size, 1)
y_train = np.array(y_train)

x_val.reshape(-1, img_size, img_size, 1)
y_val = np.array(y_val)

datagen = ImageDataGenerator(
    featurewise_center=False,  # set input mean to 0 over the dataset
    samplewise_center=False,  # set each sample mean to 0
    featurewise_std_normalization=False,  # divide inputs by std of the dataset
    samplewise_std_normalization=False,  # divide each input by its std
    zca_whitening=False,  # apply ZCA whitening
    rotation_range=30,  # randomly rotate images in the range (degrees, 0 to 180)
    zoom_range=0.2,  # Randomly zoom image
    width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
    height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
    horizontal_flip=True,  # randomly flip images
    vertical_flip=False)  # randomly flip images

datagen.fit(x_train)

model = Sequential()
model.add(Conv2D(32, 3, strides=(1, 1), padding='valid', activation='relu', input_shape=(32, 32, 3)))
model.add(MaxPool2D())

model.add(Conv2D(16, 3, padding="same", activation="relu"))
model.add(MaxPool2D())

model.add(Conv2D(8, 3, padding="same", activation="relu"))
model.add(MaxPool2D())

model.add(Conv2D(4, 3, padding="same", activation="relu"))
model.add(MaxPool2D())
model.add(Dropout(0.4))

model.add(Flatten())
model.add(Dense(128, activation="relu"))
model.add(Dense(2, activation="softmax"))

model.summary()

opt = Adam(lr=0.000001)
model.compile(optimizer=opt, loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), metrics=['accuracy'])

# train_data = tf.data.Dataset.from_tensor_slices((x_train, y_train))
# valid_data = tf.data.Dataset.from_tensor_slices((x_val, y_val))

history = model.fit(x_train, y_train, epochs=500, validation_data=(x_val, y_val))

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(500)

plt.figure(figsize=(15, 15))
plt.subplot(2, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(2, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

predictions = model.predict_classes(x_val)
predictions = predictions.reshape(1, -1)[0]

print(classification_report(y_val, predictions, target_names=['Awake (Class 0)', 'Drowsy (Class 1)']))

model.save('models/cnnDrowsyPrediction.dat')

base_model = tf.keras.applications.MobileNetV2(input_shape=(32, 32, 3), include_top=False, weights="imagenet")
base_model.trainable = False

model = tf.keras.Sequential([base_model,
                             tf.keras.layers.GlobalAveragePooling2D(),
                             tf.keras.layers.Dropout(0.2),
                             tf.keras.layers.Dense(2, activation="softmax")
                             ])

base_learning_rate = 0.00001
model.compile(optimizer=tf.keras.optimizers.Adam(lr=base_learning_rate),
              loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
              metrics=['accuracy'])

history = model.fit(x_train, y_train, epochs=500, validation_data=(x_val, y_val))

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs_range = range(500)

plt.figure(figsize=(15, 15))
plt.subplot(2, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(2, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()
