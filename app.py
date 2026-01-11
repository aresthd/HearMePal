import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from utils.chatbot import ChatBot
from model.Message import Message
from model.Conversation import Conversation
from model.User import User
from model.Preference import Preference
from model.Model import Model
from model.Language import Language
from datetime import timedelta
from urllib.parse import urlparse

# Memuat file .env
load_dotenv()

app = Flask(__name__)

# Menggunakan variabel dari file .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PATH_INTENTS'] = os.getenv('PATH_INTENTS')
app.config['PATH_DATA'] = os.getenv('PATH_DATA')
app.config['DATABASE_HOST'] = os.getenv('DATABASE_HOST')
app.config['DATABASE_USER'] = os.getenv('DATABASE_USER')
app.config['DATABASE_PASS'] = os.getenv('DATABASE_PASS')
app.config['DATABASE_NAME'] = os.getenv('DATABASE_NAME')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

chatbot = ChatBot(app.config['PATH_INTENTS'], app.config['PATH_DATA'])
message = Message(app.config['DATABASE_HOST'], app.config['DATABASE_USER'], app.config['DATABASE_PASS'], app.config['DATABASE_NAME'])
conversation = Conversation(app.config['DATABASE_HOST'], app.config['DATABASE_USER'], app.config['DATABASE_PASS'], app.config['DATABASE_NAME'])
user = User(app.config['DATABASE_HOST'], app.config['DATABASE_USER'], app.config['DATABASE_PASS'], app.config['DATABASE_NAME'])
preference = Preference(app.config['DATABASE_HOST'], app.config['DATABASE_USER'], app.config['DATABASE_PASS'], app.config['DATABASE_NAME'])
model = Model(app.config['DATABASE_HOST'], app.config['DATABASE_USER'], app.config['DATABASE_PASS'], app.config['DATABASE_NAME'])
language = Language(app.config['DATABASE_HOST'], app.config['DATABASE_USER'], app.config['DATABASE_PASS'], app.config['DATABASE_NAME'])

# Home Page
@app.route("/")
@app.route("/index")
def index():
    data = {
        'page' : 'Home',
        'current_page' : 'home',
        'has_login' : False
    }
    
    user_id = session.get("user_id")
    if user_id != None:
        data['has_login'] = True
    
    return render_template("pages/index.html", data=data)

# About Page
@app.route("/about")
def about():
    data = {
        'page' : 'About',
        'current_page' : 'about',
        'has_login' : False
    }

    user_id = session.get("user_id")
    if user_id != None:
        print(f"\n---------REGISTER ACCESS------")
        print(f"user_id : {user_id} \n\n")
        return redirect("/chat")
    
    return render_template("pages/about.html", data=data)

# Login Page
@app.route("/login", methods=['GET'])
def login():
    user_id = session.get("user_id")
    if user_id != None:
        print(f"\n---------LOGIN ACCESS------")
        print(f"user_id : {user_id} \n\n")
        return redirect("/chat")
    
    data = {
        'page' : 'Login',
        'current_page' : 'login',
    }
    
    return render_template("pages/login.html", data=data)

# Login Process
@app.route("/login", methods=['POST'])
def login_user():
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    
    result = user.login(email, password)
    print(f"\n {type(result)}\n\n")
    if isinstance(result, dict):
        session["user_id"] = result['user_id']
        print(f"\n {session['user_id']}\n\n")
        flash('Login successfully.', ['success', 'bottom'])
        return redirect('/chat')
    else:
        print(f'\n {result}\n\n')
        flash(result, ['warning', 'bottom'])
        return redirect('/login')

# Regsiter Page
@app.route("/register", methods=['GET'])
def register():
    user_id = session.get("user_id")
    if user_id != None:
        return redirect("/chat")
    
    data = {
        'page' : 'Register',
        'current_page' : 'register',
    }
    
    return render_template("pages/register.html", data=data)

