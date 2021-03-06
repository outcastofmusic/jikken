"""
Example taken from [Deep Learning with Python](https://www.manning.com/books/deep-learning-with-python)
Based on this notebook:
https://github.com/fchollet/deep-learning-with-python-notebooks/blob/master/3.5-classifying-movie-reviews.ipynb
"""
import click
import numpy as np
import yaml
from jikken import log_value
from keras import layers
from keras import models
from keras import optimizers
from keras.callbacks import LambdaCallback
from keras.datasets import imdb
import os

# add a callback to jikken for val_loss using LambdaCallback
jikken_callback = LambdaCallback(on_epoch_end=lambda epoch, logs: log_value('val_loss', logs.get('val_loss', np.nan)))


@click.command()
@click.argument('configuration_path', type=click.Path(exists=True, file_okay=True))
@click.option('-i', '--input_dir', type=click.Path(exists=False, file_okay=False, dir_okay=True))
@click.option('-o', '--output_dir', required=True, type=click.Path(exists=False, file_okay=False, dir_okay=True))
@click.option('--data_size', type=int, default=-1)
def train(configuration_path, input_dir, output_dir, data_size):
    print(output_dir)
    with open(configuration_path) as file_handle:
        config = yaml.load(file_handle)

    data_size = data_size if data_size > 0 else config['dataset_size']
    (train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=data_size)

    def vectorize_sequences(sequences, dimension=data_size):
        # Create an all-zero matrix of shape (len(sequences), dimension)
        results = np.zeros((len(sequences), dimension))
        for i, sequence in enumerate(sequences):
            results[i, sequence] = 1.  # set specific indices of results[i] to 1s
        return results

    # Our vectorized training data
    x_train = vectorize_sequences(train_data)
    # Our vectorized test data
    x_test = vectorize_sequences(test_data)

    # Our vectorized labels
    y_train = np.asarray(train_labels).astype('float32')
    y_test = np.asarray(test_labels).astype('float32')
    if input_dir is not None and os.path.exists(input_dir):
        model = models.load_model(os.path.join(input_dir, "model.h5"))
        print("model loaded")
    else:
        print("model created")
        model = models.Sequential()
        model.add(layers.Dense(16, activation='relu', input_shape=(data_size,)))
        model.add(layers.Dense(16, activation='relu'))
        model.add(layers.Dense(1, activation='sigmoid'))

        model.compile(optimizer=optimizers.RMSprop(lr=config['learning_rate']),
                      loss='binary_crossentropy',
                      metrics=['accuracy']
                      )

    x_val = x_train[:config['valid_size']]
    partial_x_train = x_train[config['valid_size']:]

    y_val = y_train[:config['valid_size']]
    partial_y_train = y_train[config['valid_size']:]

    history = model.fit(partial_x_train,
                        partial_y_train,
                        epochs=config['epochs'],
                        batch_size=config['batch_size'],
                        validation_data=(x_val, y_val),
                        callbacks=[jikken_callback]
                        )
    log_value('final_val_loss', history.history['val_loss'][-1])
    if output_dir is not None:
        model.save(os.path.join(output_dir, "model.h5"))


if __name__ == '__main__':
    train()
