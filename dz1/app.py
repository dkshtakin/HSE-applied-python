import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from analyze import analyze_city


@st.cache_data
def load_data(file):
    return pd.read_csv(file)


def get_api_key():
    api_key = st.text_input("Openweather API key", "")
    return api_key


def get_current_weather(city, api_key):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={api_key}&units=metric'
    response = requests.get(url)
    x = response.json()
    if x['cod'] != 200:
        return x
    return x


st.title("Анализ данных с использованием Streamlit")
st.write("Это интерактивное приложение для анализа данных.")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

if uploaded_file is not None:
    data = load_data(uploaded_file)

    city = st.selectbox('Выберите город для отображения статистики', data['city'].value_counts().index)

    df, df_max, df_min, mean, std, seasonal_mean, seasonal_std, anomalies, seasonal_anomalies, prediction = analyze_city(data, city)

    fig, axs = plt.subplots(2)
    fig.set_figheight(10)
    fig.set_figwidth(20)

    line, = axs[0].plot(df['timestamp'], df['temperature'], linewidth=0.5, color='#b4dcff')
    line.set_label('Температура')

    line, = axs[0].plot(df['timestamp'], mean, color='#56b0ff')
    line.set_label('mean')

    line, = axs[0].plot(df['timestamp'], mean + 2 * std, color='#ffe0c5')
    line.set_label('mean +- 2 std')
    axs[0].plot(df['timestamp'], mean - 2 * std, color='#ffe0c5')

    line = axs[0].scatter(anomalies['timestamp'], anomalies['temperature'], color='#ff6e45', s=4)
    line.set_label('Аномалии')

    line = axs[0].scatter(df_max['timestamp'], df_max['temperature'], s=16, color='g')
    line = axs[0].scatter(df_min['timestamp'], df_min['temperature'], s=16, color='g')
    line.set_label('max/min')

    axs[0].title.set_text(f'Температура и скользящее среднее с отклонением в {city}')
    axs[0].set_xlabel('Дата')
    axs[0].set_ylabel('Температура')
    axs[0].legend()
    axs[0].plot()

    line, = axs[1].plot(df['timestamp'], df['temperature'], linewidth=0.5, color='#b4dcff')
    line.set_label('Температура')

    line, = axs[1].plot(df['timestamp'], df['season'].apply(lambda x: seasonal_mean[x]), color='#56b0ff')
    line.set_label('seasonal mean')

    line, = axs[1].plot(df['timestamp'], df['season'].apply(lambda x: seasonal_mean[x] + 2 * seasonal_std[x]), color='#ffe0c5')
    line, = axs[1].plot(df['timestamp'], df['season'].apply(lambda x: seasonal_mean[x] - 2 * seasonal_std[x]), color='#ffe0c5')
    line.set_label('seasonal mean +- 2 std')

    line = axs[1].scatter(seasonal_anomalies['timestamp'], seasonal_anomalies['temperature'], color='#ff6e45', s=4)
    line.set_label('Аномалии')

    axs[1].title.set_text(f'Температура и сезонный профиль с отклонением в {city}')
    axs[1].set_xlabel('Дата')
    axs[1].set_ylabel('Температура')
    axs[1].legend()
    axs[1].plot()

    axs[0].xaxis.set_major_locator(mdates.YearLocator())
    axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    axs[1].xaxis.set_major_locator(mdates.YearLocator())
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    st.pyplot(fig)

    st.text(f'Ожидаемая температура через месяц: {prediction:.2f}°')

    api_key = get_api_key()
    if api_key is not None and api_key:
        weather_response = get_current_weather(city, api_key)
        season = 'winter'

        if weather_response['cod'] != 200:
            st.text(f'Ошибка: {weather_response}')
        else:
            current_temperature = weather_response['main']['temp']
            st.write(f'Текущая температура в {city}: {current_temperature}')

            sm_high = seasonal_mean[season] + 2 * seasonal_std[season]
            sm_low = seasonal_mean[season] - 2 * seasonal_std[season]

            if current_temperature > sm_high:
                diff = current_temperature - sm_high
                st.write(f'Температура явялется аномальной, выше на {diff:.2f} чем обычно')
            elif current_temperature < sm_low:
                diff = sm_low - current_temperature
                st.write(f'Температура явялется аномальной, ниже на {diff:.2f} чем обычно')
            else:
                st.write('Температура не является аномальной.')
else:
    st.write("Пожалуйста, загрузите CSV-файл.")