# Regist Process
@app.route("/register", methods=['POST'])
def regist():
    full_name = request.form.get('full_name', None)
    username = request.form.get('username', None)
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    confirm_password = request.form.get('confirm_password', None)
    
    result = user.register_user(username, email, full_name, password, confirm_password)
    if result == True:
        print(f'\n User {username} berhasil dibuat\n\n')
        new_user_id = user.get_user_by_username(username)['user_id']
        latest_model_id = model.get_latest_model()['model_id']
        oldest_lang_id = language.get_oldest_language()['language_id']
        res_pref = preference.create_preference(new_user_id, oldest_lang_id, latest_model_id)
        if res_pref == True:
            print(f'\n Preference of {username} berhasil dibuat\n\n')
            flash('Account created successfully.', ['success', 'top'])
            return redirect('/login')
        else:
            print(f'\n Preference of {username} gagal dibuat\n\n')
            flash(result, ['warning', 'top'])
            return redirect('/register')
    else:
        print(f'\n User {username} gagal dibuat\n\n')
        flash(result, ['warning', 'top'])
        return redirect('/register')
    
@app.route('/logout')
def logout():
    # Remove the username from the session if it's there
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Chat Page
@app.route("/chat", methods=['GET'])
@app.route("/chat/<int:conv>", methods=['GET'])
def chat(conv=None):
    data = {
        'page' : 'Chat',
        'current_page' : 'chat',
        'user' : False,
        'now_conversation' : False,
        'active_conversations' : False,
        'archived_conversations' : False
    }
    user_id = session.get("user_id")
    
    # User login and go to spesific conv
    if conv != None and user_id != None:
        data['user'] = user.get_user_by_id(user_id)
        data['active_conversations'] = conversation.get_all_conversation('active', user_id)
        data['archived_conversations'] = conversation.get_all_conversation('archived', user_id)
        data['now_conversation'] = conversation.get_conversation(conv, user_id)
        if data['now_conversation'] == None:
            conv = conversation.get_latest_conversation(user_id, 'active')['conversation_id']
            return redirect(f"/chat/{conv}")
        data['messages'] = message.get_all_messages(conv)
    
    # User not login and go to spesific conv
    elif conv != None and user_id == None:
        return redirect("/login")
    
    # User login and go to default conv
    elif conv == None and user_id != None:
        conv = conversation.get_latest_conversation(user_id, 'active')
        if conv == None:
            return redirect(f"/new")
        conv = conv['conversation_id']
        return redirect(f"/chat/{conv}")
    
    # User not login and go to default conv
    else:
        pass
        
    return render_template("pages/chat.html", data=data)

# Get Response
@app.route("/get")
def get_bot_response():
    user_message = request.args.get('msg')
    response = chatbot.get_response(user_message)
    conversation_id = int(request.args.get('conv', None))
    
    print(f'\n conversation_id: {conversation_id} \n\n')
    if conversation_id > 0:
        message.insert_message(conversation_id, 'user', user_message)
        message.insert_message(conversation_id, 'bot', response)

    return response

# New Conversation
@app.route("/new")
def add_conv():
    user_id = session.get("user_id")
    print(f'\n user_id : {user_id}')
    print(f'\n type(user_id) : {type(user_id)}')
    
    if user_id == None:
        return redirect("/login")
    
    status = conversation.create_conversation(user_id)
    if status == True:
        new_conv = conversation.get_latest_conversation(user_id)['conversation_id']
        flash('Create conversation successfully.', ['success', 'bottom'])
        return redirect(f"/chat/{new_conv}")
    else:
        previous_path = urlparse(request.referrer).path
        flash('Create conversation failed.', ['danger', 'bottom'])
        return redirect(previous_path)

# Rename Conversation
@app.route("/chat/<int:conv>/edit", methods=['POST'])
def edit_conv(conv):
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
        
    title = request.form.get('title', None)
    if title != None:
        conversation.edit_conversation(conv, user_id, title)
        print(f'\nSuccess edit title\n\n')
        
    return redirect(f'/chat/{conv}')

