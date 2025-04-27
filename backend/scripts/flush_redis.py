import redis


def flush_redis_store(host="localhost", port=6379, db=0, password=None):
    try:
        # Connect to Redis
        r = redis.Redis(host=host, port=port, db=db, password=password)

        # Ping to check connection
        if r.ping():
            print("Connected to Redis successfully!")

        # Flush all keys in the selected database
        r.flushdb()
        print(f"Redis database {db} has been flushed (all keys deleted).")

    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Adjust host, port, db, and password if needed
    flush_redis_store()
