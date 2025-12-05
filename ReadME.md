1. Restart container normally:
docker compose up

2. Background mode:
docker compose up -d

3. Stop:
docker-compose down --remove-orphans

4. Start an already existing stopped container:
docker start visioncrafterai_be_api

5. See logs:
docker logs -f visioncrafterai_be_api

6. The --no-cache flag forces Docker to rebuild the image fresh and install all dependencies from requirements.txt. 
docker-compose build --no-cache

7. Built table
docker-compose exec visioncrafterai_be bash -c "cd /app && python -m app.init_db"