# Archive Conversation
@app.route("/chat/<int:conv>/archive", methods=['GET'])
def archive_conv(conv):
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    conversation.end_conversation(conv, user_id)
    print(f'\nSuccess archive conversation id={conv}\n\n')
    flash('Success archive conversation.', ['success', 'bottom'])
    
    conv = conversation.get_latest_conversation(user_id, 'active')['conversation_id']
    
    previous_path = urlparse(request.referrer).path
    path_segments = previous_path.split('/')
    path_first_segments = path_segments[1] if len(path_segments) > 1 else None
    conv_id_before = path_segments[2] if len(path_segments) > 2 else None
    
    if path_first_segments == 'chat' and conv_id_before != None:
        conv_before = conversation.get_conversation(conv_id_before, user_id)
        if conv_before is not None and conv_before['ended_at'] is None:
            return redirect(f'/{path_first_segments}/{conv_id_before}')
        else:
            return redirect(f'/chat/{conv}')
    elif path_first_segments == 'setting':
        return redirect(f'/{path_first_segments}')
    else:
        return redirect(previous_path)
    
# Unarchive Conversation
@app.route("/chat/<int:conv>/unarchive", methods=['GET'])
def unarchive_conv(conv):
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    conversation.start_conversation(conv, user_id)
    print(f'\nSuccess Unarchive conversation id={conv}\n\n')
    flash('Success Unarchive conversation.', ['success', 'bottom'])
    
    conv = conversation.get_latest_conversation(user_id, 'active')['conversation_id']
    
    previous_path = urlparse(request.referrer).path
    path_segments = previous_path.split('/')
    path_first_segments = path_segments[1] if len(path_segments) > 1 else None
    conv_id_before = path_segments[2] if len(path_segments) > 2 else None
    
    if path_first_segments == 'chat' and conv_id_before != None:
        conv_before = conversation.get_conversation(conv_id_before, user_id)
        if conv_before is not None and conv_before['ended_at'] is None:
            return redirect(f'/{path_first_segments}/{conv_id_before}')
        else:
            return redirect(f'/chat/{conv}')
    elif path_first_segments == 'setting':
        return redirect(f'/{path_first_segments}')
    else:
        return redirect(previous_path)

# Delete Conversation
@app.route("/chat/<int:conv>/delete", methods=['POST'])
def delete_conv(conv):
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    delete = request.form.get('delete', None)
    if delete != None:
        conversation.delete_conversation(conv, user_id)
        print(f'\nSuccess delete conversation id={conv}\n\n')
        flash('Success delete conversation.', ['success', 'bottom'])
        
        conv = conversation.get_latest_conversation(user_id, 'active')['conversation_id']
        
        previous_path = urlparse(request.referrer).path
        path_segments = previous_path.split('/')
        path_first_segments = path_segments[1] if len(path_segments) > 1 else None
        conv_id_before = path_segments[2] if len(path_segments) > 2 else None
        
        if path_first_segments == 'chat' and conv_id_before != None:
            conv_before = conversation.get_conversation(conv_id_before, user_id)
            if conv_before is not None and conv_before['ended_at'] is None:
                return redirect(f'/{path_first_segments}/{conv_id_before}')
            else:
                return redirect(f'/chat/{conv}')
        elif path_first_segments == 'setting':
            return redirect(f'/{path_first_segments}')
        else:
            return redirect(previous_path)
        
    return redirect(f'/chat/{conv}')


