import json
import re


def valid_achievements(achievements):
    if not isinstance(achievements, dict):
        print("Invalid: achievements is not a dictionary")
        return False
    if "planets" not in achievements:
        print("Invalid: 'planets' key missing in achievements")
        return False
    if not isinstance(achievements["planets"], list):
        print("Invalid: 'planets' is not a list")
        return False
    for planet in achievements["planets"]:
        if not isinstance(planet, dict):
            print("Invalid: planet entry is not a dictionary")
            return False
        if (
            "name" not in planet
            or "image" not in planet
            or "achievements" not in planet
        ):
            print("Invalid: planet missing 'name', 'image', or 'achievements' key")
            return False
        if not isinstance(planet["name"], str) or not isinstance(planet["image"], str):
            print("Invalid: planet 'name' or 'image' is not a string")
            return False
        if not isinstance(planet["achievements"], list):
            print("Invalid: planet 'achievements' is not a list")
            return False
        for achievement in planet["achievements"]:
            if not isinstance(achievement, dict):
                print("Invalid: achievement entry is not a dictionary")
                return False
            if (
                "name" not in achievement
                or "description" not in achievement
                or "type" not in achievement
            ):
                print(
                    "Invalid: achievement missing 'name', 'description', or 'type' key"
                )
                return False
            if not isinstance(achievement["name"], str) or not isinstance(
                achievement["description"], str
            ):
                print("Invalid: achievement 'name' or 'description' is not a string")
                return False
            if achievement["type"] not in ["progress", "game", "streak"]:
                print(
                    f"Invalid: achievement 'type' is not valid ({achievement.get('type')})"
                )
                return False
            if "data" not in achievement:
                print("Invalid: achievement missing 'data' key")
                return False
            if not isinstance(achievement["data"], dict):
                print("Invalid: achievement 'data' is not a dictionary")
                return False
            # Validate achievement["data"] based on achievement["type"]
            if achievement["type"] == "progress":
                if (
                    "startDate" not in achievement["data"]
                    or "endDate" not in achievement["data"]
                ):
                    print(
                        "Invalid: progress achievement missing 'startDate' or 'endDate'"
                    )
                    return False
                if not isinstance(
                    achievement["data"]["startDate"], str
                ) or not isinstance(achievement["data"]["endDate"], str):
                    print(
                        "Invalid: progress achievement 'startDate' or 'endDate' is not a string"
                    )
                    return False
                date_regex = r"^\d{4}-\d{2}-\d{2}$"
                if not re.match(
                    date_regex, achievement["data"]["startDate"]
                ) or not re.match(date_regex, achievement["data"]["endDate"]):
                    print(
                        "Invalid: progress achievement 'startDate' or 'endDate' does not match YYYY-MM-DD"
                    )
                    return False
                if "moneyToSave" not in achievement["data"] or not isinstance(
                    achievement["data"]["moneyToSave"], int
                ):
                    print(
                        "Invalid: progress achievement missing 'moneyToSave' or it is not an int"
                    )
                    return False
            elif achievement["type"] == "streak":
                if (
                    "startDate" not in achievement["data"]
                    or "endDate" not in achievement["data"]
                ):
                    print(
                        "Invalid: streak achievement missing 'startDate' or 'endDate'"
                    )
                    return False
                if not isinstance(
                    achievement["data"]["startDate"], str
                ) or not isinstance(achievement["data"]["endDate"], str):
                    print(
                        "Invalid: streak achievement 'startDate' or 'endDate' is not a string"
                    )
                    return False
                date_regex = r"^\d{4}-\d{2}-\d{2}$"
                if not re.match(
                    date_regex, achievement["data"]["startDate"]
                ) or not re.match(date_regex, achievement["data"]["endDate"]):
                    print(
                        "Invalid: streak achievement 'startDate' or 'endDate' does not match YYYY-MM-DD"
                    )
                    return False
                if "numConsecutiveDays" not in achievement["data"] or not isinstance(
                    achievement["data"]["numConsecutiveDays"], int
                ):
                    print(
                        "Invalid: streak achievement missing 'numConsecutiveDays' or it is not an int"
                    )
                    return False
                if "minimumStreakAmount" not in achievement["data"] or not isinstance(
                    achievement["data"]["minimumStreakAmount"], int
                ):
                    print(
                        "Invalid: streak achievement missing 'minimumStreakAmount' or it is not an int"
                    )
                    return False
                if "frequency" not in achievement["data"] or achievement["data"][
                    "frequency"
                ] not in ["daily", "weekly", "monthly"]:
                    print(
                        "Invalid: streak achievement missing 'frequency' or it is not valid"
                    )
                    return False
            elif achievement["type"] == "game":
                if (
                    "startDate" not in achievement["data"]
                    or "endDate" not in achievement["data"]
                ):
                    print("Invalid: game achievement missing 'startDate' or 'endDate'")
                    return False
                if not isinstance(
                    achievement["data"]["startDate"], str
                ) or not isinstance(achievement["data"]["endDate"], str):
                    print(
                        "Invalid: game achievement 'startDate' or 'endDate' is not a string"
                    )
                    return False
                date_regex = r"^\d{4}-\d{2}-\d{2}$"
                if not re.match(
                    date_regex, achievement["data"]["startDate"]
                ) or not re.match(date_regex, achievement["data"]["endDate"]):
                    print(
                        "Invalid: game achievement 'startDate' or 'endDate' does not match YYYY-MM-DD"
                    )
                    return False
    return True


with open("functions/checking.json", "r") as f:
    data = json.load(f)

print(valid_achievements(data))
