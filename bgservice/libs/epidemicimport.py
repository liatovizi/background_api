import logging
import csv
import datetime
import re

def parse_epidemic_csv(filepath):
    tracks = []
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='	')
        line = 0
        column_cnt = 0
        columns = {}
        for row in csv_reader:
            if line == 0:
                for (i, field) in zip(range(0, len(row)), row):
                    columns[field] = i
                    column_cnt = column_cnt + 1
            else:
                if 'StreamingId' not in columns:
                    raise Exception(f'Bad format: StreamingId column not found in epidemic CSV')
                if len(row) == 0:
                    continue
                if len(row) != column_cnt:
                    raise ValueError(f'Invalid field count on line {line + 1} in "{filepath}"')
                reldate = re.split('[T ]', row[columns['Releasedate']])[0].split('-')
                reldate = int(datetime.datetime(int(reldate[0]), int(reldate[1]), int(reldate[2])).timestamp() * 1000)
                tracks.append({
                    'streaming_id': row[columns['StreamingId']],
                    'track_id': row[columns['Id']],
                    'title': row[columns['Title']],
                    'metadata_tags': row[columns['MetadataTags']].split(', '),
                    'metadata_tags_str': row[columns['MetadataTags']],
                    'genres': [g.split(': ') for g in row[columns['Genres']].split(', ')],
                    'genres_str': row[columns['Genres']],
                    'moods': row[columns['Moods']].split(', '),
                    'moods_str': row[columns['Moods']],
                    'tempo_bpm': row[columns['TempoBPM']],
                    'energy_level': row[columns['EnergyLevel']],
                    'release_date': reldate,
                    'composer_id': row[columns['ComposerId']].split(',')[-1],
                    'composer_name': row[columns['ComposerName']].split(',')[-1],
                    'duration': row[columns['Duration']],
                    'sha256': row[columns['SHA256Sum']],
                    'url': row[columns['URL']],
                })
            line = line + 1
    return tracks
