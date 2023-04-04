
import re  
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__) 

app.secret_key = 'abcdefgh'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353hw4db'
  
mysql = MySQL(app)  

@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        if user:              
            session['loggedin'] = True
            session['userid'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return redirect(url_for('tasks'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)

@app.route('/logout', methods =['GET', 'POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            message = 'Choose a different username!'
  
        elif not username or not password or not email:
            message = 'Please fill out the form!'

        else:
            cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, % s, % s, % s)', (username, email, password,))
            mysql.connection.commit()
            message = 'User successfully created!'

    elif request.method == 'POST':

        message = 'Please fill all the fields!'
    return render_template('register.html', message = message)

@app.route('/tasks', methods =['GET', 'POST'])
def tasks():
    user_id = session.get('userid')

    todo_status = 'Todo'
    done_status = 'Done'

    # LIST TASKS
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Task WHERE user_id = %s AND status = %s ORDER BY deadline', (user_id, todo_status, ))
    todos = cursor.fetchall()
    cursor.execute('SELECT * FROM Task WHERE user_id = %s AND status = %s ORDER BY done_time DESC', (user_id, done_status, ))
    dones = cursor.fetchall()
    
    # LIST TASKTYPES
    cursor.execute('SELECT * FROM TaskType')
    types = cursor.fetchall()

    # Create message from add()
    create_message = request.args.get('create_message')
    # Done-Undone messages from finish(task_id)
    done_message = request.args.get('done_message')
    undone_message = request.args.get('undone_message')
    # Delete message from delete(task_id)
    delete_message = request.args.get('delete_message')
    # Update message from delete(task_id)
    update_message = request.args.get('update_message')

    return render_template('tasks.html', todos=todos, dones=dones, types=types, 
                           create_message=create_message, done_message=done_message, 
                           undone_message=undone_message, delete_message=delete_message, 
                           update_message=update_message)

@app.route("/add", methods=["POST"])
def add():
    user_id = session.get('userid')
    if user_id: 
        messages = []
        todo_type = 'Todo'
        if 'title' in request.form and 'description' in request.form \
                                and 'deadline' in request.form and 'task_type' in request.form:
            title = request.form['title']
            description = request.form['description']
            deadline = request.form['deadline']
            task_type = request.form['task_type']
            if not deadline:
                messages.append('Please enter a valid Deadline!')
            if not task_type:
                messages.append('Please enter a valid Type!')
            if not description:
                messages.append('Please enter a valid Description!')
            if not title:
                messages.append('Please enter a valid Title!')
            if not messages:
                with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
                    cursor.execute("INSERT INTO Task (title, description, status, deadline, creation_time, user_id,  task_type) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                                (title, description, todo_type, deadline, datetime.now(), user_id, task_type,))
                    mysql.connection.commit()
                messages.append(title + ' created successfully')
            create_message = '\n'.join(messages)
            
    return redirect(url_for("tasks", create_message=create_message))

@app.route("/done-undone/<string:task_id>")
def finish(task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Task WHERE id = %s ORDER BY deadline', (task_id, ))
    todo = cursor.fetchone()
    todo_type = 'Todo'
    done_type = 'Done'
    done_messages = []
    undone_messages = []
    title = todo['title']
    if todo['status'] == todo_type:
        cursor.execute('UPDATE Task SET status = %s, done_time = %s WHERE id = %s', (done_type, datetime.now(), task_id, ))  
        done_messages.append(title+ ' is done')
    else:
        cursor.execute('UPDATE Task SET status = %s, done_time = %s WHERE id = %s', (todo_type, None ,  task_id, ))
        undone_messages.append(title + ' is undone')  
    mysql.connection.commit()
    done_message = '\n'.join(done_messages)
    undone_message = '\n'.join(undone_messages)
    return redirect(url_for("tasks", done_message=done_message, undone_message=undone_message))

@app.route("/update/<string:task_id>", methods=['GET', 'POST'])
def update(task_id):
    if request.method == 'POST':
        update_messages = []
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        task_type = request.form['task_type']
        if not deadline:
            update_messages.append('Please enter a valid Deadline!')
        if not task_type:
            update_messages.append('Please enter a valid Type!')
        if not description:
            update_messages.append('Please enter a valid Description!')
        if not title:
            update_messages.append('Please enter a valid Title!')
        if not update_messages:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE Task SET title = %s, description = %s, deadline = %s, task_type = %s WHERE id = %s', (title, description, deadline, task_type, task_id,))
            mysql.connection.commit()
            update_messages.append(task_id + ' updated!')
        update_message = '\n'.join(update_messages)
        return redirect(url_for('tasks', update_message=update_message))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Task WHERE id = %s', (task_id,))
        task = cursor.fetchone()
        cursor.execute('SELECT type FROM TaskType')
        types = cursor.fetchall()
        return render_template('update.html', task=task, types=types, task_id=task_id)

@app.route("/delete/<string:task_id>")
def delete(task_id):
    delete_messages = []
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM Task WHERE id = %s", (task_id, ))
    mysql.connection.commit()
    delete_messages.append(task_id + ' is deleted')
    delete_message = '\n'.join(delete_messages)
    return redirect(url_for("tasks", delete_message=delete_message))

@app.route('/analysis', methods =['GET', 'POST'])
def analysis():
    user_id = session.get('userid')
    done_type = 'Done'
    todo_type = 'Todo'
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT title, (TIMESTAMPDIFF \
                   (SECOND, deadline, done_time))  \
                   AS latency FROM Task WHERE \
                   user_id = %s AND status = %s AND done_time > deadline', 
                   (user_id, done_type, ))
    firsts = cursor.fetchall()
    
    cursor.execute('SELECT AVG(TIMESTAMPDIFF \
                   (SECOND, creation_time, done_time)) \
                   AS avg_completion_time FROM Task \
                   WHERE user_id = %s AND status = %s', 
                   (user_id, done_type, ))
    second = cursor.fetchone()

    cursor.execute('SELECT task_type, COUNT(*) AS \
                   num_completed FROM Task WHERE \
                   user_id = %s AND status = %s \
                   GROUP BY task_type ORDER BY \
                   num_completed DESC', 
                   (user_id, done_type, ))
    thirds = cursor.fetchall()

    cursor.execute('SELECT title, deadline \
                    FROM Task WHERE user_id = %s \
                   AND status = %s ORDER BY \
                   deadline ASC', 
                   (user_id, todo_type, ))
    fourths = cursor.fetchall()

    cursor.execute('SELECT title, TIMESTAMPDIFF \
                   (MINUTE, creation_time, done_time) \
                   AS completion_time \
                   FROM Task WHERE status = %s AND \
                   user_id = %s ORDER BY \
                   completion_time DESC LIMIT 2', (done_type, user_id, ))
    fifths = cursor.fetchall()

    return render_template('analysis.html', 
                           firsts = firsts, second=second, 
                           thirds= thirds, fourths=fourths, 
                           fifths=fifths)
    
                       

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
