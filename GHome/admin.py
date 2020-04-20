import time
from flask import Blueprint, render_template, request, redirect, url_for, current_app

import atexit

from GHome import handler
from GHome.auth import login_required
import urllib3

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
def index():
    users = handler.get_tokens()
    users_list = []
    for user in users:
        user_id = user['id']
        username = user['username']
        auth_token = user['auth_token']

        users_list.append([user_id, username, auth_token])

    scheduler_state = current_app.config['SCHEDULER_STATE']

    return render_template("admin.html", users_list=users_list, scheduler_state=scheduler_state)


@bp.route("/<username>/", methods=("GET", "POST"))
@login_required
def switches(username):
    switches = handler.get_switch(username)

    switch_list = []
    for switch in switches:
        id = switch['id']
        name = switch['name']
        pin = switch['pin']

        switch_list.append([id, name, pin])

    return render_template("admin_switch.html", switch_list=switch_list, username=username)


@bp.route("/add/token", methods=['POST'])
@login_required
def add_token():
    username = request.form["username"]
    auth_token = request.form["auth_token"]

    handler.add_user_token(username, auth_token)

    return redirect(url_for('admin.index'))


@bp.route("/delete/token", methods=['GET'])
@login_required
def delete_token():
    id = request.args.get("id")

    handler.delete_token(id)

    return '1'


@bp.route("/update/switch", methods=['GET'])
@login_required
def update_switch():
    id = request.args.get("id")
    name = request.args.get("name")
    pin = request.args.get("pin")

    handler.update_switch_by_admin(pin, name, id)

    return '1'


@bp.route("/delete/switch", methods=['GET'])
@login_required
def delete_switch():
    id = request.args.get("id")

    handler.delete_switch_by_admin(id)

    return '1'


@bp.route("/create/switch", methods=['POST'])
@login_required
def create_switch():
    username = request.form["username"]
    name = request.form["name"]
    pin = request.form["pin"]

    handler.create_switch_by_admin(username, name, pin)

    return redirect('/admin/' + username + '/')


@bp.route("/scheduler/", methods=['GET'])
@login_required
def change_scheduler():
    s = request.args.get("s")
    current_app.config['SCHEDULER_STATE'] = int(s)

    if s == '1':
        scheduler = current_app.config['SCHEDULER']
        app = current_app.app_context()
        scheduler.add_job(func=do_schedule, trigger="interval", minutes=5, id='cron_job', args=[app])
        scheduler.start()
    else:
        scheduler = current_app.config['SCHEDULER']
        # atexit.register(lambda: scheduler.shutdown())
        scheduler.remove_job('cron_job')

    return redirect(url_for('admin.index'))


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


def do_schedule(cont):
    app = cont.app
    with app.app_context():
        triggers = handler.get_schedule_work()
        for trigger in triggers:
            send_request(trigger['auth_token'], trigger['pin'], str(trigger['value']))

    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


def send_request(auth_token, pin, value):
    http = urllib3.PoolManager()
    url = current_app.config['BLYNK_HOST'] + auth_token + "/update/" + pin + "?value=" + value
    r = http.request('GET', url)
    data = r.data

    return data
