from GHome.db import get_db
import datetime

def get_tokens():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM token"
    )
    token = cur.fetchall()
    return token

def create_switch_by_admin(username, name, pin):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO switch (username, name, pin) VALUES (%s,%s,%s)", (username, name, pin),
    )
    db.commit()

def get_switch(username):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM switch WHERE username = %s", (username,)
    )
    switch = cur.fetchall()
    return switch

def update_switch_by_admin(pin, name, id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE switch SET pin = %s, name = %s WHERE id = %s", (pin, name, id),
    )
    db.commit()

def get_switch_from_id(id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM switch WHERE id = %s", (id,)
    )
    switch = cur.fetchone()
    return switch

def delete_switch_by_admin(id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM switch WHERE id = %s",
        (id,)
    )
    db.commit()

def get_trigger(switch_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM trigger WHERE switch_id = %s", (switch_id,)
    )
    trigger = cur.fetchall()
    return trigger

def update_trigger(trigger_id, value, time, is_enable):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE trigger SET value = %s, time = %s, is_enable = %s WHERE id = %s", (value, time, is_enable, trigger_id),
    )
    db.commit()

def delete_trigger(id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM trigger WHERE id = %s",
        (id,)
    )
    db.commit()

def add_trigger(switch_id, value, time):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO trigger (switch_id, value, time) VALUES (%s,%s,%s)", (switch_id, value, time),
    )
    db.commit()

def add_user_token(username, auth_token):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO token (username, auth_token) VALUES (%s,%s)", (username, auth_token),
    )
    db.commit()

def delete_token(id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM token WHERE id = %s",
        (id,)
    )
    db.commit()

def get_token(username):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM token WHERE username = %s", (username,)
    )
    token = cur.fetchone()
    return token

def get_schedule_work():
    now = datetime.datetime.now()

    time = now.hour * 60 + now.minute
    time = int(time/30) * 30

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT token.auth_token, switch.pin, `trigger`.value, `trigger`.time FROM `trigger`, switch, token "
        "WHERE `trigger`.switch_id = switch.id AND switch.username = token.username AND `trigger`.is_enable = 1 "
        "AND `trigger`.time = %s", (time,)
    )
    trigger = cur.fetchall()
    return trigger