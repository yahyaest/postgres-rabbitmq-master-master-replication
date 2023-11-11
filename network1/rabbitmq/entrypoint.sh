#!/bin/sh

rabbitmq-server &
# Function to check if RabbitMQ is up and running
wait_for_rabbitmq() {
    until rabbitmqctl node_health_check 2>&1 | grep -q "Health check passed"; do
        echo "RabbitMQ is not ready yet. Waiting..."
        sleep 5
    done
}

wait_for_rabbitmq  # Wait for RabbitMQ to start

echo "Stopping RabbitMQ..."
rabbitmqctl stop_app
sleep 10s
echo "Reseting RabbitMQ..."
rabbitmqctl reset
sleep 10s
echo "Starting RabbitMQ..."
rabbitmqctl start_app

tail -f /dev/null