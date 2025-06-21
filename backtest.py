# Abel Kahsai
# June 19, 2025
#import json 
#from kafka import KafkaConsumer
#from allocator import allocate 
#import time
#import numpy as np
#from datetime import datetime, timedelta

import json
from kafka import KafkaConsumer
from datetime import datetime, timedelta
from allocator import allocate  # Assuming this function is defined elsewhere


class Backtester:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'mock_l1_stream',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        self.order_size = 5000
        self.parameters = {
            'lambda_over': 0.5,
            'lambda_under': 0.5,
            'theta_queue': 0.2
        }

        # Tracking variables
        self.filled_shares = 0
        self.total_cash = 0
        self.executions = []

        # For benchmarks
        self.best_ask_results = {'total_cash': 0, 'avg_fill_px': 0}
        self.twap_results = {'total_cash': 0, 'avg_fill_px': 0}
        self.vwap_results = {'total_cash': 0, 'avg_fill_px': 0}

    def run_backtest(self):
        """Main backtest loop"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=9)  # Simulate for 9 minutes

        for message in self.consumer:
            current_time = datetime.now()
            if current_time > end_time:
                break

            snapshot = message.value
            venues = snapshot['venues']
            remaining = self.order_size - self.filled_shares

            if remaining > 0:
                split, _ = allocate(
                    remaining, venues,
                    self.parameters['lambda_over'],
                    self.parameters['lambda_under'],
                    self.parameters['theta_queue']
                )

                for i, qty in enumerate(split):
                    if qty > 0:
                        exe = min(qty, venues[i]['ask_sz'])
                        self.filled_shares += exe
                        self.total_cash += exe * venues[i]['ask_px']
                        self.executions.append({
                            'price': venues[i]['ask_px'],
                            'shares': exe,
                            'timestamp': snapshot['timestamp']
                        })

            self.run_benchmarks(venues, remaining)

        self.calculate_results()
        self.print_results()

    def run_benchmarks(self, venues, remaining):
        """Run benchmark strategies"""
        if remaining > 0:
            best_venue = min(venues, key=lambda x: x['ask_px'])
            exe = min(remaining, best_venue['ask_sz'])
            self.best_ask_results['total_cash'] += exe * best_venue['ask_px']
            self.best_ask_results['avg_fill_px'] += exe

    def calculate_results(self):
        """Calculate final metrics"""
        optimized = {
            'total_cash': self.total_cash,
            'avg_fill_px': self.total_cash / self.filled_shares if self.filled_shares > 0 else 0
        }

        baselines = {
            'best_ask': {
                'total_cash': self.best_ask_results['total_cash'],
                'avg_fill_px': self.best_ask_results['total_cash'] / self.order_size
            },
            'vwap': {
                'total_cash': self.total_cash,  # Placeholder
                'avg_fill_px': self.total_cash / self.filled_shares if self.filled_shares > 0 else 0
            }
        }

        savings = {}
        for strategy in baselines:
            base = baselines[strategy]['total_cash']
            savings[strategy] = (
                (base - optimized['total_cash']) / base * 10000 if base > 0 else 0.0
            )

        self.results = {
            'best_parameters': self.parameters,
            'optimized': optimized,
            'baselines': baselines,
            'savings_vs_baselines_bps': savings
        }

    def print_results(self):
        """Print final results in JSON format"""
        print(json.dumps(self.results, indent=2))


if __name__ == "__main__":
    backtester = Backtester()
    backtester.run_backtest()

        