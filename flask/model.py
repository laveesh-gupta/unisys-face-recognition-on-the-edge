import tensorflow as tf
from livenessmodel import get_liveness_model

# Get the liveness network
model = get_liveness_model()

# load weights into new model
model.load_weights("model/model.h5")
print("Loaded model from disk")
model.save("liveness_model.h5", save_format='h5')
print("Model saved in disk")
