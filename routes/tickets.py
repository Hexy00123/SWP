import bson.json_util

from routes.utils import validator, user_authorisation
from flask import Blueprint, make_response, jsonify, render_template, request
from models import *
from bson import errors
from json import *

tickets_blueprint = Blueprint('tickets', __name__)


@tickets_blueprint.route('/admin/ticket', methods=['POST'])
@validator('location_id', 'modername', 'password', 'updates')
def create_ticket():
    pass


@tickets_blueprint.route('/admin/tickets', methods=['GET'])
@validator()
def tickets():
    data = []
    for ticket in db.Ticket.find():
        location = db.Location.get_by_id(ticket.location_id)
        if location is None:
            db.Ticket.remove_by_id(ticket.location_id)
            continue

        data.append(ticket)

    return render_template('tickets.html', data=data)


@tickets_blueprint.route('/admin/ticket/<id>', methods=['GET'])
def ticket_card(id):
    try:
        ticket = db.Ticket.get_by_id(ObjectId(id))
    except errors.InvalidId:
        ticket = None

    if ticket is None:
        return make_response("No such ticket", 204)

    location = db.Location.get_by_id(ticket.location_id)
    if location is None:
        db.Ticket.remove_by_id(ticket.id)
        return make_response("Location is removed", 204)

    return render_template('ticket_card.html', ticket=ticket, location=location, json=jsonify(ticket.jsonify()))


@tickets_blueprint.route('/admin/ticket', methods=['PUT'])
@validator('id')
def process_ticket(id):
    ticket = db.Ticket.get_by_id(ObjectId(id))
    if ticket is None:
        return make_response('Ticket already processed', 204)

    location = db.Location.get_by_id(ticket.location_id)
    if location is None:
        return make_response('Location does not exist', 204)

    updates = loads(request.data.decode())
    for field, value in updates.items():
        print(field, ticket.updates[field], value)
        if value:
            db.Location.update_instance(location._id, field, ticket.updates[field])
    db.Ticket.remove_by_id(ticket._id)

    return make_response({}, 200)


@tickets_blueprint.route('/admin/ticket', methods=['DELETE'])
def remove_ticket(id):
    ticket = db.Ticket.get_by_id(ObjectId(id))
    if ticket is None:
        return make_response('Ticket already processed or does not exist', 204)

    db.Ticket.remove_by_id(ticket._id)
    return make_response({}, 200)
