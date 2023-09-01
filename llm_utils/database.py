import pyodbc

def get_db_connection(db_server, db_name, db_user, db_password):
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + db_server
        + ";DATABASE="
        + db_name
        + ";UID="
        + db_user
        + ";PWD="
        + db_password
    )
    return pyodbc.connect(conn_str)