import json
from pqueue import Queue as PersistentQueue
import re
import requests
import pandas as pd
import time
import requests
from sqlalchemy import create_engine
from flask import g
from flask import Flask, session, redirect, url_for, escape, request, render_template
from flask import flash
import records

app = Flask(__name__)
app.secret_key = "change me pls"

persistent_queue = None
#  persistent_queue = PersistentQueue("persistent_jobs")

from queue import Queue

simple_queue = Queue()

simple_queue.put("job1")
simple_queue.put("job2")
simple_queue.put("startup_sequence_end")


clients_lastseen = {}


def add(item):
    if persistent_queue is not None:
        global persistent_queue
        persistent_queue.push(item)
    else:
        simple_queue.put(item)


def get_queue_size():
    if persistent_queue is not None:
        raise NotImplementedError("!!!")
        # probably return persistent_queue.qsize()
    else:
        return simple_queue.qsize()


@app.route('/')
def index():
    g.n_jobs = get_queue_size()
    return render_template("stats.html")


@app.route("/new_action", methods=['GET', 'POST'])
# @mock.patch('requests.post', mock.Mock(side_effect=lambda q, qq, qqq: InlineClass({'text': LOGIN_ENDPOINT_MOCK_USERTYPE})))
def login():
    print("LOGIN NEW ACTION")
    oldsize = get_queue_size()
    add((
        request.form['key'],
        request.form['value'],
    ))
    newsize = get_queue_size()
    return "OLD={} NEW={}".format(oldsize, newsize)



whohaswhat = {

} # todo move to permanent

@app.route("/signoff")
def signoff():
    """
        instead logoff
        assuming friendly termination notify
    """
    pass

from flask import send_from_directory
@app.route('/<path:path>.js')
def send_static_js(path):
    return send_from_directory('',path+'.js')

@app.route('/<path:path>.html')
def send_static_html(path):
    return send_from_directory('',path+'.html')


@app.route("/get_front_job", methods=['GET'])
def get_front_job():

    request.args.get('key', '')



    # raise DeprecationWarning("THIS IS WRONG")
    print ("!!!!!!!abstraction! tmp fix me dangerous!!!!")
    return json.dumps(
        {} if get_queue_size()==0 else simple_queue.get()
    )


@app.route("/heartbeat",methods=['GET'])
def heartbeat():
    # objid = ???
    from time import time
    t = time()
    clients_lastseen[request.args.get('peer_id')] = time()
    #THIS NEEDS TO BE SEPARATE THREAD "GARBAGECOLLECT"
    for key,val in clients_lastseen.items():
        if clients_lastseen[key] < time() - 8:
            del clients_lastseen[key]
    #THIS NEEDS TO BE SEPARATE THREAD
    print (clients_lastseen)

    from random import random
    if random()>0.5:
        heartbeat_json_command = json.dumps({"cmd":"srv-setkey","key":t,"value":"valueof" + str(t)})
    else:
        send_to = None
        if len(clients_lastseen) > 1:
            for key in clients_lastseen.keys():
                if key!=request.args['peer_id']:
                    send_to = key

            heartbeat_json_command = json.dumps({
                "cmd":"srv-replicate",
                "to":send_to,
                "key":"identity/"+request.args['peer_id']
            })

        else:
            #only 1 client
            heartbeat_json_command=json.dumps({})

    return heartbeat_json_command

@app.route("/new_view")
def add_new_view():
    return """
        <html><body>
        <form action='/new_action' method='post'>
        <input type='text' name='key'>
        <input type='text' name='value'>
        <input type='submit' value='submit'>
        </form></body></html>
    """


if __name__ == '__main__':
    app.run(debug=True)
