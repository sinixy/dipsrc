import os
import joblib
from typing import List, Callable

from config import settings
from model.opt import (
    equal_weighted_portfolio,
    min_variance_portfolio,
    min_variance_ledoitwolf,
    nco_portfolio,
)


class ModelRegistry:
    _pickers: dict[str, str] = {}
    _risk_map: dict[str, Callable] = {
        "mean_variance": min_variance_portfolio,
        "ledoit_wolf": min_variance_ledoitwolf,
        "nco": nco_portfolio,
        "equal": equal_weighted_portfolio,
    }

    @classmethod
    def scan(cls, dir_path: str):
        for fn in os.listdir(dir_path):
            if fn.endswith(".pkl"):
                name = fn[:-4]
                cls._pickers[name] = os.path.join(dir_path, fn)

    @classmethod
    def list_pickers(cls) -> List[str]:
        return list(cls._pickers.keys())

    @classmethod
    def get_picker(cls, name: str):
        path = cls._pickers.get(name)
        if not path:
            return None
        return joblib.load(path)

    @classmethod
    def list_risk_models(cls) -> List[str]:
        return list(cls._risk_map.keys())

    @classmethod
    def get_risk_fn(cls, name: str):
        return cls._risk_map.get(name)