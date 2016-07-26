# ---------------------------------------------
#
# The file down is part of the shs project.  
# Copyright (c) 2015 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------

import psycopg2

if __name__ == "__main__":
    conn = psycopg2.connect(dbname='siesta',
                            user='andrey',
                            password='gfhjkm')
    cur = conn.cursor()
    cur.execute("""DROP TABLE mde;""")
    cur.execute("""DROP TABLE calc;""")
    cur.execute("""DROP TABLE data_types;""")
    conn.commit()
    conn.close()
