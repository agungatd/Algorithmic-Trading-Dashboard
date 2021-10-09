#import library

import dash
from dash import dcc, html
import datetime as dt
import flask
import os
import pandas as pd
from pandas_datareader import data
import time 

# memanggil fungsi yang kita buat dari script helper kita
from helper import *

# untuk men-set up dashbaord
app = dash.Dash(
    __name__
)
server = app.server

# memasukan data
# df = pd.read_csv('bbca2020.csv')
symbol = 'BBCA.JK'
source = 'yahoo'
start_date = '2020-09-01'
end_date = '2021-09-01'

df = data.DataReader(symbol, source, start_date, end_date)
df['Stock'] = symbol
# mengatur pengaturan tampilan

# adding function to determine movement and volume different from a row before
def movement(df):
    df = df.reset_index()
    for i in range(1, len(df)):
        vol_bef = df.loc[i-1,'Volume']
        vol_now = df.loc[i,'Volume']
        vol_diff = vol_now - vol_bef

        if  (vol_diff >= 0):
            df.loc[i,'Movement'] = 'up'
        else:
            df.loc[i,'Movement'] = 'down'
        df.loc[i,'Volume_Difference'] = vol_diff
        # set for first row
        df.loc[0,'Movement'] = 'up'
        df.loc[0,'Volume_Difference'] = 0
    return df

df = movement(df)

app.layout = html.Div([ # pembungkus utama
    html.Div([
        # untuk judul
        html.H2('Algoritmic trading demo', 
                style={'display': 'inline',
                       'float': 'left',
                       'font-size': '2.65em',
                       'margin-left': '7px',
                       'font-weight': 'bolder',
                       'font-family': 'Product Sans',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0'
                       })
    ]),
    # dashboard core component untuk input dalam bentuk dropdown
    dcc.Dropdown(
        id='stock-ticker-input',
        options=[{'label': s[0], 'value': str(s[1])} 
                 for s in zip(df.Stock.unique(), df.Stock.unique())], # memunculkan semua emiten yang ada di dataframe kolom stock
        value=['BBCA.JK'], # value default yang masuk pertama kali
        multi=True # supaya bisa memasukan beberapa input 
    ),
    # untuk membuat tab 
    dcc.Tabs(id='dashboard-tabs', value='price-tab',children=[
        
        # tab pertama
		dcc.Tab(label='Candle Chart', value='price-tab',children=[
            html.Div(id='graphs') # menampilkan plot
        ]),
        # tab kedua
        dcc.Tab(label='Recomendation', value='change-tab',children=[
            html.Div(),
            html.H2('MACD Recomendation : '), 
            html.H2(id = 'macd_rec')

        ])
    ])
], className="container")

# fungsi untuk membuat bollinger band
def bbands(price, window_size=10, num_of_std=5):
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std  = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

#untuk menerima input dan mengeluarkan output
@app.callback(
    dash.dependencies.Output('graphs','children'),
    dash.dependencies.Output('macd_rec','children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph(tickers): #fungsi untuk membuat output 
    graphs = []

    if not tickers:
        graphs.append(html.H3(
            "Select a stock ticker.",
            style={'marginTop': 20, 'marginBottom': 20}
        ))
    else:
        for i, ticker in enumerate(tickers):

            dff = df[df['Stock'] == ticker]

            candlestick = {
                'x': dff['Date'],
                'open': dff['Open'],
                'high': dff['High'],
                'low': dff['Low'],
                'close': dff['Close'],
                'type': 'candlestick',
                'name': ticker,
                'legendgroup': ticker
            }
            bb_bands = bbands(dff.Close)
            bollinger_traces = [{
                'x': dff['Date'], 'y': y,
                'type': 'scatter', 'mode': 'lines',
                'line': {'width': 1},
                'hoverinfo': 'none',
                'legendgroup': ticker,
                'showlegend': True if i == 0 else False,
                'name': '{} - bollinger bands'.format(ticker)
            } for i, y in enumerate(bb_bands)]
            graphs.append(dcc.Graph(
                id=ticker,
                figure={
                    'data': [candlestick] + bollinger_traces,
                    'layout': {
                        'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                        'legend': {'x': 0}
                    }
                }
            ))

    macd_signal = macd(df)['macd_signal'][len(macd(df))-1]
    # saya mau ambil macd untuk hari paling terakhir 

    return graphs, macd_signal

# untuk selalu menjalankan script python

if __name__ == '__main__':
    app.run_server(debug=True)
