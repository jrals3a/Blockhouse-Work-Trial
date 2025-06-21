# Abel Kahsai
# June 19, 2025

# Smart Order Router Backtest with Cont-Kukanov Model

## Overview
This project implements a backetest for a Smart Order Router (SQR) using the Cont & Kukanov cost model. It simulates market data using Kafka and bnchmarks the results against basic execution strategies.

## Requirements
- Python 3.8+
- Kafka 
- Java (for Kafka)
- pandas, numpy, kafka-python

## Installation
1. Install Kafka:
'''bash
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0