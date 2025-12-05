# Docker Setup & Troubleshooting Guide

## Quick Start

### Using the docker-manager script (Recommended)
```bash
# Start services
./docker-manager.sh up

# View status
./docker-manager.sh status

# View logs
./docker-manager.sh logs

# Stop services
./docker-manager.sh down

# Complete cleanup
./docker-manager.sh clean-all
```

### Using docker-compose directly
```bash
# Start services in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

## Available Services

- **API**: `http://localhost:8000`
- **Database**: `localhost:5432`
  - Username: `postgres`
  - Password: `postgres`
  - Database: `visioncrafter`

## Connecting with pgAdmin Desktop

1. Open pgAdmin Desktop
2. Create a new server connection:
   - **Host name/address**: `localhost`
   - **Port**: `5432`
   - **Username**: `postgres`
   - **Password**: `postgres`
   - **Database**: `visioncrafter`

## Common Issues & Solutions

### Issue: "Port 5432 is already in use"

**Cause**: Local PostgreSQL or another process is using port 5432

**Solutions**:

1. **Check what's using the port**:
   ```bash
   lsof -i :5432
   ```

2. **Kill the process** (if it's local PostgreSQL):
   ```bash
   sudo kill -9 <PID>
   ```

3. **Or stop local PostgreSQL**:
   ```bash
   # macOS
   brew services stop postgresql@15
   
   # Linux
   sudo systemctl stop postgresql
   ```

4. **Or use a different port** in docker-compose.yml:
   ```yaml
   ports:
     - "5433:5432"  # Use 5433 instead of 5432
   ```

### Issue: "Port 8000 is already in use"

**Cause**: Another service is using port 8000

**Solution**:
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or modify docker-compose.yml to use a different port
# Change: "8000:8000" to "8001:8000"
```

### Issue: Containers keep stopping unexpectedly

**Cause**: Database not ready when API tries to connect

**Solution**: Already fixed! Updated docker-compose.yml with proper health checks and dependency configuration.

### Issue: "Orphan containers" warning

**Solution**:
```bash
./docker-manager.sh clean-all
# Or
docker-compose down -v --remove-orphans
```

## Complete Cleanup

To completely reset everything:

```bash
# Using the script
./docker-manager.sh clean-all

# Or manually
docker-compose down -v --remove-orphans
docker volume prune -f
docker network prune -f
```

## Environment Variables

All environment variables are configured with sensible defaults. To customize:

1. Create a `.env` file in the project root
2. Add your custom values
3. Restart docker-compose

**Example .env file**:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=visioncrafter
POSTGRES_PORT=5432
```

## Useful Commands

```bash
# View container status
docker-compose ps

# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f db      # Database logs
docker-compose logs -f visioncrafterai_be  # API logs

# Execute command in container
docker-compose exec db psql -U postgres -d visioncrafter  # Database shell
docker-compose exec visioncrafterai_be bash  # API shell

# Rebuild containers
docker-compose build

# Restart services
docker-compose restart
```

## Development Workflow

1. **Start services**:
   ```bash
   ./docker-manager.sh up
   ```

2. **Check status**:
   ```bash
   ./docker-manager.sh status
   ```

3. **View logs**:
   ```bash
   ./docker-manager.sh logs
   ```

4. **Connect to database**:
   ```bash
   ./docker-manager.sh shell-db
   ```

5. **Stop services**:
   ```bash
   ./docker-manager.sh down
   ```

## macOS Specific Notes

- Make sure Docker Desktop is running before executing docker commands
- If you have local PostgreSQL installed, it may conflict with Docker PostgreSQL
- Use `brew services list` to check running services
- Use `brew services stop postgresql@15` to stop local PostgreSQL

## Docker Desktop Resources

To improve performance, increase Docker Desktop resources:
1. Open Docker Desktop
2. Settings → Resources
3. Increase CPU and Memory allocation
4. Click "Apply & Restart"
