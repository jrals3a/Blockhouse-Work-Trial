# Abel Kahsai
# June 19, 2025

# import json, time, datetime, KafkaProducer, and pd
import json
import time
from datetime import datetime
from kafka import KafkaProducer
import pandas as pd

# define parse_csv_to_snapshots
def parse_csv_to_snapshots(file_path):
    """Parse CSV file into venue snapshots"""
    df = pd.read_csv(file_path)

    # make sure timestamp is converted to datetime
    df['ts_event'] = pd.to_datetime(df['ts_event'])

    # make sure publisher and timestamp are grouped
    snapshots = []
    for ts, group in df.groupby('ts_event'):
        venues = []
        for _, row in group.iterrows():
            venues.append({
                'publisher_id': row['publisher_id'],
                'ask': row['ask_px_00'],
                'ask_size': row['ask_sz_00'],
                'fee': 0.001, #Example fee
                'rebate': 0.0005 #Example rebate
            })
        snapshots.append({'timestamp': ts.isoformat(), 'venues': venues})
    return snapshots

# define produce_to_kafka
def produce_to_kafka(snapshots, topic='mock_l1_stream'):
    """Produce snapshots to Kafka topic"""
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer = lambda v: json.dumps(v).encode('utf-8')
    )

    prev_time = None
    for snapshot in snapshots:
        current_time = datetime.fromisoformat(snapshot['timestamp'])

        # real-time 
        if prev_time:
            time_diff = (current_time - prev_time).total_seconds()
            time.sleep(time_diff)
        prev_time = current_time

        producer.send(topic, value = snapshot)
    producer.flush()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python kafka_producer.py <csv_file>")
        sys.exit(1)

    snapshots = parse_csv_to_snapshots(sys.argv[1])
    produce_to_kafka(snapshots)