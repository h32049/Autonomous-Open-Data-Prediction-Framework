import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA

from Program.Arima_Order import Arima_Order


class Arima_Main:

    def __init__(self, data_series, steps: int, optimize: bool):
        self.data_series = data_series
        self.steps = steps
        self.optimize = optimize

    @staticmethod
    def make_forecast(arima_model_order, data_series, steps):
        arima_model_station_data = ARIMA(data_series, order=arima_model_order).fit(disp=0)
        forecast_list = arima_model_station_data.forecast(steps=steps)[0].tolist()

        return forecast_list

    @staticmethod
    def get_forecast_accuracy_with_real_data(forecast, actual):
        rmse = np.mean((forecast - actual) ** 2) ** .5
        return rmse

    @staticmethod
    def get_steps_and_points_of_min_rmse(dataframe):
        min_rmse = dataframe.min().min()
        results = dataframe.isin([min_rmse])
        series_obj = results.any()
        column_names = list(series_obj[series_obj == True].index)
        for col in column_names:
            rows = list(results[col][results[col] == True].index)
            for row in rows:
                return [row, col]

    def get_all_possible_arima_models_with_data_points(self):
        if self.optimize:
            if len(self.data_series) <= 1000 + self.steps:
                optimize_point = len(self.data_series)
            else:
                optimize_point = 1010
        else:
            optimize_point = len(self.data_series)
        arima_models_order_and_data_points_dict = dict()
        last_point = len(self.data_series) - 1 - self.steps
        process = 0
        data_point_range = range(100, optimize_point, 10)
        data_point_range_len = len(range(100, optimize_point, 10))
        for data_points in data_point_range:
            process += 1
            first_point = last_point - data_points
            if first_point < 0:
                break
            data_series_copy = self.data_series[first_point:last_point].copy()
            order = Arima_Order(data_series_copy).get_arima_best_order()
            if order == 0:
                # print('ARIMA model was NOT DEFINED for', len(data_series_copy), 'observation points')
                print('{:.0f}%'.format(process / data_point_range_len * 100))
                continue
            else:
                # print('ARIMA model with order', order, 'for', len(data_series_copy), 'observation points')
                print('{:.0f}%'.format(process / data_point_range_len * 100))
                arima_models_order_and_data_points_dict[data_points] = order

        return arima_models_order_and_data_points_dict

    def get_arima_forecast(self):

        arima_models_order_and_data_points_dict = Arima_Main.get_all_possible_arima_models_with_data_points(self)

        # dataframe of data points, steps and RMSE
        rmse_df = pd.DataFrame()

        rmse_dict = dict()
        last_point = len(self.data_series) - 1 - self.steps

        for data_points, order in arima_models_order_and_data_points_dict.items():

            first_point = last_point - data_points
            data_series_copy = self.data_series[first_point:last_point].copy()

            # ----- Make copy of real data for comparing with forecast ----- #
            station_data_copy_with_steps = self.data_series[last_point - 1:last_point - 1 + self.steps].copy()

            forecast_list = Arima_Main.make_forecast(order, data_series_copy, self.steps)

            rmse = Arima_Main.get_forecast_accuracy_with_real_data(forecast_list, station_data_copy_with_steps.values)
            rmse_dict[data_points] = rmse

        rmse_series = pd.Series(rmse_dict)
        rmse_df[str(self.steps)] = rmse_series

        rmse_df.reset_index(inplace=True)
        rmse_df['order'] = arima_models_order_and_data_points_dict.values()
        rmse_df.rename(columns={'index': 'points'}, inplace=True)
        rmse_df.set_index(['points', 'order'], inplace=True)

        results = Arima_Main.get_steps_and_points_of_min_rmse(rmse_df)

        data_points_for_forecast = results[0][0]

        steps = int(results[1])

        data_series_copy = self.data_series[- data_points_for_forecast:].copy()

        arima_model_order = Arima_Order(data_series_copy).get_arima_best_order()

        forecast = Arima_Main.make_forecast(arima_model_order, data_series_copy, steps)

        return [data_points_for_forecast, arima_model_order, steps, forecast]