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
                    date_and_time date,
                    information text,
                    media_type text,
                    user_id text,
                    user_name text)
            ''')
    except Exception as e:
        print('[problems]', e)    
    finally:
        # Close the connection.
        try:
            await conn.close()
            print('GOOOD')
        except Exception as e:
            print('[almost]')

async def write_to_db(information='', id='', media_type='', user_name='', table_name='received'):
    try:
        dsn = f"postgresql://{DATABASE['user']}:{DATABASE['pass']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}"
        conn = await asyncpg.connect(dsn)
        await conn.execute(f'''
                INSERT INTO {table_name}(date_and_time, information, media_type, user_id, user_name) VALUES($1, $2, $3, $4, $5)
                ''', datetime.now(), information, media_type, id, user_name)
    except Exception as e:
        print('[ZALUPA]', e)    
    finally:
        # Close the connection.
        try:
            await conn.close()
            print('GOOOD')
        except Exception as e:
            print('NOT GOD')

    print('[database]' ,'OK')

# async def start_db():
#     asyncio.get_event_loop().run_until_complete(bench_asyncpg_pool())