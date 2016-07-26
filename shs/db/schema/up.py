# ---------------------------------------------
#
# The file up is part of the shs project.  
# Copyright (c) 2015 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------

import psycopg2

data_types = {
    "mde": {
        "temp": "float32",
        "e_ks": "float32",
        "e_tot": "float32",
        "vol": "float32",
        "p": "float32",
    }
}

if __name__ == "__main__":
    conn = psycopg2.connect(dbname='siesta',
                            user='andrey',
                            password='gfhjkm')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE data_types (
        id serial PRIMARY KEY,
        table_name varchar (20) NOT NULL,
        array_name varchar (20) NOT NULL,
        array_type varchar (10) NOT NULL
        );""")

    cur.execute("""CREATE TABLE calc (
        id serial PRIMARY KEY,
        name varchar (50) NOT NULL,
        label varchar (25) NOT NULL,
        dir varchar (100) NOT NULL
        );""")

    cur.execute("""CREATE TABLE mde (
        id serial PRIMARY KEY,
        calc_id int REFERENCES calc(id),
        temp bytea  NOT NULL,
        e_ks bytea  NOT NULL,
        e_tot bytea  NOT NULL,
        vol bytea  NOT NULL,
        p bytea  NOT NULL
        );""")

    for table, val in data_types.iteritems():
        for array, data_type in val.iteritems():
            cur.execute("""INSERT INTO data_types(
                table_name,
                array_name,
                array_type) VALUES (%s, %s, %s);""",
                        (table, array, data_type))

    conn.commit()
    conn.close()
