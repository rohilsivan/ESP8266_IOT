from flask import Flask, render_template, jsonify
import pandas as pd
import os
import json

app = Flask(__name__)

# Path to your latest_log.csv
LOG_FILE = r"C:\Users\Rohil\Desktop\python\latest_log.csv"


def read_log():
    """Reads the CSV log file and formats data for frontend."""
    if not os.path.exists(LOG_FILE):
        return []

    try:
        df = pd.read_csv(LOG_FILE)

        # Rename to match frontend columns
        df = df.rename(columns={
            'ts': 'Timestamp',
            'event_type': 'Label',
            'details': 'Name'
        })

        # Try to parse JSON in details
        def parse_json_safe(value):
            try:
                return json.loads(value)
            except:
                return value

        df["Name"] = df["Name"].apply(parse_json_safe)

        # Return last 100 entries
        return df.tail(100).to_dict(orient="records")

    except Exception as e:
        print(f"[ERROR] Could not read log: {e}")
        return []


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/data')
def data():
    return jsonify(read_log())


@app.route('/favicon.ico')
def favicon():
    return '', 204


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
