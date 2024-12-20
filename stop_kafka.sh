cd
cd C:/kafka/

./bin/windows/kafka-server-stop.bat &
echo "Server stopped."
sleep 5

./bin/windows/zookeeper-server-stop.bat &
echo "Zookeeper stopped."