ESP8266 Forklift Safety & Monitoring System

A smart industrial safety system built using the ESP8266, designed to monitor forklift usage, ensure driver authentication, track speed, detect unsafe behavior, and send data to a laptop/PC for analytics, AI anomaly detection, and visualization.

📌 Project Overview

This project provides a full IoT-based safety solution for forklifts by integrating real-time sensors, MQTT communication, and AI analytics.
The ESP8266 collects operational data, while a laptop performs face detection, logs all events, and runs anomaly analysis to detect unsafe behavior.

✨ Key Features

Real-time speed monitoring using a Hall Effect sensor

Driver presence detection using an IR sensor

Face authentication using laptop webcam

Emergency panic button detection

Load confirmation before vehicle operation

Live MQTT communication between ESP8266 → Laptop

Dashboard & event logs stored on PC

AI-based anomaly detection (Isolation Forest + rule-based)

Audible buzzer alerts for safety warnings

📡 System Architecture
[Hall Sensor] --->|
[IR Sensor] ------>|             MQTT            |--> [Dashboard UI]
[Panic Button] --->|--> ESP8266 ---- WiFi -----> |--> [AI Analytics]
[Load Button] ---->|                             |--> [Face Detection]
[Buzzer, LED] <----|                             |--> [Log File Storage]

🛠 Hardware Components

ESP8266 NodeMCU

Hall Effect Sensor (A3144) + magnet

IR presence sensor

Emergency (panic) button

Load-confirmation push button

Active buzzer (LOW trigger)

LED indicator

Laptop webcam

Laptop/PC for MQTT, dashboard, logging, AI

🔌 Hardware Connections
Hall Sensor

VCC → 3.3V

GND → GND

D0 → D7

IR Sensor

VCC → 3.3V

GND → GND

OUT → D2

Panic Button

One side → D3

Other side → GND

Load Button

One side → D6

Other side → GND

Buzzer

Signal → D5

VCC → 3.3V/5V

GND → GND

LED

Anode → 220Ω → D1

Cathode → GND

💻 Software Workflow

IR sensor detects driver → ESP sends entry event

Laptop performs face authentication

If authorized → MQTT → ESP turns LED ON

Hall sensor measures real-time speed

Load button & panic button events are transmitted

Laptop dashboard logs & displays the data

AI checks for anomalies (overspeeding, irregular patterns)

AI alerts sent back to ESP activate buzzer

📊 AI Model Used

Hybrid approach:

1. Rule-based checks

Overspeed

Missing load confirmation

Repeated panic alerts

2. Machine learning (Isolation Forest)

Learns normal driving patterns

Detects anomalies such as

sudden spikes in speed

frequent panic events

irregular sensor behavior
