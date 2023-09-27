from sklearn.base import BaseEstimator, TransformerMixin
from keras import Sequential

class KerasWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, num_epochs=100, verbose=0, **kwargs):
        self.num_epochs = num_epochs
        self.verbose = verbose
        self.model = Sequential(**kwargs)
        
    def fit(self, X, y):
        self.model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_squared_error'])
        self.model.fit(X, y, validation_split = 0.2 ,epochs=self.num_epochs, verbose=self.verbose)
        return self
    
    def transform(self, X):
        # Perform any necessary transformations
        return X
    
    def predict(self, X):
        return self.model.predict(X)
    
    
    def __getstate__(self):
        # Get the state to be pickled
        state = self.__dict__.copy()

        # Remove the unpicklable model object
        del state['model']

        return state

    def __setstate__(self, state):
        # Restore the state from the unpickled state
        self.__dict__.update(state)

        if 'model_weights' in state:
            self.model = Sequential()
            self.model.set_weights(state['model_weights'])
            self.model.compile(loss=state['model_loss'], optimizer=state['model_optimizer'], metrics=state['model_metrics'])
        else:
            self.model = None
