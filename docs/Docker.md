

# Build and run command


docker build -t jack:latest .

docker run -d -p 5000:5000 --env-file .env --name jack jack:latest

docker run -d -p 5555:42600 --env-file .env --name jack jack:latest



