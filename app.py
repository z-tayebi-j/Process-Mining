import os
import base64
from io import BytesIO
import pandas as pd
from matplotlib import pyplot as plt
from pm4py import read_xes
import pm4py
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
path = 'G:\\uni\\term8\\Project\\test\\Flask\\static\\uploads\\'
filename_global = ''


@app.route('/', methods=['GET', 'POST'])
def index():
    global filename_global
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename_global = file.filename
            file.save(path + filename_global)
            return redirect(url_for('index'))
    elif filename_global:
        log = pm4py.read_xes(path + filename_global)
        event_counts = pm4py.get_event_attribute_values(log, "concept:name")
        events_df = pd.DataFrame(list(event_counts.items()), columns=['Event', 'Count'])
        plt.figure(figsize=(5, 3))
        plt.xticks(fontsize=9)
        plt.xticks(rotation=20, ha='right')
        plt.bar(events_df['Event'], events_df['Count'], color='#1e0972')
        plt.xlabel('Activity')
        plt.ylabel('Count')
        plt.title('Activity Frequency')
        plt.tight_layout()

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        data = dict()
        data['total events'] = len(log)
        data['total cases'] = len(set(log['case:concept:name']))
        data['total activities'] = len(set(log['concept:name']))
        data['start time'] = min(log['time:timestamp'])
        data['end time'] = max(log['time:timestamp'])

        return render_template('upload.html', filename=filename_global, plot_url=plot_url, data=data)

    return render_template('upload.html', filename=None, nodes=[], links=[])


@app.route('/result/<filename>')
def display_image(filename):
    return render_template('display.html', filename=filename)


@app.route('/dfg/<filename>')
def dfg(filename):
    log = pm4py.read_xes(path + filename)
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    pm4py.save_vis_dfg(dfg, start_activities, end_activities, path + "dfg.png")
    return render_template('display_dfg.html', filename="dfg.png", dataset=filename)


@app.route('/dfg2/<filename>')
def dfg2(filename):
    log = pm4py.read_xes(path + filename)
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    links = [{"source": src, "target": tgt, "frequency": freq} for (src, tgt), freq in dfg.items()]
    nodes = []

    for act in start_activities:
        links.append({"source": "START", "target": act, "frequency": start_activities[act]})

    for act in end_activities:
        links.append({"source": act, "target": "END", "frequency": end_activities[act]})

    node_ids = set()

    for link in links:
        if link['source'] not in node_ids:
            node_ids.add(link['source'])
        if link['target'] not in node_ids:
            node_ids.add(link['target'])

    for id in node_ids:
        print(id)
        nodes.append({"id": id})

    return render_template('DFG.html', filename=filename, nodes=nodes, links=links)


@app.route('/petri_net/<filename>')
def petri_net(filename):
    log = pm4py.read_xes(path + filename)
    petri, start_activities, end_activities = pm4py.discover_petri_net_heuristics(log)
    pm4py.save_vis_petri_net(petri, start_activities, end_activities, path + "petrinet.png")
    return redirect(url_for('display_image', filename="petrinet.png"))


@app.route('/bpmn/<filename>')
def bpmn(filename):
    log = pm4py.read_xes(path + filename)
    bpmn = pm4py.discover_bpmn_inductive(log)
    pm4py.save_vis_bpmn(bpmn, path + "bpmn.png")
    return redirect(url_for('display_image', filename="bpmn.png"))


@app.route('/petri_net_data/<filename>')
def petri_net_data(filename):
    log = pm4py.read_xes(path + filename)
    petri, start_activities, end_activities = pm4py.discover_petri_net_heuristics(log)

    places = []
    for place in petri.places:
        places.append({
            'id': place.name,
            'cx': 0,
            'cy': 0
        })

    transitions = []
    for transition in petri.transitions:
        transitions.append({
            'id': transition.name,
            'x': 0,
            'y': 0,
            'type': 'filled' if transition.label else 'empty'
        })

    arcs = []
    for arc in petri.arcs:
        arcs.append({
            'source': arc.source.name,
            'target': arc.target.name
        })

    return jsonify({'places': places, 'transitions': transitions, 'arcs': arcs})


@app.route('/petri_net2/<filename>')
def petri_net2(filename):
    return render_template('PetriNet.html', filename=filename)


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
