import json
import os
import time
import subprocess
import re
import picamera

from FileSettings import INPUT_STRING_FILE, OUTPUT_STRING_FILE, WEATHER_FILE
from WeatherJSON import weather_hook


def count(words: list, string: str) -> int:
    """
    Counts how many of the words in words is in the string

    :param words:
    :param string:
    """
    count = 0
    for word in words:
        if word in string:
            count += 1
    return count


class SettingsParser:
    settingsWords = ["volume down", "volume up", "volume level", "mute", "add new user", "shut down"]
    def parse(self, string: str):
        if count(self.settingsWords, string > 1):
            return "You may only change one setting at a time"
        elif "volume down" in string.lower():
            command = "amixer -q sset Master 10%-"
            process = subprocess.Popen(command.split(), stdout = subprocess.PIPE)
            #method to decrease volume by ten notches
        elif "volume up" in string.lower():
            command = "amixer -q sset Master 10%+"
            process = subprocess.Popen(command.split(), stdout = subprocess.PIPE)
            #method to increase volume by ten notches
        elif "volume level" in string.lower():
            #regex to find every number in string
            arr = re.findall(r'[0-9]+', str)
            #makes most sense to use the first number for desired volume
            newLevel = arr[0]
            if newLevel < 0 or newLevel > 100:
                #fail if volume is out of bounds
                return "invalid volume"
            else:
                command = "amixer sset Master {}%".format(str(newLevel))
                process = subprocess.Popen(command.split(), stdout = subprocess.PIPE)
                #Set speaker volume to newLevel value
        elif "mute" in string.lower():
            command = "amixer sset Master 0%"
            process = subprocess.Popen(command.split(), stdout = subprocess.PIPE)
        elif "shut down" in string.lower():
            #Try changing the command contents if this doesn't work. 
            command = "sudo shutdown"
            process = subprocess.Popen(command.split(), stdout = subprocess.PIPE)
            return "shutting down"
        
            

class WeatherParser:
    # The word that must be in the string for weather parser to parse
    weather_file = WEATHER_FILE
    activation_string = "weather"
    current_weather_strings = ["current", "outside", "now", "current", "today"]
    tomorrow_weather_strings = ["tomorrow", "a day", "one"]
    week_weather_strings = ["week", "weekend"]

    def __init__(self):
        super().__init__()

    def parse(self, string: str):
        TOLERANCE = 1
        if self.activation_string in string.lower():
            with open(self.weather_file, 'r') as fin:
                weather = json.load(fin, object_hook=weather_hook)
            if count(self.current_weather_strings, string) >= TOLERANCE:
                return weather['current']['summary']
            elif count(self.tomorrow_weather_strings, string) >= TOLERANCE:
                return weather['forecast'][0]['summary']
            elif count(self.week_weather_strings, string) >= TOLERANCE:
                return weather['week_summary']
            else:
                return None


class FactParser:
    capital_of_france_strings = ["capital", "france"]
    colorado_state_rock_strings = ["colorado", "state", "rock"]
    tiger_woods_strings = ['who', 'tiger', 'woods']

    def __init__(self):
        super().__init__()

    def parse(self, string: str):
        if count(self.capital_of_france_strings, string) >= 2:
            return 'The capital of france is paris'
        elif count(self.colorado_state_rock_strings, string) >= 3:
            return 'The state rock for colorado is basalite'
        elif count(self.tiger_woods_strings, string) >= 3:
            return 'Tiger Woods is a professional golfer.'
        else:
            return None


def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


def parse_string(line):
    result = None
    weather_result = weather_parser.parse(line)
    fact_result = fact_parser.parse(line)
    settings_result = settings_parser.parse(line)
    if weather_result is not None:
        result = weather_result
    elif fact_result is not None:
        result = fact_result
    elif settings_result is not None:
        result = settings_result
    if result is not None:
        with open(OUTPUT_STRING_FILE, "a") as fout:
            fout.write(result + "\n")
            return True
    return False


if __name__ == "__main__":
    file_name = INPUT_STRING_FILE
    activation_string = "mirror"
    delay = 10
    sentence_lookahead = 1
    weather_parser = WeatherParser()
    fact_parser = FactParser()
    settings_parser = SettingsParser()
    while True:
        # read file into list
        lines = [line.rstrip() for line in open(file_name)]
        # clear the current file
        open(file_name, 'w').close()
        # parse each line
        for i, line in enumerate(lines):
            # is the activation word in the string attempt to parse the string
            if activation_string in line and not parse_string(line):
                # if the line had the activation but was not parseable try current and next line
                if i < len(lines) - sentence_lookahead:
                    for j in range(1, sentence_lookahead + 1):
                        line += " " + lines[i + j]
                    parse_string(line)
                # if a theoretically parseable string is at end of file write that line to the file
                else:
                    # if file is empty overwrite with line
                    if os.stat(file_name).st_size == 0:
                        with open(file_name, "w") as fout:
                            fout.write(line)
                    else:
                        line_prepender(file_name, line)
        time.sleep(delay)
