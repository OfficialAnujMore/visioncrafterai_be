#!/bin/bash

# VisionCrafterAI Docker Manager Script
# This script helps manage common Docker operations

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_usage() {
    echo "VisionCrafterAI Docker Manager"
    echo ""
    echo "Usage: $0 {command}"
    echo ""
    echo "Commands:"
    echo "  up              - Start services (docker-compose up)"
    echo "  down            - Stop services (docker-compose down)"
    echo "  restart         - Restart services"
    echo "  clean           - Stop and remove containers, networks, volumes"
    echo "  clean-all       - Clean everything including orphans"
    echo "  logs            - View logs from all services"
    echo "  logs-api        - View logs from API service only"
    echo "  logs-db         - View logs from database service only"
    echo "  ps              - Show running containers"
    echo "  shell-api       - Open shell in API container"
    echo "  shell-db        - Open psql shell in database"
    echo "  status          - Check service status"
    echo ""
}

# Check if docker-compose is installed
check_docker() {
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: docker-compose is not installed${NC}"
        exit 1
    fi
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Command handlers
cmd_up() {
    print_info "Starting services..."
    docker-compose up -d
    print_status "Services started successfully"
    print_info "API: http://localhost:8000"
    print_info "Database: localhost:5432"
}

cmd_down() {
    print_info "Stopping services..."
    docker-compose down
    print_status "Services stopped"
}

cmd_restart() {
    print_info "Restarting services..."
    docker-compose restart
    print_status "Services restarted"
}

cmd_clean() {
    print_info "Cleaning up containers, networks, and volumes..."
    docker-compose down -v
    print_status "Cleanup complete"
}

cmd_clean_all() {
    print_info "Complete cleanup (including orphans)..."
    docker-compose down -v --remove-orphans
    docker volume prune -f
    print_status "Complete cleanup finished"
}

cmd_logs() {
    docker-compose logs -f
}

cmd_logs_api() {
    docker-compose logs -f visioncrafterai_be
}

cmd_logs_db() {
    docker-compose logs -f db
}

cmd_ps() {
    docker-compose ps
}

cmd_shell_api() {
    docker-compose exec visioncrafterai_be bash
}

cmd_shell_db() {
    docker-compose exec db psql -U postgres -d visioncrafter
}

cmd_status() {
    print_info "Checking service status..."
    docker-compose ps
}

# Main logic
check_docker

case "${1:-help}" in
    up)
        cmd_up
        ;;
    down)
        cmd_down
        ;;
    restart)
        cmd_restart
        ;;
    clean)
        cmd_clean
        ;;
    clean-all)
        cmd_clean_all
        ;;
    logs)
        cmd_logs
        ;;
    logs-api)
        cmd_logs_api
        ;;
    logs-db)
        cmd_logs_db
        ;;
    ps)
        cmd_ps
        ;;
    shell-api)
        cmd_shell_api
        ;;
    shell-db)
        cmd_shell_db
        ;;
    status)
        cmd_status
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        print_usage
        exit 1
        ;;
esac
