from flask import Flask, render_template, request, Response
import pandas as pd
import pickle

app = Flask(__name__)

kit_items_df = pd.read_csv('final_mape_kits.csv')
kit_items = kit_items_df.columns[1:].tolist()  


def load_model(kit_item):
    filename = f'arima_models/{kit_item}_arima_model.pkl'
    with open(filename, 'rb') as file:
        return pickle.load(file)


def forecast(kit_item, months):
    model = load_model(kit_item)

    forecast_data = model.forecast(steps=months)  
    forecast_dates = pd.date_range(start='2024-1-1', periods=months, freq='M') 
    forecast_series = pd.DataFrame(forecast_data)
    forecast_dates=forecast_dates.strftime('%Y-%m-%d')
    forecasts=forecast_series.set_index(forecast_dates)
    forecasts = pd.DataFrame({'Date': forecast_dates, 'Forecast': forecast_data}) 
    return forecasts

@app.route('/')
def index():
    return render_template('index.html', kit_items=kit_items)

@app.route('/forecast', methods=['POST'])
def do_forecast():
    kit_item = request.form['kit_item']
    months = int(request.form['months'])
    forecast_data = forecast(kit_item, months)
    
    return render_template('result.html', kit_item=kit_item, months=months, forecast=forecast_data)

@app.route('/download_forecast', methods=['GET'])
def download_forecast():
    kit_item = request.args.get('kit_item')
    months = int(request.args.get('months'))
    forecast_data = forecast(kit_item, months)
    
   
    csv_output = forecast_data.to_csv(index=False)
    

    response = Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-disposition":
                 f"attachment; filename={kit_item}_forecast.csv"})
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
