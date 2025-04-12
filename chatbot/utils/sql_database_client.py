import os
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SQLDatabaseClient:
    """
    Client for connecting to and querying SQL databases (MySQL, PostgreSQL)
    """
    def __init__(self):
        self.engine = self._create_engine()
        self.connection = None
        self._metadata = None
        self._tables = None
        
    def _create_engine(self):
        """Create SQLAlchemy engine from database settings"""
        db_type = settings.DB_TYPE
        
        # Get database connection parameters from Django settings
        if db_type == 'postgresql':
            db_url = f"postgresql://{settings.DATABASES['default']['USER']}:{settings.DATABASES['default']['PASSWORD']}@{settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}/{settings.DATABASES['default']['NAME']}"
        elif db_type == 'mysql':
            db_url = f"mysql+mysqlconnector://{settings.DATABASES['default']['USER']}:{settings.DATABASES['default']['PASSWORD']}@{settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}/{settings.DATABASES['default']['NAME']}"
        else:
            # SQLite - using absolute path
            db_path = settings.DATABASES['default']['NAME']
            db_url = f"sqlite:///{db_path}"
        
        try:
            return create_engine(db_url)
        except Exception as e:
            logger.error(f"Error creating database engine: {e}")
            raise
    
    def connect(self):
        """Establish connection to the database"""
        if self.connection is None or self.connection.closed:
            try:
                self.connection = self.engine.connect()
                return True
            except Exception as e:
                logger.error(f"Error connecting to database: {e}")
                return False
        return True
    
    def disconnect(self):
        """Close the database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
    
    def get_tables(self):
        """Get list of available tables in the database"""
        if self._tables is None:
            try:
                self.connect()
                self._tables = sqlalchemy.inspect(self.engine).get_table_names()
            except Exception as e:
                logger.error(f"Error retrieving tables: {e}")
                self._tables = []
        return self._tables
    
    def get_table_schema(self, table_name):
        """Get schema information for a table"""
        try:
            self.connect()
            inspector = sqlalchemy.inspect(self.engine)
            columns = inspector.get_columns(table_name)
            
            schema_info = {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True)
                    } for col in columns
                ]
            }
            
            # Get primary keys
            primary_keys = inspector.get_pk_constraint(table_name).get('constrained_columns', [])
            schema_info["primary_keys"] = primary_keys
            
            # Get foreign keys if available
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                schema_info["foreign_keys"] = [
                    {
                        "columns": fk.get('constrained_columns', []),
                        "referenced_table": fk.get('referred_table', ''),
                        "referenced_columns": fk.get('referred_columns', [])
                    } for fk in foreign_keys
                ]
                
            return schema_info
            
        except Exception as e:
            logger.error(f"Error retrieving schema for table {table_name}: {e}")
            return {"error": str(e)}
    
    def execute_query(self, query, params=None, safe_mode=True):
        """Execute a raw SQL query and return results as pandas DataFrame"""
        if safe_mode and not self._is_safe_query(query):
            return pd.DataFrame({"error": ["This query contains unsafe operations and was blocked for security reasons."]})
        
        try:
            self.connect()
            if params:
                result = pd.read_sql(text(query), self.connection, params=params)
            else:
                result = pd.read_sql(text(query), self.connection)
            return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            error_df = pd.DataFrame({"error": [f"Error executing query: {str(e)}"]})
            return error_df
    
    def _is_safe_query(self, query):
        """Check if a query is safe (read-only) to prevent data modification"""
        query = query.strip().lower()
        unsafe_keywords = ["drop", "delete", "update", "insert", "alter", "truncate", "create", "replace"]
        
        # Simple check for unsafe operations
        for keyword in unsafe_keywords:
            if keyword in query.split():
                return False
                
        return True
    
    def get_database_info(self):
        """Get comprehensive information about the database structure"""
        tables = self.get_tables()
        db_info = {
            "tables": [],
            "relationships": []
        }
        
        # Get schema for each table
        for table in tables:
            schema = self.get_table_schema(table)
            if "error" not in schema:
                db_info["tables"].append(schema)
                
                # Add relationships if available
                if "foreign_keys" in schema:
                    for fk in schema["foreign_keys"]:
                        relationship = {
                            "from_table": table,
                            "from_columns": fk["columns"],
                            "to_table": fk["referenced_table"],
                            "to_columns": fk["referenced_columns"]
                        }
                        db_info["relationships"].append(relationship)
        
        return db_info
    
    def get_sample_data(self, table_name, limit=5):
        """Get sample data from a table"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Error retrieving sample data for {table_name}: {e}")
            return pd.DataFrame({"error": [str(e)]})
    
    def analyze_table(self, table_name):
        """Get basic statistics about a table"""
        try:
            self.connect()
            # Get column counts
            count_query = f"SELECT COUNT(*) as total_rows FROM {table_name}"
            count_result = self.execute_query(count_query)
            
            # Get schema
            schema = self.get_table_schema(table_name)
            
            # Get sample data
            sample = self.get_sample_data(table_name)
            
            analysis = {
                "table_name": table_name,
                "row_count": count_result["total_rows"].iloc[0] if not count_result.empty else 0,
                "schema": schema,
                "sample_data": sample.to_dict(orient='records') if not sample.empty and "error" not in sample else []
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing table {table_name}: {e}")
            return {"error": str(e)}