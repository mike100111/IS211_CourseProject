import os
import sqlite3
import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'theblog.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('THEBLOG_SETTINGS', silent=True)

###Database####

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
	
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
		
##############

####User Control####

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_posts'))
    return render_template('login.html', error=error)
	
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_posts'))
	
##############

####Views#####		

@app.route('/dashboard')
def show_posts():
    db = get_db()
    cur = db.execute('select id, title, content, published, strftime("%H:%M %m-%d-%Y ", published) As "PublishedDate", author from post where display = 1 order by id desc')
    posts = cur.fetchall()
    return render_template('show_posts.html', posts=posts)
	
@app.route('/add', methods=['POST'])
def add_post():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into post (title, content, published, author, display) values (?, ?, ?, ?, ?)',[request.form['title'], request.form['content'], datetime.datetime.now(), 'admin', '1'])
    db.commit()
    flash('New post was successfully posted')
    return redirect(url_for('show_posts'))
	

@app.route("/edit", methods=['POST'])
def edit_post():
	
	db = get_db()
	if request.form['submit'] == 'Delete':		
		cur = db.execute('delete from post where id = ?', [request.form['id'],])		
		db.commit()
		flash('Post deleted')
		return redirect(url_for('show_posts'))	
	else:
		cur = db.execute('select id, title, content, published from post where display = 1 and id = ? limit 1', [request.form['id'],])
		post = cur.fetchall()
		return render_template('edit_post.html', post=post[0])	
	
@app.route('/update', methods=['POST'])
def update_post():
	if request.form['submit'] == 'Cancel':
		flash('Update canceled')
		
	else:
		db = get_db()
		db.execute('update post set title = ?, content = ? where id = ?',[request.form['title'], request.form['content'], request.form['id']])
		db.commit()
		flash('Post was successfully updated')
	return redirect(url_for('show_posts'))

if __name__ == "__main__":
    app.run()
	