# https://pypi.org/project/statsmodels/
# https://www.statsmodels.org/stable/install.html

from statsmodels.graphics.tsaplots import plot_pacf, plot_acf
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')


class Arima_Order:

    def __init__(self, data_series):
        self.data_series = data_series

    def get_d_value_and_ADF_test(self):
        # ----- Augmented Dickey-Fuller test ----- #
        # ----- p-value > 0.05: the data has a unit root and is non-stationary ----- #
        # ----- p-value <= 0.05: the data does not have a unit root and is stationary ----- #
        # ----- The more negative is ADF Statistic, the more likely we have a stationary dataset ----- #

        d = 0

        try:
            adf_test_results = adfuller(self.data_series.values)
        except:
            return d

        data_series_diff = self.data_series
        while adf_test_results[1] > 0.05 or d == 0:
            if d > 2:
                return 0
            d += 1
            # ----- make data stationary and drop NA values ----- #
            data_series_diff = data_series_diff.diff().dropna()
            try:
                data_series_diff_values = data_series_diff.values
                adf_result = adfuller(data_series_diff_values)
            except:
                d -= 1
                return d

        # print('ADF p-value:', adf_result[1])
        # print('d:', d)

        # ----- autocorrelation ----- #
        #plot_acf(data_diff)
        #plt.gcf().autofmt_xdate()
        #plt.show()
        # ----- partial autocorrelation ----- #
        #plot_pacf(data_diff)
        #plt.gcf().autofmt_xdate()
        #plt.show()

        return d

    def get_arima_best_order(self):

        d = Arima_Order.get_d_value_and_ADF_test(self)

        p_values = range(0, 5)
        q_values = range(0, 5)

        aic_dict = dict()

        for p in p_values:
            for d in range(d, 2):
                for q in q_values:
                    order = (p, d, q)

                    try:
                        arima_station_model = ARIMA(self.data_series, order).fit(disp=0)
                        aic = arima_station_model.aic
                        # print('ARIMA%s aic = %.5f' % (order, aic))

                        if [p, d, q] == [0, 0, 0] or [p, d, q] == [0, 1, 0] or [p, d, q] \
                                == [0, 1, 1]:
                            continue

                        if aic not in aic_dict:
                            aic_dict[aic] = order

                    except:
                        # print('ARIMA%s aic not defined' % (order,))
                        continue

        # if aic_dict is empty
        # it is impossible to create arima model for this data set
        if len(aic_dict) == 0:
            return 0

        min_val = min(aic_dict.keys())
        # print('min AIC value', min_val)
        # print('ARIMA model was created with order', aic_dict[min_val])

        # ----- ARIMA (p, d, q) ----- #
        p = aic_dict[min_val][0]
        q = aic_dict[min_val][2]

        return [p, d, q]
