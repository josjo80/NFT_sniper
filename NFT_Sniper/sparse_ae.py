import tensorflow as tf

class SparseAutoEncoder:
    def __init__(self, input_dim):
        xavier=tf.keras.initializers.GlorotUniform()
        self.l1 = tf.keras.layers.Dense(
            input_dim,
            kernel_initializer=xavier,
            activation=tf.nn.sigmoid,
            input_shape=(input_dim,))
        self.l2 = tf.keras.layers.Dense(
            input_dim,
            kernel_initializer=xavier,
            activation=tf.nn.sigmoid)
        self.l3 = tf.keras.layers.Dense(
            input_dim,
            kernel_initializer=xavier,
            activation=tf.nn.sigmoid)
        self.train_op = tf.keras.optimizers.SGD(learning_rate=0.01)
        self.rho = 0.05
        self.alpha= 0.001
        self.beta = 4

    def kl_divergence(self, rho, rho_hat):
        return rho * tf.math.log(rho) - rho * tf.math.log(rho_hat) + (1 - rho) * \
            tf.math.log(1 - rho) - (1 - rho) * tf.math.log(1 - rho_hat)

    def run(self,X):
        out1=self.l1(X)
        out2=self.l2(out1)
        out3 = self.l3(out2)
        return out3
    def get_loss(self,X,Y):
        rho_hat = tf.reduce_mean(self.l1(X),axis=0)
        kl = self.kl_divergence(self.rho,rho_hat)

        out1=self.l1(X)
        out2=self.l2(out1)
        X_prime=self.l3(out2)
        diff = X-X_prime

        W1 = self.l1.variables[0]
        W2 = self.l2.variables[0]
        W3 = self.l3.variables[0]
        cost= 0.5*tf.reduce_mean(tf.reduce_sum(diff**2,axis=1))  \
        +0.5*self.alpha*(tf.nn.l2_loss(W1) + tf.nn.l2_loss(W2) + tf.nn.l2_loss(W3))   \
        +self.beta*tf.reduce_sum(kl)
        return cost

        return tf.math.square(boom2-Y)

    def get_grad(self,X,Y):
        with tf.GradientTape() as tape:
            tape.watch(self.l1.variables)
            tape.watch(self.l2.variables)
            tape.watch(self.l3.variables)
            L = self.get_loss(X,Y)
            g = tape.gradient(
                L, [self.l1.variables[0],
                    self.l1.variables[1],
                    self.l2.variables[0],
                    self.l2.variables[1],
                    self.l3.variables[0],
                    self.l3.variables[1]]
                )
        return g

    def network_learn(self,X,Y):
        g = self.get_grad(X,Y)
        self.train_op.apply_gradients(
            zip(g, [self.l1.variables[0],
                    self.l1.variables[1],
                    self.l2.variables[0],
                    self.l2.variables[1],
                    self.l3.variables[0],
                    self.l3.variables[1]])
                )


# SIMPLE
def simple_sparse_ae(dim, encoding_dim=32, optimizer='adadelta', loss='binary_crossentropy'):
    input_img = tf.keras.layers.Input(shape=(dim,))
    # add a dense layer with L1 activity regularizer
    encoded = tf.keras.layers.Dense(
        encoding_dim, activation='relu', 
        activity_regularizer=tf.keras.regularizers.l1(10e-5))(input_img)
    decoded = tf.keras.layers.Dense(dim, activation='sigmoid')(encoded)
    autoencoder = tf.keras.models.Model(input_img, decoded)
    autoencoder.compile(optimizer=optimizer, loss=loss)
    #autoencoder.fit(x_train, x_train, epochs=100, batch_size=256, shuffle=True, validation_data=(x_test, x_test))
    return autoencoder