# Setting Page
@app.route("/setting")
def setting():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    user_preference = preference.get_preferences_by_user_id(user_id)
    
    data = {
        'page' : 'Setting',
        'current_page' : 'setting',
        'active_conversations' : conversation.get_all_conversation('active', user_id),
        'archived_conversations' : conversation.get_all_conversation('archived', user_id),
        'all_conversations' : conversation.get_all_conversation('all', user_id),
        'all_models' : model.get_all_models(),
        'all_languages' : language.get_all_languages(),
        'user' : user.get_user_by_id(user_id),
        'user_preference' : user_preference,
        'model_preference' : model.get_model(user_preference['model_id']),
        'lang_preference' : language.get_language(user_preference['language_id']),
        'now_conversation' : False,
        'archived_chats' : conversation.get_archived_conversations(user_id)
    }
    
    print(f"\n data['active_conversations'] : {data['active_conversations']} \n\n")
    print(f"\n data['now_conversation'] : {data['now_conversation']} \n\n")
    
    return render_template("pages/setting.html", data=data)

# Profile Edit Process
@app.route("/profile/edit", methods=['POST'])
def profile_edit():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    full_name = request.form.get('full_name', None)
    username = request.form.get('username', None)
    email = request.form.get('email', None)
    
    if full_name != None and username != None and email != None:
        status = user.update_user_details(user_id, username, full_name, email)
        if status == True:
            flash("Profile updated successfully.", ['success', 'bottom'])
            return redirect('/setting')
        else:
            flash("Profile update failed.", ['danger', 'bottom'])
            return redirect('/setting')
    else:
        flash("Please fill out the field.", ['warning', 'bottom'])
        return redirect('/setting')

# Passowrd Update Process
@app.route("/profile/update-pass", methods=['POST'])
def update_pass():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    old_password = request.form.get('old_password', None)
    new_password = request.form.get('new_password', None)
    confirm_password = request.form.get('confirm_password', None)
    
    if old_password != None and new_password != None and confirm_password != None:
        result = user.update_user_password(user_id, old_password, new_password, confirm_password)
        if result == True:
            flash("Password updated successfully.", ['success', 'bottom'])
            return redirect('/setting')
        else:
            flash(result, ['danger', 'bottom'])
            return redirect('/setting')
    else:
        flash("Please fill out the field.", ['warning', 'bottom'])
        return redirect('/setting')


# Model Preference Edit Process
@app.route("/model/edit", methods=['POST'])
def model_edit():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    new_model = request.form.get('new_model', None)
    user_preference = preference.get_preferences_by_user_id(user_id)

    if new_model != None:
        status = preference.update_preference(preference_id=user_preference['preference_id'], model_id=new_model)
        if status == True:
            flash("Model Preference update successfully.", ['success', 'bottom'])
            return redirect('/setting')
        else:
            flash("Model Preference update failed.", ['danger', 'bottom'])
            return redirect('/setting')
    else:
        flash("Please fill out the field.", ['warning', 'bottom'])
        return redirect('/setting')
            
# Language Preference Edit Process
@app.route("/lang/edit", methods=['POST'])
def lang_edit():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    new_lang = request.form.get('new_lang', None)
    user_preference = preference.get_preferences_by_user_id(user_id)

    if new_lang != None:
        status = preference.update_preference(preference_id=user_preference['preference_id'], language_id=new_lang)
        if status == True:
            flash("Language Preference update successfully.", ['success', 'bottom'])
            return redirect('/setting')
        else:
            flash("Language Preference update failed.", ['danger', 'bottom'])
            return redirect('/setting')
    else:
        flash("Please fill out the field.", ['warning', 'bottom'])
        return redirect('/setting')
            
        


# Archive All Conversation
@app.route("/chat/archive-all", methods=['POST'])
def archive_all_conv():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    conversation.end_all_conversation(user_id)
    print(f'\nSuccess archive all conversations \n\n')
    return redirect(f'/setting')

# Delete All Conversation
@app.route("/chat/delete-all", methods=['POST'])
def delete_all_conv():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect("/login")
    
    delete = request.form.get('delete', None)
    if delete != None:
        conversation.delete_all_conversation(user_id)
        print(f'\nSuccess delete all conversations \n\n')
        
    return redirect(f'/setting')
    

        

# @app.route("/conv/<int:value>")
# def conversation(value):
#     return f'The value is {value}'


if __name__ == '__main__':
    app.run(debug=True, port=5050)