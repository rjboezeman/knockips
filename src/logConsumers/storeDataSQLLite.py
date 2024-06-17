from utils.knockIPBase import KnockIPBase
from utils.logger import log
from config import sqllite_db
import sqlite3

class SQLLiteDataStore(KnockIPBase):

    def __init__(self, multi_queue, shutdown_event):
        super().__init__(multi_queue, shutdown_event)
        try:
            # Initiate SQL Lite database:
            self.db = sqlite3.connect(sqllite_db)
            self.cursor = self.db.cursor()
            self._configure_db()
            log.info(f"Connected to SQLite database successfully: {sqllite_db}")
        except sqlite3.Error as e:
            log.error(f"Failed to connect to SQLite database: {e}")

    def _configure_db(self):
        try:
            # Set PRAGMA journal_mode to WAL for more predictable write behavior
            self.cursor.execute('PRAGMA journal_mode=WAL;')
            self.db.commit()
            log.info("Database configured to use WAL mode.")
        except sqlite3.Error as e:
            log.error(f"Failed to configure database: {e}")

    async def cleanup(self):
        if self.db:
            try:
                log.info("Committing any pending transactions and closing SQLite database connection.")
                self.db.commit()  # Ensure all transactions are committed
                self.db.close()
            except sqlite3.Error as e:
                log.error(f"Failed to close SQLite database: {e}")

    def _create_table(self, columns):
        try:
            # Dynamically create table based on columns
            columns_sql = ', '.join([f'"{col}" TEXT' for col in columns])
            self.cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    {columns_sql}
                )
            ''')
            self.db.commit()
            log.debug("Table created or verified successfully.")
        except sqlite3.Error as e:
            log.error(f"Failed to create or verify table: {e}")

    async def process_log_line(self, log_line):
        log.debug('SQLLiteDataStore process_log_line: ' + log_line)
        return True

    async def take_action(self, output):
        log.debug('SQLLiteDataStore take_action: ' + str(output))
        try:
            await self._store_dict(output)
            return True
        except Exception as e:
            log.error(f"Failed to take action: {e}")
            return False

    async def _store_dict(self, data_dict):
        try:
            # Ensure the table exists with the required columns
            self._create_table(data_dict.keys())

            # Insert the data into the table
            columns = ', '.join([f'"{col}"' for col in data_dict.keys()])
            placeholders = ', '.join(['?' for _ in data_dict.values()])
            values = list(data_dict.values())

            self.cursor.execute(f'''
                INSERT INTO data ({columns}) VALUES ({placeholders})
            ''', values)
            self.db.commit()  # Ensure data is immediately written to the file
            log.debug(f"Data stored successfully: {data_dict}")
        except sqlite3.Error as e:
            log.error(f"Failed to insert data: {e}")
        except Exception as e:
            log.error(f"Unexpected error occurred: {e}")
