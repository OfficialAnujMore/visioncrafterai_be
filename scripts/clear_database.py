"""
Database Cleanup Script for Development
Clears all data from specified tables or entire database

Usage (Docker - Recommended):
    docker exec -it visioncrafterai_api python scripts/clear_database.py --all
    docker exec -it visioncrafterai_api python scripts/clear_database.py --all --yes
    docker exec -it visioncrafterai_api python scripts/clear_database.py --tables user
    docker exec -it visioncrafterai_api python scripts/clear_database.py --tables user refreshtoken
    
    # Quick reset shortcut:
    docker exec -it visioncrafterai_api bash scripts/reset_database.sh

Usage (Local - requires DATABASE_URL with localhost):
    python scripts/clear_database.py --all
    python scripts/clear_database.py --tables user --yes
"""
import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to Python path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import engine
from app.models import User, RefreshToken


# Map of table names to models
TABLE_MODELS = {
    "user": User,
    "refreshtoken": RefreshToken,
}


async def clear_table(table_name: str, session: AsyncSession) -> int:
    """
    Clear all records from a specific table
    
    Args:
        table_name: Name of the table to clear
        session: Database session
        
    Returns:
        Number of records deleted
    """
    if table_name not in TABLE_MODELS:
        print(f"❌ Unknown table: {table_name}")
        print(f"Available tables: {', '.join(TABLE_MODELS.keys())}")
        return 0
    
    model = TABLE_MODELS[table_name]
    
    try:
        # Get count before deletion
        count_stmt = select(model)
        result = await session.exec(count_stmt)
        records = result.all()
        count = len(records)
        
        if count == 0:
            print(f"⚠️  Table '{table_name}' is already empty")
            return 0
        
        # Delete all records
        delete_stmt = delete(model)
        await session.exec(delete_stmt)
        await session.commit()
        
        print(f"✅ Cleared {count} records from table '{table_name}'")
        return count
        
    except Exception as e:
        await session.rollback()
        print(f"❌ Error clearing table '{table_name}': {str(e)}")
        return 0


async def clear_all_tables(session: AsyncSession) -> dict:
    """
    Clear all tables in the database
    
    Args:
        session: Database session
        
    Returns:
        Dictionary with table names and counts deleted
    """
    results = {}
    
    # Order matters - delete child tables first (foreign key constraints)
    ordered_tables = ["refreshtoken", "user"]
    
    for table_name in ordered_tables:
        count = await clear_table(table_name, session)
        results[table_name] = count
    
    return results


def confirm_action(message: str) -> bool:
    """
    Ask user for confirmation
    
    Args:
        message: Confirmation message to display
        
    Returns:
        True if user confirms, False otherwise
    """
    response = input(f"{message} (yes/no): ").lower().strip()
    return response in ['yes', 'y']


async def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Clear database tables for development/testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples (Docker - Recommended):
  docker exec -it visioncrafterai_api python scripts/clear_database.py --all
  docker exec -it visioncrafterai_api python scripts/clear_database.py --all --yes
  docker exec -it visioncrafterai_api python scripts/clear_database.py --tables user
  docker exec -it visioncrafterai_api bash scripts/reset_database.sh
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clear all tables in the database'
    )
    
    parser.add_argument(
        '--tables',
        nargs='+',
        help=f'Specific tables to clear. Available: {", ".join(TABLE_MODELS.keys())}'
    )
    
    parser.add_argument(
        '--yes',
        '-y',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.tables:
        parser.print_help()
        print("\n❌ Error: You must specify either --all or --tables")
        sys.exit(1)
    
    if args.all and args.tables:
        print("❌ Error: Cannot use --all and --tables together")
        sys.exit(1)
    
    # Show warning
    print("\n" + "="*60)
    print("⚠️  WARNING: DATABASE CLEANUP OPERATION")
    print("="*60)
    
    if args.all:
        print("📋 Action: Clear ALL tables")
        print(f"📊 Tables: {', '.join(TABLE_MODELS.keys())}")
    else:
        print(f"📋 Action: Clear specific tables")
        print(f"📊 Tables: {', '.join(args.tables)}")
    
    print("="*60 + "\n")
    
    # Confirm action
    if not args.yes:
        if not confirm_action("🚨 This will DELETE ALL DATA from the specified tables. Continue?"):
            print("❌ Operation cancelled")
            sys.exit(0)
    
    print("\n🔄 Starting database cleanup...\n")
    
    # Execute cleanup
    async with AsyncSession(engine) as session:
        if args.all:
            results = await clear_all_tables(session)
            total = sum(results.values())
            print(f"\n✅ Total records deleted: {total}")
        else:
            total = 0
            for table_name in args.tables:
                count = await clear_table(table_name, session)
                total += count
            print(f"\n✅ Total records deleted: {total}")
    
    print("\n🎉 Database cleanup completed successfully!\n")


if __name__ == "__main__":
    asyncio.run(main())
