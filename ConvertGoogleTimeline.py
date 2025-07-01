import json
import csv
import sys
import os
from datetime import datetime

# this code is dirty and not optimized - it was partially AI generated and modified by the author to extract date/time, lat and lng data from Google Timeline JSON exports to be used for rough location data for a stepcount dashboard from a Garmin smartwatch. This script provides only a csv of extracted data.

def make_reader(in_json):
    # open Timeline JSON, forcing utf-8 encoding.
    json_data = json.loads(open(in_json, encoding="utf-8").read())

    for segment in json_data['semanticSegments']:
        if 'visit' in segment:
            latitude, longitude = segment['visit']['topCandidate']['placeLocation']['latLng'].replace('°', '').split(', ')
            time = datetime.strptime(segment['startTime'], '%Y-%m-%dT%H:%M:%S.%f%z')
            yield [time.isoformat(), float(longitude), float(latitude)]

        if 'activity' in segment:
            for type in ['start', 'end']:
                latitude, longitude = segment['activity'][type]['latLng'].replace('°', '').split(', ')
                time = datetime.strptime(segment[f'{type}Time'], '%Y-%m-%dT%H:%M:%S.%f%z')
                yield [time.isoformat(), float(longitude), float(latitude)]

        if 'position' in segment:
            latitude, longitude = segment['LatLng'].replace('°', '').split(', ')
            time = datetime.strptime(segment['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')
            yield [time.isoformat(), float(longitude), float(latitude)]

        if 'timelinePath' in segment:
            # only catching the first loc on timelinePath entries
            for point in segment['timelinePath'][:1]:
                latitude, longitude = point['point'].replace('°', '').split(', ')
                time = datetime.strptime(point['time'], '%Y-%m-%dT%H:%M:%S.%f%z')
                yield [time.isoformat(), float(longitude), float(latitude)]

def getFullPath(inPath):
    if not os.path.isabs(inPath):
        script_path = os.path.abspath(__file__)
        path, file = os.path.split(script_path)
        inPath = os.path.join(path, inPath)
    return inPath

# define file names (relative path from script)
input_file = 'Timeline.json'
output_file = 'Timeline.csv'

# Read Json
reader = make_reader(input_file)
# Add the Headers
features = [['Time', 'Longitude', 'Latitude']]
for row in reader:
    features.append(row)

# Write CSV
writer = csv.writer(open(output_file, 'w', newline=''))
writer.writerows(features)
