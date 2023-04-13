from flask import Flask, render_template, request, session, redirect, url_for, session
import re
import json
import dbconnect

app = Flask(__name__)
app.secret_key = 'pran125'


@app.route('/')
def root():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login_endpoint(): #the endpoint
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        # validate user from the database
        
        value = dbconnect.confirm_login(email,password)
        
        if value == False:
            return render_template("login.html", message="Email or Password invalid.")

        else:
            # extract all the records subscribed by the user
            session['email'] = email
            session['username'] = value
            data = dbconnect.get_subscribed_music(email)
            session['json_to_compare'] = data
            return render_template('main.html', username = session['username'], songs=data) 
        
    else:
        return render_template('login.html')
    
@app.route('/query', methods=['POST'])
def query(): #using the scan function to get the data
    title = request.form['title']
    artist = request.form['artist']
    year = request.form['year']
    
    data = dbconnect.get_query(title,artist,year)
    
    if data == False:
        print(session['json_to_compare'])
        return render_template('main.html', username = session['username'], songs=session['json_to_compare'], message="Enter atleast one parameter to search.") 
    else:
        query_data = [i for i in data if i not in session['json_to_compare']]
        print(query_data)
        return render_template("main.html", username = session['username'], songs=session['json_to_compare'], query_data=query_data)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        rpassword = request.form["rpassword"]
        
        #check if passwords match
        if password != rpassword:
            return render_template("register.html", message="Passwords do not match. Enter again.")
        
        else:
            # enter user in database
            value = dbconnect.register(email, username, password)
            if value == True:
                return render_template("login.html", message="User created successfully. Please login.")
            else:
                return render_template("register.html", message="Email already exists.")
            

    else:
        return render_template('register.html')
    

@app.route("/subscribe", methods=['POST'])
def susbcribe():
    data = dict(request.form) # artist : title
    artist = list(data)[0]
    title = data[artist]
    
    dbconnect.susbcribe_song(session['email'], title, artist)
    
    data = dbconnect.get_subscribed_music(session['email'])
    if len(data) != 0:
        session['json_to_compare'] = data
    return render_template('main.html', username = session['username'], songs=session['json_to_compare'], message='Song successfully subscribed.')

@app.route("/remove", methods=['POST'])
def remove():
    # print(request.form) #name-value
    data = dict(request.form) # artist : title
    artist = list(data)[0]
    title = data[artist]
    value = dbconnect.remove_subscription(session['email'], title, artist)
    
    # reloading main page
    data = dbconnect.get_subscribed_music(session['email'])
    session['json_to_compare'] = data
    return render_template('main.html', username = session['username'], songs=session['json_to_compare'], message='Song Removed from subscription.')

if __name__ == '__main__':
    app.run()