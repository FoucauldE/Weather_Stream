from datetime import datetime

def convert_timestamp(timestamp_ms, include_time=False):
    # From unix timestamp (in ms) to human readable

    timestamp_sec = timestamp_ms / 1000
    dt = datetime.utcfromtimestamp(timestamp_sec)

    if include_time:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return dt.strftime('%Y-%m-%d')