from pydantic import BaseModel
from application.routers.fact import _convert_model_to_dict


def test_convert_model_to_dict_single_model():
    model = BaseModel()
    result = _convert_model_to_dict(model)
    assert result == {}


def test_convert_model_to_dict_list_of_model():
    models = [BaseModel(), BaseModel(), BaseModel()]
    result = _convert_model_to_dict(models)
    assert result == [{}, {}, {}]
