from flask import Blueprint, g, redirect, request, url_for
from flask import render_template

from GHome import handler
from GHome.auth import login_required

bp = Blueprint("home", __name__)

@bp.route("/")
@login_required
def index():
    username = g.user['username']
    switches = handler.get_switch(username)

    switch_list = []
    for switch in switches:
        id = switch['id']
        name = switch['name']
        switch_list.append([id, name])

    return render_template("home.html", switch_list=switch_list)

@bp.route("/<int:id>/switch", methods=("GET", "POST"))
def switch_details(id):
    switch = handler.get_switch_from_id(id)
    if switch['username'] == g.user['username']:
        triggers = handler.get_trigger(id)
        trigger_list = []
        for trigger in triggers:
            id = trigger['id']
            value = trigger['value']
            is_enable = trigger['is_enable']
            time = trigger['time']
            time = '{:02d}:{:02d}'.format(*divmod(time, 60))
            trigger_list.append([id, value, is_enable, time])

        return render_template("switch.html", trigger_list=trigger_list, name = switch['name'], switch_id = switch['id'])

    return redirect('./')

@bp.route("/trigger/update/", methods=("GET", "POST"))
def trigger_update():
    trigger_id = request.args.get("trigger_id")
    value = request.args.get("value")
    time = request.args.get("time")
    is_enable = request.args.get("is_enable")

    handler.update_trigger(trigger_id, value, time, is_enable)

    return '1'

@bp.route("/trigger/delete/", methods=("GET", "POST"))
def trigger_delete():
    trigger_id = request.args.get("trigger_id")

    handler.delete_trigger(int(trigger_id))

    return '1'

@bp.route("/trigger/add/", methods=("GET", "POST"))
def trigger_add():
    value = request.form["trigger_value"]
    time = request.form["trigger_time"]
    switch_id = request.form["switch_id"]

    time = time.split(":")
    time = int(time[0]) * 60 + int(time[1])

    handler.add_trigger(int(switch_id), int(value), time)

    return redirect('/' + switch_id + "/switch")
