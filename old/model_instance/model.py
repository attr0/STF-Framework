import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
import keras
import numpy as np
import random

class Model:
    model: keras.Model
    input_shape: tuple

    def __init__(self, gpu_dev: str, gpu_mem_size: int, model_path: int) -> None:
        tf.get_logger().setLevel('ERROR')
        # init gpu
        if gpu_dev != "cpu":
            gpus = tf.config.list_physical_devices("GPU")
            if gpu_dev not in gpus:
                raise Exception(f"No gpu named: {gpu_dev}")

            # Restrict TensorFlow to only allocate {gpu_mem_size}Bytes of memory on the {gpu_dev}
            try:
                tf.config.set_logical_device_configuration(
                    gpu_dev,
                    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=gpu_mem_size) ],
                    )
            except RuntimeError as e:
                # Virtual devices must be set before GPUs have been initialized
                raise Exception(e)
            
        # load model
        self.model = keras.models.load_model(model_path, compile=False)
        self.model.compile(optimizer="SGD", loss=None, metrics=None)
        # save input shape
        self.input_shape = list(self.model.layers[0].input_shape[0])

    """
    Note, x_input must have an additional dimension for batch operation.
    Eg., the input is 36x128, then x_input should be 1x36x128
    """
    def predict(self, x_input: np.ndarray):
        for i in range(1, len(self.input_shape)):
            if x_input.shape[i] != self.input_shape[i]:
                raise Exception(f"Input shape is incorrect. Expect: {self.input_shape}")
        
        return self.model.predict(x_input)


if __name__ == "__main__":
    m = Model("cpu", 0, "./test/0.h5")
    print(f"input_shape: {m.input_shape}")
    
    input_data = []
    for i in range(12):
        v = []
        for i in range(326):
            v.append(random.random())
        input_data.append(v)
    input_data = np.array([input_data])

    output_data = m.predict(input_data)
    print(output_data)