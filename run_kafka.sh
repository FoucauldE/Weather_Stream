#!/bin/bash

cd C:/kafka/

echo "Starting zookeeper..."
./bin/windows/zookeeper-server-start.bat ./config/zookeeper.properties &
sleep 5

echo "Starting server..."
./bin/windows/kafka-server-start.bat ./config/server.properties &
sleep 5 

echo "Creating topic..."
./bin/windows/kafka-topics.bat --create --topic weather-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092

echo "Katka setup complete."
