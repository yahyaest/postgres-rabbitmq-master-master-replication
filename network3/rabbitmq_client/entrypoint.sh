#!/bin/sh

python scripts/producer.py &
python scripts/consumer.py &

tail -f /dev/null