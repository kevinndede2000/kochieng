from flask import Flask, render_template, request, redirect, url_for, session
from collections import defaultdict
import json
import os

app = Flask(__name__)
app.secret_key = "junior-school-secret"

DATA_FILE = "data.json"
students_data = []
subjects = [
    "English", "Kiswahili", "Math", "Science", "CRE",
    "Social Studies", "ICT", "Creative Arts", "Agriculture", "Pretechnical"
]

# Load saved records if present
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        students_data = json.load(f)

def save_records():
    with open(DATA_FILE, 'w') as f:
        json.dump(students_data, f)

def calculate_performance(total):
    if total >= 400:
        return "Excellent"
    elif total >= 300:
        return "Good"
    elif total >= 200:
        return "Fair"
    else:
        return "Needs Improvement"

def convert_grade(score):
    if score >= 80:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    else:
        return "E"

@app.route('/')
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    for student in students_data:
        scores = [student['subjects'].get(subj, 0) for subj in subjects]
        student['total'] = sum(scores)
        student['performance'] = calculate_performance(student['total'])

    ranked = sorted(students_data, key=lambda x: x['total'], reverse=True)
    for i, student in enumerate(ranked):
        student['rank'] = i + 1

    subject_averages = defaultdict(list)
    for student in students_data:
        for subj in subjects:
            score = student['subjects'].get(subj)
            if score is not None:
                subject_averages[subj].append(score)

    averages = {subj: round(sum(scores)/len(scores), 1) if scores else 0 for subj, scores in subject_averages.items()}

    return render_template("index.html", students=ranked, subjects=subjects, averages=averages)

@app.route('/submit', methods=["POST"])
def submit():
    name = request.form['name']
    subject = request.form['subject']
    score = int(request.form['score'])
    remarks = request.form.get('remarks', '')

    for s in students_data:
        if s['name'] == name:
            s['subjects'][subject] = score
            s['remarks'] = remarks
            break
    else:
        students_data.append({
            "name": name,
            "subjects": {subject: score},
            "remarks": remarks
        })

    save_records()
    return redirect('/')

@app.route('/report/<name>')
def report(name):
    student = next((s for s in students_data if s['name'] == name), None)
    if not student:
        return f"No report found for {name}", 404

    total = sum(student['subjects'].get(subj, 0) for subj in subjects)
    performance = calculate_performance(total)
    grades = {subj: convert_grade(student['subjects'].get(subj, 0)) for subj in subjects}

    return render_template("report.html", student=student, total=total,
                           performance=performance, subjects=subjects, grades=grades)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]
        if user == "teacher" and pw == "password123":
            session["logged_in"] = True
            return redirect("/")
        else:
            error_msg = "Invalid credentials"
            return render_template("login.html", error=error_msg)
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)





