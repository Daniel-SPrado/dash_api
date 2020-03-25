from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from validation import JsonValidation, ArgsValidation
from flask_cors import CORS 

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/dash_api"
app.config["MONGO_DBNAME"] = "dash_api"
cors = CORS(app)
app.config['CORS_HEADERS'] = 'application/json'


mongo = PyMongo(app)

CORS_ANSWER = {'Content-Type': 'application/json; charset=utf-8', 
                                               'Access-Control-Allow-Origin': "*",
                                               'Access-Control-Allow-Methods': "POST, GET, PUT, OPTIONS, DELETE, PATCH" 
                                               }

@app.route('/', methods=['GET'])
def index():
    return 'DASH_API has been started'
    
@app.route('/group', methods=['GET'])
def group_list():
    amount = request.args.get('latest', default=0, type=int)

    response = list(mongo.db.groups.find(ArgsValidation().group_args(
                                                request.args)).sort(
                                                "$natural", -1).limit(amount))

    for document in response:
        del document['_id']

    return jsonify(response), CORS_ANSWER
    
# Cria grupo
@app.route('/group', methods=['POST'])
def group_register():
    group = request.get_json() if request.is_json else request.form.to_dict()
    if not JsonValidation().group_validation(group):
        abort(400)
    try:
        mongo.db.groups.update_one(group, {'$set': group},
                                          upsert=True)
    except errors.WriteError:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500
    return jsonify({'code': 200, 'message': 'Success'}), 200

# Delete grupo
@app.route('/delete/group', methods=['POST'])
def group_delete():
    group = request.get_json() if request.is_json else request.form.to_dict()
    if not JsonValidation().group_validation(group):
        abort(400)
    try:
        response = list(mongo.db.groups.find({"group": group['group']}))
        
        for document in response:
            del document['_id']
                       
        mongo.db.groups.remove( { "group": group['group'] } )
        
    except:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500
    return jsonify({'code': 200, 'message': 'Success'}), CORS_ANSWER


# Adiciona service ao grupo e ao command
@app.route('/add/group', methods=['POST'])
def group_add():
    group = request.get_json() if request.is_json else request.form.to_dict()
    print(group['group'])
    print(group)
    if not JsonValidation().group_validation(group):
        abort(400)
    try:
        mongo.db.groups.update(
            { "group": group['group'] }, 
            { "$push": 
                { 
                    "services": 
                    {
                        "chipset": group['services']['chipset'],
                        "mac": group['services']['mac'], 
                        "number": group['services']['number'] 
                    } 
                } 
            }
        ),
        print("Agora testar commands")
        mongo.db.commands.update_one(
            group["services"], 
            {
                '$set': group["services"],
                '$set': { 
                    "command": [], 
                    "ip": '',
                    "group": group['group']    
                }
            },
            upsert=True
        )
    except errors.WriteError:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500
    return jsonify({'code': 200, 'message': 'Success'}), CORS_ANSWER

# Delete service de group
@app.route('/delete/service', methods=['POST'])
def group_exclude():
    group = request.get_json() if request.is_json else request.form.to_dict()
    if not JsonValidation().group_validation(group):
        abort(400)
    try:
        mongo.db.groups.update(
            { "group": group['group'] }, 
            { "$pull": 
                { 
                    "services": 
                    {  
                        "chipset": group['services']['chipset'],
                        "mac": group['services']['mac'], 
                        "number": group['services']['number']
                    } 
                } 
            }
        )
        mongo.db.commands.remove( 
            {  
                "chipset": group['services']['chipset'],
                "mac": group['services']['mac'],
                "number": group['services']['number'],
            } 
         )
    except errors.WriteError:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500
    return jsonify({'code': 200, 'message': 'Success'}), 200

#Lista commands
@app.route('/command', methods=['GET'])
def command_list():
    amount = request.args.get('latest', default=0, type=int)

    response = list(mongo.db.commands.find(ArgsValidation().command_args(
                                                request.args)).sort(
                                                "$natural", -1).limit(amount))

    for document in response:
        del document['_id']

    return jsonify(response), 200

# Adiciona command ao command
# Acrescentar 'option' para definir como o comando vai interagir com o cliente
@app.route('/add/command', methods=['POST'])
def command_add():
    command = request.get_json() if request.is_json else request.form.to_dict()
    if not JsonValidation().command_validation(command):
        return 400
    try:
        mongo.db.commands.update(
            { 
                "mac": command['services']['mac'],
                "chipset": command['services']['chipset'],
                "number": command['services']['number'] 
            }, 
            { "$push": 
                { 
                    "command": 
                    { 
                        "name": command['command']['name'],
                        "ip": command['command']['ip'],
                        "params": command['command']['params']
                    } 
                } 
            }
        )
    except errors.WriteError:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500
    return jsonify({'code': 200, 'message': 'Success'}), 200

@app.route('/change/command', methods=['POST'])
def command_change():
    command = request.get_json() if request.is_json else request.form.to_dict()
    print(command['ip'])
    if not JsonValidation().command_validation(command):
        return 400
    try:
        mongo.db.commands.update(
            { 
                "mac": command['mac'],
                "chipset": command['chipset'],
                "number": command['number'] 
            }, 
            {             
                "$set": { 
                    "ip": str(command['ip']) 
                }
            }
        )
    except errors.WriteError:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500
    return jsonify({'code': 200, 'message': 'Success'}), 200

# Apaga command de command
@app.route('/delete/command', methods=['POST'])
def command_delete():
    command = request.get_json() if request.is_json else request.form.to_dict()
    print(command)
    if not JsonValidation().command_validation(command):
        abort(400)
    try:
        mongo.db.commands.update(
            { 
                "mac": command['services']['mac'],
                "chipset": command['services']['chipset'],
                "number": command['services']['number'] 
            }, 
            { "$pull": 
                { 
                    "command": 
                    {
                        "name": command['command']['name'],
                        "ip": command['command']['ip'],
                        "params": command['command']['params']
                    } 
                } 
            },
        )
    except errors.WriteError:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500
    return jsonify({'code': 200, 'message': 'Success'}), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)


