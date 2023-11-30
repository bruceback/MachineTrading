import autots.models.base
import pandas as pd
from autots import AutoTS


def get_prediction(ts: pd.DataFrame, date_col: str, target_col: str) -> autots.models.base.PredictionObject:
    model = AutoTS(forecast_length=7, frequency="infer", model_list="superfast",
                   ensemble='simple', drop_data_older_than_periods=365, verbose=0)
    model.fit(ts, date_col=date_col, value_col=target_col, id_col=None)

    return model.predict()
