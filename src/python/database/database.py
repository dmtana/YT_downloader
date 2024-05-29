import asyncpg

from datetime import datetime
from config.config import DATABASE

async def start_db():
    try:
        dsn = f"postgresql://{DATABASE['user']}:{DATABASE['pass']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}"
        conn = await asyncpg.connect(dsn)
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS received (
                    id serial PRIMARY KEY,
                    date_and_time TIMESTAMP,
                    information text,
                    media_type text,
                    user_id text,
                    user_name text,
                    bot_name text)
            ''')
    except Exception as e:
        print('[DATABASE][X][creation table problem]', e)    
    finally:
        try:
            await conn.close()
            print('[DATABASE][+][DONE TABLE]')
        except Exception as e:
            print('[DATABASE][X][ERROR CLOSING in start_db()]')

async def write_to_db(information='', id='', media_type='', user_name='', bot_name='', table_name='received'):
    try:
        dsn = f"postgresql://{DATABASE['user']}:{DATABASE['pass']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}"
        conn = await asyncpg.connect(dsn)
        await conn.execute(f'''
                INSERT INTO {table_name}(date_and_time, information, media_type, user_id, user_name, bot_name) VALUES($1, $2, $3, $4, $5, $6)
                ''', datetime.now(), information, media_type, id, user_name, bot_name)
    except Exception as e:
        print('[DATABASE][X][write to db error]\n', e)    
    finally:
        try:
            await conn.close()
            print('[DATABASE][+][DONE write to db]')
        except Exception as e:
            print('[DATABASE][X][ERROR CLOSING in write_to_db()]\n', e)

async def check_status(query : str):
    try:
        dsn = f"postgresql://{DATABASE['user']}:{DATABASE['pass']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}"
        conn = await asyncpg.connect(dsn)
        rows = await conn.fetch(query)
        for row in rows:
            print(row)
    except Exception as e:
        print('[DATABASE][X][wrong getting results from database in database.check_status()]\n', e)        
    finally:
        try:
            await conn.close()        
        except:    
            print('null day Z -> database.check_status()')