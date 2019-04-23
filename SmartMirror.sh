#!/bin/bash
python weatherApi.py &
python PygameMain.py &
python FacialRecognition.py &
python WeatherParser.py &