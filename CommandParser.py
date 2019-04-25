import json
import os
import time

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
    # Add result string here
    if weather_result is not None:
        result = weather_result
    elif fact_result is not None:
        result = fact_result
    # add check result string for None

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
    # Add parser
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