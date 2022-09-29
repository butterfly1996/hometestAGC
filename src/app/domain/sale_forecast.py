import tensorflow as tf
from src.utils.singleton import SingletonMeta
from src.app.domain.model.forecast_result import ForecastResult
from config.config import get_config
import pickle
import numpy as np
model = None
vocabularies = None


class SaleForecastModel(metaclass=SingletonMeta):
    WINDOW_SIZE = 60
    def __init__(self):
        global model
        if model is None:
            model = tf.keras.models.load_model(get_config("model", "model_path"))
        global vocabularies
        if vocabularies is None:
            # with open("resources/vocabularies.pkl", "rb") as f:
            with open("/Users/lap02342/PycharmProjects/pod_foods/resources/vocabularies.pkl", "rb") as f:
                vocabularies = pickle.load(f)
        self.model = model

    @staticmethod
    def __preprocessing(request_info):
        return [
            np.array(np.where(vocabularies['PRODUCT_METADATA']==request_info.product_metadata)),
            np.array(np.where(vocabularies['STORE_TYPE']==request_info.store_type)),
            np.array(np.where(vocabularies['REGION_ID_x']==request_info.region_id)),
            np.array(np.where(vocabularies['BRAND_ID']==request_info.brand_id)),
            np.array(np.where(vocabularies['PRODUCT_ID']==str(request_info.product_id))),
            np.array(np.where(vocabularies['STORE_ID_x']==str(request_info.store_id))),
            np.array(np.where(vocabularies['STORE_SIZE']==request_info.store_size)),
            np.array([[request_info.quantities]])
        ]

    def forecast(self, request_info) -> ForecastResult:
        model_input = self.__preprocessing(request_info)
        # forecast_result = self.model(model_input)
        forecast_result = self.model(model_input)

        return forecast_result.numpy()[0][0][0]


if __name__ == '__main__':
    print("python shape: ", np.array([54]).shape)
    print("python shape: ", np.array([[0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,   0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0]]).shape)
    model = tf.keras.models.load_model("/Users/lap02342/PycharmProjects/pod_foods/resources/model.h5")
    print(model([
            np.array([54.]),
            np.array([4.]),
            np.array([2.]),
            np.array([370.]),
            np.array([4661.]),
            np.array([629.]),
            np.array([4.]),
            np.array([[[
                0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
                0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,   0.,  0.,  0.,  1.,  0.,  0.,
                0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0]]])]
    ))
