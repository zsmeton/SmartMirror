import json
import os
import time

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
    weather_file = "weather.txt"
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


def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


def parse_string(line):
    if "mirror" in line:
        weather_result = weather_parser.parse(line)
        if weather_result is not None:
            with open("say.txt", "a") as fout:
                fout.write(weather_result + "\n")
                return True
        return False


if __name__ == "__main__":
    file_name = "microphone.txt"
    activation_string = "mirror"
    delay = 10
    sentence_lookahead = 1
    weather_parser = WeatherParser()
    # face_recognition_parser = ()
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
