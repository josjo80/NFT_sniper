#https://discuss.tensorflow.org/t/generating-embeddings-from-one-hot-vectors/2978/3

import numpy as np
import tensorflow as tf 
from tensorflow.keras import backend as K


def np_onehot(x):
    x = np.asarray(x)
    n_values = np.max(x) + 1
    return np.eye(n_values)[x][:, 1:]


class OnehotEmbedding(tf.keras.layers.Layer):
    def __init__(self, Nembeddings, **kwargs):
        self.Nembeddings = Nembeddings
        super(OnehotEmbedding, self).__init__(**kwargs)

    def build(self, input_shape):
        # Create a trainable weight variable for this layer.
        self.kernel = self.add_weight(name='kernel',
                                      shape=(input_shape[2], self.Nembeddings),
                                      initializer='uniform',
                                      trainable=True)
        super(OnehotEmbedding, self).build(input_shape)  # Be sure to call this at the end

    def call(self, x):
        return K.dot(x, self.kernel)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1], self.Nembeddings)


def embed_onehot(x, embedding_dim=64):
    x = np.asarray(x)
    if len(x.shape) == 2:
        x = np.expand_dims(x, 0)
    shp = x.shape
    n_examples = shp[1]
    vocab_size = shp[2]
    model = tf.keras.layers.Embedding(
        vocab_size, embedding_dim, input_shape=(n_examples,)
    )
    return model(K.argmax(x, axis=-1))

def embed_integers(x, embedding_dim=64):
    # Create one-hot encoding
    one_hot = tf.keras.utils.to_categorical(x)

    shp = one_hot.shape
    n_examples = shp[1]
    vocab_size = shp[2]

    # Get embedding from model
    model = tf.keras.layers.Embedding(
        vocab_size, embedding_dim, input_shape=(n_examples,)
    )
    emb = model(K.argmax(one_hot, axis=-1))
    return emb

def get_pudgy_embeddings(pudgy_one_hot, embedding_dim=64):
    one_hot = np.expand_dims(pudgy_one_hot, 0) if len(pudgy_one_hot.shape) == 2 \
                                               else pudgy_one_hot
    input_shape = one_hot.shape
    model = OnehotEmbedding(embedding_dim, input_shape=input_shape)
    return model(one_hot)    
