import re
import pandas as pd
from dateutil import parser


def android_preprocess(data):
    patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s(?:AM|PM|am|pm)?(?:\s\w{3,4})?\s-\s',
        r"\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} ?(?:AM|PM)? - ",
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM|am|pm)?\s-\s'
        # Add more patterns if needed
    ]

    messages = []
    dates = []

    # Apply each pattern
    for pattern in patterns:
        messages_temp = re.split(pattern, data)
        dates_temp = re.findall(pattern, data)

        # Combine results, excluding the first element (empty before the first match)
        if messages_temp and dates_temp:
            messages.extend(messages_temp[1:])
            dates.extend(dates_temp)

    # Create DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Parse dates using dateutil.parser
    df['message_date'] = df['message_date'].apply(lambda x: parser.parse(x.strip(' - ')))

    # Rename the column
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Ensure the 'date' column is a datetime object
    df['date'] = pd.to_datetime(df['date'])

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df


def ios_preprocess(data):
    # Define the pattern to split messages and extract dates, including AM/PM
    pattern = r'\[\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{1,2}:\d{1,2}\s(?:AM|PM)]'

    # Split messages and find dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create a DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Parse dates using dateutil.parser and ensure they are datetime objects
    df['message_date'] = df['message_date'].apply(lambda x: parser.parse(x.strip('[] ')))

    # Rename the column
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Ensure the 'date' column is a datetime object
    df['date'] = pd.to_datetime(df['date'])

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df["user"] = df["user"].str.lstrip()
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
