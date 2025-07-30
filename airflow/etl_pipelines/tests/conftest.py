class fake_db_conn():
    def __init__(self, conn_name = ""):
        self.conn_name = conn_name

    def cursor(self, cursor_factory=None):
        if cursor_factory:
            return cursor(cursor_type=cursor_factory, conn_name=self.conn_name)
        else:
            return cursor(conn_name = self.conn_name)

    def commit(self):
        return

    def close(self):
        return

class cursor(fake_db_conn):
    def __init__(self, cursor_type = None, conn_name = None):
        self.cursor_type = cursor_type
        self.conn_name = conn_name

    def execute(self, sql, tup):
        return

    def fetchall(self):
        if self.conn_name == "station_in_bc":
            return[("station4", False), ("station5", True)]
