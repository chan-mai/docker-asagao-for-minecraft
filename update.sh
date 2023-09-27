docker stop asagao-for-minecraft
docker rm --force asagao-for-minecraft
git pull origin master
docker compose up -d --build