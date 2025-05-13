from langgraph.store.postgres import PostgresStore
# или from langgraph.store.redis import RedisStore

DB_URI = "postgresql://postgres:1234@localhost:5432/mydb"  # или "redis://localhost:6379"
with PostgresStore.from_conn_string(DB_URI) as store: # для Redis — RedisStore.from_conn_string
    # один раз создаём таблицы/ключи
    store.setup()
    namespace = ("comon", "game")

    game = {"who":"Детектив ","what":"Получил новое дело", "where":"в библиотеке", "why":"убийство"}

    store.put(namespace, "1", game)

    print()
