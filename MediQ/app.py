
from flask import Flask, render_template, request, redirect, url_for
import os, json, random, uuid

app = Flask(__name__, template_folder='templates', static_folder='static')
BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, 'data')
HOSPITALS_FILE = os.path.join(DATA_DIR, 'hospitals.json')
APPOINTMENTS_FILE = os.path.join(DATA_DIR, 'appointments.json')

def load_json(p):
    try:
        with open(p, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json(p, data):
    with open(p, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    hospitals = load_json(HOSPITALS_FILE)
    for i,h in enumerate(hospitals):
        h['rating'] = round(random.uniform(3.5,5.0),1)
        h['beds_available'] = random.randint(50, min(300, h.get('beds',300)))
        if not h.get('image'):
            h['image'] = f'img/h{(i%5)+1}.svg'
    return render_template('index.html', hospitals=hospitals)

@app.route('/search')
def search():
    q = request.args.get('location','').strip().lower()
    hospitals = load_json(HOSPITALS_FILE)
    results = [h for h in hospitals if q in h.get('name','').lower() or q in h.get('city','').lower()]
    for i,h in enumerate(results):
        h['rating'] = round(random.uniform(3.5,5.0),1)
        h['beds_available'] = random.randint(50, min(300, h.get('beds',300)))
        if not h.get('image'):
            h['image'] = f'img/h{(i%5)+1}.svg'
    return render_template('index.html', hospitals=results)

@app.route('/hospital/<hid>')
def hospital(hid):
    hospitals = load_json(HOSPITALS_FILE)
    h = next((x for x in hospitals if x.get('id')==hid), None)
    if not h:
        return "Not found", 404
    h['rating'] = round(random.uniform(3.5,5.0),1)
    h['beds_available'] = random.randint(50, min(300, h.get('beds',300)))
    treatments = ["Cardiology","Neurology","Pediatrics","ENT","Orthopedics","Radiology","Oncology","Dermatology","Psychiatry","Physiotherapy"]
    h['treatments'] = random.sample(treatments, k=7)
    if not h.get('doctors'):
        h['doctors'] = [
            {"id":"d1","name":"Dr. Sarah Johnson","department":h['treatments'][0],"experience":5,"available": random.choice([True,False])},
            {"id":"d2","name":"Dr. Michael Chen","department":h['treatments'][1],"experience":8,"available": random.choice([True,False])},
            {"id":"d3","name":"Dr. Emily Rodriguez","department":h['treatments'][2],"experience":11,"available": random.choice([True,False])}
        ]
    else:
        for d in h['doctors']:
            d['available'] = random.choice([True, False])
    if not h.get('image'):
        h['image'] = 'img/banner.svg'
    return render_template('hospital.html', hospital=h)

@app.route('/book/<hid>/<doctor>', methods=['GET','POST'])
def book(hid, doctor):
    hospitals = load_json(HOSPITALS_FILE)
    h = next((x for x in hospitals if x.get('id')==hid), None)
    if request.method=='POST':
        date = request.form.get('date')
        time = request.form.get('time')
        price = request.form.get('price') or str(random.randint(500,1500))
        aid = str(uuid.uuid4())[:8]
        appt = {'id':aid,'hospital_id':hid,'hospital_name':h.get('name'),'doctor':doctor,'date':date,'time':time,'paid':False,'price':price}
        appts = load_json(APPOINTMENTS_FILE)
        appts.append(appt)
        save_json(APPOINTMENTS_FILE, appts)
        return redirect(url_for('payment', aid=aid))
    price = random.randint(500,1500)
    return render_template('book.html', hospital=h, doctor=doctor, price=price)

@app.route('/payment/<aid>', methods=['GET','POST'])
def payment(aid):
    if request.method=='POST':
        appts = load_json(APPOINTMENTS_FILE)
        for a in appts:
            if a.get('id')==aid:
                a['paid']=True
        save_json(APPOINTMENTS_FILE, appts)
        return redirect(url_for('success', aid=aid))
    return render_template('payment.html', aid=aid)

@app.route('/success/<aid>')
def success(aid):
    appts = load_json(APPOINTMENTS_FILE)
    a = next((x for x in appts if x.get('id')==aid), None)
    return render_template('success.html', appt=a)

@app.route('/appointments')
def appointments():
    appts = load_json(APPOINTMENTS_FILE)
    return render_template('appointments.html', appts=appts)

if __name__=='__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(HOSPITALS_FILE):
        with open(HOSPITALS_FILE,'w') as f: json.dump([], f)
    if not os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE,'w') as f: json.dump([], f)
    app.run(debug=True, host='0.0.0.0', port=5000)
