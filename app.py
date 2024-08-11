import os
from pm4py import read_xes
import pm4py
from flask import Flask, render_template, request, redirect, url_for

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
        dfg, start_activities, end_activities = pm4py.discover_dfg(log)
        nodes = [{"id": act} for act in set(dfg.keys()).union(start_activities.keys()).union(end_activities.keys())]
        links = [{"source": src, "target": tgt, "frequency": freq} for (src, tgt), freq in dfg.items()]

        # اضافه کردن گره شروع و پایان
        nodes.append({"id": "START"})
        nodes.append({"id": "END"})

        for act in start_activities:
            links.append({"source": "START", "target": act, "frequency": start_activities[act]})

        for act in end_activities:
            links.append({"source": act, "target": "END", "frequency": end_activities[act]})

        # ایجاد یک مجموعه از id های موجود در nodes
        node_ids = {node['id'] for node in nodes}

        # اطمینان حاصل کردن از وجود همه source و target ها در nodes
        for link in links:
            if link['source'] not in node_ids:
                nodes.append({"id": link['source']})
                print(f"Added missing node for source: {link['source']}")
            if link['target'] not in node_ids:
                nodes.append({"id": link['target']})
                print(f"Added missing node for target: {link['target']}")

        return render_template('upload.html', filename=filename_global, nodes=nodes, links=links)

    return render_template('upload.html', filename=None, nodes=[], links=[])

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
def bpmn(filename):
    log = pm4py.read_xes(path + filename)
    bpmn = pm4py.discover_bpmn_inductive(log)
    pm4py.save_vis_bpmn(bpmn, path + "bpmn.png")
    return redirect(url_for('display_image', filename="bpmn.png"))

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
