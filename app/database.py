import cx_Oracle
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Oracle database manager for scan results"""
    
    def __init__(self):
        self.connection = None
        self._init_connection()
    
    def _init_connection(self):
        """Initialize database connection"""
        try:
            # Oracle connection string
            dsn = cx_Oracle.makedsn(
                settings.oracle_host,
                settings.oracle_port,
                service_name=settings.oracle_service
            )
            
            self.connection = cx_Oracle.connect(
                user=settings.oracle_username,
                password=settings.oracle_password,
                dsn=dsn
            )
            
            # Create tables if they don't exist
            self._create_tables()
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create scan_results table
            cursor.execute("""
                CREATE TABLE scan_results (
                    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    job_name VARCHAR2(255) NOT NULL,
                    build_number NUMBER NOT NULL,
                    status VARCHAR2(50) NOT NULL,
                    results CLOB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create scan_logs table
            cursor.execute("""
                CREATE TABLE scan_logs (
                    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    job_name VARCHAR2(255) NOT NULL,
                    build_number NUMBER NOT NULL,
                    log_content CLOB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            logger.info("Database tables created successfully")
            
        except cx_Oracle.DatabaseError as e:
            # Table might already exist, which is fine
            if "ORA-00955" in str(e):  # Name is already being used
                logger.info("Tables already exist")
            else:
                logger.error(f"Database error: {e}")
                raise
    
    def store_scan_result(self, job_name: str, build_number: int, status: str, results: Dict[str, str]) -> bool:
        """Store scan result in database"""
        try:
            cursor = self.connection.cursor()
            
            # Convert results dict to JSON string
            import json
            results_json = json.dumps(results)
            
            cursor.execute("""
                INSERT INTO scan_results (job_name, build_number, status, results)
                VALUES (:1, :2, :3, :4)
            """, (job_name, build_number, status, results_json))
            
            self.connection.commit()
            logger.info(f"Stored scan result for {job_name}#{build_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store scan result: {e}")
            self.connection.rollback()
            return False
    
    def get_scan_result(self, job_name: str, build_number: int) -> Optional[Dict[str, Any]]:
        """Retrieve scan result from database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT job_name, build_number, status, results, timestamp
                FROM scan_results
                WHERE job_name = :1 AND build_number = :2
                ORDER BY timestamp DESC
            """, (job_name, build_number))
            
            row = cursor.fetchone()
            if row:
                import json
                return {
                    "job_name": row[0],
                    "build_number": row[1],
                    "status": row[2],
                    "results": json.loads(row[3]) if row[3] else {},
                    "timestamp": row[4]
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve scan result: {e}")
            return None
    
    def store_scan_log(self, job_name: str, build_number: int, log_content: str) -> bool:
        """Store scan log in database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO scan_logs (job_name, build_number, log_content)
                VALUES (:1, :2, :3)
            """, (job_name, build_number, log_content))
            
            self.connection.commit()
            logger.info(f"Stored scan log for {job_name}#{build_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store scan log: {e}")
            self.connection.rollback()
            return False
    
    def get_scan_log(self, job_name: str, build_number: int) -> Optional[str]:
        """Retrieve scan log from database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT log_content
                FROM scan_logs
                WHERE job_name = :1 AND build_number = :2
                ORDER BY timestamp DESC
            """, (job_name, build_number))
            
            row = cursor.fetchone()
            return row[0] if row else None
            
        except Exception as e:
            logger.error(f"Failed to retrieve scan log: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


# Global database instance
db_manager = DatabaseManager() 