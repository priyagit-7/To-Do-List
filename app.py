from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone 
import pytz 
# Removed: from jinja2_time import TimeExtension

app=Flask(__name__)

# --- TIMEZONE CONFIGURATION FIX ---
# 1. Define the Local Timezone
LOCAL_TZ = pytz.timezone("Asia/Kolkata")

# 2. Define and register a custom Jinja filter (CRITICAL FIX)
# This filter converts UTC datetime to the specified local timezone (tz)
@app.template_filter('local_time')
def local_time_filter(dt, tz):
    if dt is None:
        return ""
    # 1. Make the naive datetime (from the database) timezone-aware (as UTC)
    dt_utc = pytz.utc.localize(dt)
    # 2. Convert the UTC time to the target local timezone
    dt_local = dt_utc.astimezone(tz)
    # 3. Format the output to the desired string, including 12-hour clock and AM/PM
    return dt_local.strftime('%d-%m-%Y %I:%M:%S %p')
# --- END TIMEZONE CONFIGURATION ---
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
#Data Class ~ Row of Data
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    complete = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=lambda : datetime.now(timezone.utc)) 
    def __repr__(self)->str:
        return f"Task {self.id}"
#Homepage
@app.route('/',methods=["POST", "GET"])
def index():
    #Add Task 
    if request.method == 'POST':
        current_task = request.form["content"]
        new_task=MyTask(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"Error adding task: {e}")
            return f"Error adding task: {e}"
    #see all current tasks
    else:
        tasks = MyTask.query.order_by(MyTask.created).all()
        # Pass the LOCAL_TZ variable and tasks
    return render_template("index.html", tasks=tasks, local_tz=LOCAL_TZ)
#Delete Task
@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"Error deleting task: {e}"
#Update Task
@app.route("/update/<int:id>",methods=["GET", "POST"])
def edit(id:int):
    task = MyTask.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form['content']
        task.created = datetime.now(timezone.utc) 
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"Error updating task: {e}"
    else: 
        return render_template("edit.html",task=task)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)