from keras.models import Sequential
from keras.layers import Dense, LSTM, Reshape
from keras.optimizers import Adam

def rnn(n_obs, n_action, n_hidden_layer=1, n_neuron_per_layer=16,
        activation='relu', loss='mse', learning_rate=0.01):
    """ RNN with LSTM layer"""
    model = Sequential()
    model.add(Dense(n_neuron_per_layer, input_dim=n_obs, activation=activation))
    model.add(Reshape((1, n_neuron_per_layer)))  # Reshape for LSTM input
    model.add(LSTM(n_neuron_per_layer, activation=activation))
    model.add(Dense(n_action, activation='linear'))

    optimizer = Adam(learning_rate=learning_rate)
    model.compile(loss=loss, optimizer=optimizer)
    return model

def mlp(n_obs, n_action, n_hidden_layer=1, n_neuron_per_layer=32,
        activation='relu', loss='mse'):
    """ A multi-layer perceptron. Adapted from WJie12's code."""
    print(n_action)
    model = Sequential()

    model.add(Dense(n_neuron_per_layer, input_dim=n_obs, activation=activation))
    for _ in range(n_hidden_layer):
        model.add(Dense(n_neuron_per_layer, activation=activation))
    model.add(Dense(n_action, activation='linear'))
    model.compile(loss=loss, optimizer=Adam())
    print(model.summary())
    return model