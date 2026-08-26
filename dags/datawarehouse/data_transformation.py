
from datetime import datetime, timedelta

""" sample data for testing{
        "video_id": "lM7zWJRrRtg",
        "publishedAt": "2026-07-31T15:00:34Z",
        "title": "Why dict[str, Any] Slowly Destroys Your Code",
        "duration": "PT20M47S",
        "viewCount": "23537",
        "likeCount": "1010",
        "commentCount": "98"
    },"""


def parse_duration(duration_str: str) -> timedelta:

    duration_str = duration_str.replace("P", "").replace("T", "")
    components = ['D', 'H', 'M', 'S']
    values = {'D': 0, 'H': 0, 'M': 0, 'S': 0}  # days, hours, minutes, seconds

    for component in components:
        if component in duration_str:
            value, duration_str = duration_str.split(component)
            values[component] = int(value)

    total_duration = timedelta(days=values['D'], hours=values['H'], minutes=values['M'], seconds=values['S'])
    return total_duration


def transform_data(row: dict) -> dict:
    """
    Transforms the input data row by parsing the duration and converting it to a timedelta object.
    Args:
        row (dict): A dictionary representing a row of data.
    Returns:
        dict: A transformed dictionary with the duration converted to a timedelta object.
    """
    transformed_row = row.copy()
    duration_td = parse_duration(row['duration'])  # Parse the duration string and convert it to a timedelta object

    # Parse the duration string and convert it to a timedelta object
    transformed_row['Duration'] = (datetime.min + duration_td).time()  # Convert the timedelta to a time object
    transformed_row['Video_Type'] = "Shorts" if duration_td.total_seconds() < timedelta(minutes=1).total_seconds() else "Normal"  # Determine the video type based on duration

    return transformed_row  # Return the transformed row
