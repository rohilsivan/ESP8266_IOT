ESP8266 Forklift Safety System

A simple IoT safety system using ESP8266 to monitor forklift speed, detect driver presence, authenticate the operator, and send events to a laptop for logging and AI-based safety analysis.

Features

• Speed monitoring using Hall sensor
• Driver presence detection (IR)
• Face authentication on laptop
• Panic + Load confirmation buttons
• MQTT communication (ESP8266 ↔ Laptop)
• Dashboard + event logs
• AI anomaly detection for unsafe behavior

Hardware

ESP8266, Hall Sensor, IR Sensor, Panic Button, Load Button, Buzzer (LOW trigger), LED, Laptop webcam.

Core Workflow

IR detects driver → ESP sends event

Laptop verifies face

Authorized → LED ON

Hall sensor measures speed

Panic/Load events sent via MQTT

Laptop logs, displays, and analyzes data

AI flags anomalies and sends alerts back to ESP

Repository Contents

app.py – Dashboard + AI

pc_ai_recog_with_logging.py – Face authentication + logging

script.js & index.html – Dashboard UI

latest_log.csv.xlsx – Sample logs

Project report

Summary

A compact IoT + AI solution improving forklift safety through monitoring, authentication, and real-time alerts.
