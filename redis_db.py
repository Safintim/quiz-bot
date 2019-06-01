import redis
import os
from dotenv import load_dotenv

load_dotenv()

db = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True, charset='utf-8')
