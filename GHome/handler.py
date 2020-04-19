from GHome.db import get_db
import datetime

def get_tokens():
    db = get_db()
    token = db.execute(
        "SELECT * FROM token"
    ).fetchall()
    return token

def create_switch_by_admin(username, name, pin):
    db = get_db()
    db.execute(
        "INSERT INTO switch (username, name, pin) VALUES (?,?,?)", (username, name, pin),
    )
    db.commit()

def get_switch(username):
    db = get_db()
    switch = db.execute(
        "SELECT * FROM switch WHERE username = ?", (username,)
    ).fetchall()
    return switch

def update_switch_by_admin(pin, name, id):
    db = get_db()
    db.execute(
        "UPDATE switch SET pin = ?, name = ? WHERE id = ?", (pin, name, id),
    )
    db.commit()

def get_switch_from_id(id):
    db = get_db()
    switch = db.execute(
        "SELECT * FROM switch WHERE id = ?", (id,)
    ).fetchone()
    return switch

def delete_switch_by_admin(id):
    db = get_db()
    db.execute(
        "DELETE FROM switch WHERE id = ?",
        (id,)
    )
    db.commit()

def get_trigger(switch_id):
    db = get_db()
    trigger = db.execute(
        "SELECT * FROM trigger WHERE switch_id = ?", (switch_id,)
    ).fetchall()
    return trigger

def update_trigger(trigger_id, value, time, is_enable):
    db = get_db()
    db.execute(
        "UPDATE trigger SET value = ?, time = ?, is_enable = ? WHERE id = ?", (value, time, is_enable, trigger_id),
    )
    db.commit()

def delete_trigger(id):
    db = get_db()
    db.execute(
        "DELETE FROM trigger WHERE id = ?",
        (id,)
    )
    db.commit()

def add_trigger(switch_id, value, time):
    db = get_db()
    db.execute(
        "INSERT INTO trigger (switch_id, value, time) VALUES (?,?,?)", (switch_id, value, time),
    )
    db.commit()

def add_user_token(username, auth_token):
    db = get_db()
    db.execute(
        "INSERT INTO token (username, auth_token) VALUES (?,?)", (username, auth_token),
    )
    db.commit()

def delete_token(id):
    db = get_db()
    db.execute(
        "DELETE FROM token WHERE id = ?",
        (id,)
    )
    db.commit()

def get_token(username):
    db = get_db()
    token = db.execute(
        "SELECT * FROM token WHERE username = ?", (username,)
    ).fetchone()
    return token

def get_schedule_work():
    now = datetime.datetime.now()

    time = now.hour * 60 + now.minute
    time = int(time/30) * 30

    db = get_db()
    trigger = db.execute(
        "SELECT token.auth_token, switch.pin, trigger.value, trigger.time FROM trigger, switch, token "
        "WHERE trigger.switch_id = switch.id AND switch.username = token.username AND trigger.is_enable = 1 "
        "AND trigger.time > ? AND trigger.time <= ?", (time, time+30),
    ).fetchall()
    return trigger