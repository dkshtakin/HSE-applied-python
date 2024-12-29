from datetime import date
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from dateutil import relativedelta
import pandas as pd


def get_weather_prediction(df, y, pred_date):
    dow = pred_date.weekday()
    doy = pred_date.timetuple().tm_yday
    spring = range(80, 172)
    summer = range(172, 264)
    autumun = range(264, 355)
    if doy in spring:
        season = 'spring'
    elif doy in summer:
        season = 'summer'
    elif doy in autumun:
        season = 'autumun'
    else:
        season = 'winter'

    df_copy = pd.concat([pd.to_datetime(df['timestamp']).dt.dayofweek, df['season']], axis=1)

    ohe = OneHotEncoder(handle_unknown='ignore')
    ohe.fit(df_copy)
    df_ohe = ohe.transform(df_copy)
    lr = LinearRegression()
    lr.fit(df_ohe, y)

    data = {'timestamp': [dow], 'season': [season]}
    df_curr = pd.DataFrame.from_dict(data)
    y_pred = lr.predict(ohe.transform(df_curr))

    return y_pred[0]


def analyze_city(data, city):
    df = data[data['city'] == city]

    seasonal_mean = df.groupby('season')['temperature'].mean()
    seasonal_std = df.groupby('season')['temperature'].std()

    mean = df['temperature'].rolling(window=30).mean()
    std = df['temperature'].rolling(window=30).std()

    anomalies = df[(df['temperature'] > mean + 2 * std) | (df['temperature'] < mean - 2 * std)]

    seasonal_anomalies = df[(df['temperature'] > df['season'].apply(lambda x: seasonal_mean[x] + 2 * seasonal_std[x])) | (df['temperature'] < df['season'].apply(lambda x: seasonal_mean[x] - 2 * seasonal_std[x]))]

    df_max = df.loc[df['temperature'].idxmax()]
    df_min = df.loc[df['temperature'].idxmin()]

    prediction = get_weather_prediction(df, mean.fillna(mean.median()), date.today() + relativedelta.relativedelta(months=1))

    return df, df_max, df_min, mean, std, seasonal_mean, seasonal_std, anomalies, seasonal_anomalies, prediction
