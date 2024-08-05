import os
from pm4py import read_xes
import pm4py
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
path = 'G:\\uni\\term8\\Project\\test\\Flask\\static\\uploads\\'
filename_global = ''


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        filename_global = filename
        file.save(path + filename)
        return render_template('upload.html', filename=filename)
    return redirect(request.url)


@app.route('/result/<filename>')
def display_image(filename):
    return render_template('display.html', filename=filename)


@app.route('/dfg/<filename>')
def dfg(filename):
    log = pm4py.read_xes(path + filename)
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    pm4py.save_vis_dfg(dfg, start_activities, end_activities, path + "dfg.png")
    return redirect(url_for('display_image', filename="dfg.png"))


@app.route('/petri_net/<filename>')
def petri_net(filename):
    log = pm4py.read_xes(path + filename)
    petri, start_activities, end_activities = pm4py.discover_petri_net_heuristics(log)
    pm4py.save_vis_petri_net(petri, start_activities, end_activities, path + "petrinet.png")
    return redirect(url_for('display_image', filename="petrinet.png"))


@app.route('/bpmn/<filename>')
def bpmn(filename=filename_global):
    log = pm4py.read_xes(path + filename)
    bpmn = pm4py.discover_bpmn_inductive(log)
    pm4py.save_vis_bpmn(bpmn, path + "bpmn.png")
    return redirect(url_for('display_image', filename="bpmn.png"))
