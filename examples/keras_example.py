# example taken from keras book
import click
import numpy as np
import yaml
from keras import layers
from keras import models
from keras import optimizers
from keras.datasets import imdb


@click.command()
@click.option('--configuration_path', '-c', required=True, type=click.Path(exists=True, file_okay=True))
def train(configuration_path):
    with open(configuration_path) as file_handle:
        config = yaml.load(file_handle)

    (train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=config['dataset_size'])

    def vectorize_sequences(sequences, dimension=config['dataset_size']):
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

    model = models.Sequential()
    model.add(layers.Dense(16, activation='relu', input_shape=(config['dataset_size'],)))
    model.add(layers.Dense(16, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    model.compile(optimizer=optimizers.RMSprop(lr=config['learning_rate']),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    x_val = x_train[:config['valid_size']]
    partial_x_train = x_train[config['valid_size']:]

    y_val = y_train[:config['valid_size']]
    partial_y_train = y_train[config['valid_size']:]

    history = model.fit(partial_x_train,
                        partial_y_train,
                        epochs=config['epochs'],
                        batch_size=config['batch_size'],
                        validation_data=(x_val, y_val))


if __name__ == '__main__':
    train()
