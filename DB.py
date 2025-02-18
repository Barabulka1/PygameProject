import sqlite3

def save(h, c, k):
    con = sqlite3.connect("results")
    con.execute(f"INSERT INTO Results(hits, cadrs, kills) VALUES({h}, {c}, {k})")
    con.commit()