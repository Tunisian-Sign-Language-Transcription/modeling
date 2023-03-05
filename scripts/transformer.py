from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
import settings as s
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import MultiHeadAttention, LayerNormalization, Dropout, Layer
from tensorflow.keras.layers import Embedding, Input, GlobalAveragePooling1D, Dense
from tensorflow.keras.datasets import imdb
from tensorflow.keras.models import Sequential, Model
import numpy as np
import warnings
import os
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

from data_preparation import load_data


class TransformerBlock(Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = Sequential(
            [
                Dense(ff_dim, activation="relu"),
                Dense(embed_dim), ]
        )
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)

        self.dropout1 = Dropout(rate)
        self.dropout2 = Dropout(rate)
        

    def call(self, inputs, training):

        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)

        return self.layernorm2(out1 + ffn_output)


class PositionEmbedding(Layer):
    def __init__(self, maxlen, embed_dim):
        super(PositionEmbedding, self).__init__()
        self.pos_emb = Embedding(input_dim=maxlen, output_dim=embed_dim)

    def call(self, x):
        maxlen = s.MAXLEN
        positions = tf.range(start=0, limit=maxlen, delta=1)
        # vector of 30 integers -> tensor of shape (30, 258)
        positions = self.pos_emb(positions)

        return x + positions


def build_transformer_pose_model():
    embedding_layer = PositionEmbedding(maxlen=s.MAXLEN, embed_dim=s.EMBED_DIM)
    transformer_block = TransformerBlock(s.EMBED_DIM, s.NUM_HEADS, s.FF_DIM)

    inputs = Input(shape=(s.MAXLEN,s.EMBED_DIM))
    x = embedding_layer(inputs)
    x = transformer_block(x)
    x = GlobalAveragePooling1D()(x)
    x = Dropout(0.1)(x)
    x = Dense(20, activation="relu")(x)
    x = Dropout(0.1)(x)
    outputs = Dense(s.ACTIONS.shape[0], activation="softmax")(x)

    model = Model(inputs=inputs, outputs=outputs)
    return model

def train_transformer_model(model_name):
    sequences, labels = load_data()

    X = np.array(sequences)
    y = np.array(labels)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05)
    model = build_transformer_pose_model()

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    history = model.fit(
        X_train,
        y_train,
        #batch_size=64,
        epochs=s.TRANSFORMER_EPOCHS,
        validation_data=(X_test, y_test)
    )
    
    model.save_weights(os.path.join(s.MODELS_DIR, f'{model_name}.h5'))




    
    





    

    

    

    
