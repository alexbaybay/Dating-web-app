import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, current_app, jsonify
from dating import app, db, bcrypt
from dating.forms import RegistrationForm, LoginForm, EditProfileForm, MessageForm
from dating.models import *
from flask_login import login_user, current_user, logout_user, login_required
from dating.queries import *
from dating.matcher import *
import datetime


@app.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/home")
@login_required
def home():
    users_stack = User.query.all()
    exists = db.session.query(db.exists().where(Interest.interest_id == current_user.id)).scalar()
    if exists==False:
        return redirect(url_for('add_interests'))
    return render_template('home.html', users_stack=users_stack)

@app.route("/about")
@login_required
def about():
    return render_template('about.html', title='About')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilepics', picture_fn)

    output_size = (568, 528)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def clean_time(str_tme):
    """ Helper function to clean a string that comes from the html date input """

    chars = str_tme.split('T')
    tm = (" ").join(chars)
    return tm + ":00"


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                firstname=form.firstname.data, lastname=form.lastname.data, date_of_birth=form.date_of_birth.data,
                city=form.city.data, phone=form.phone.data)
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  #checks if user is logged in
        return redirect(url_for('home'))    #redirect to the home page
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  #The result of filter_by() is a query that only includes the objects that have a matching username. complete query by calling first(), returns the user object if it exists,None if it does not.
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/account")
@login_required
#Allows a user to view their account profile only if they are logged in
def account():

    selected_interests = []

    user_interests = Interest.query.filter_by(interest_id=current_user.id).first()

    user_book_genre_id = user_interests.book_genre_id
    user_movie_genre_id = user_interests.movie_genre_id
    user_music_genre_id = user_interests.music_genre_id
    user_fav_cuisine_id = user_interests.fav_cuisine_id
    user_hobby_id = user_interests.hobby_id
    user_outdoor_id = user_interests.outdoor_id
    user_religion_id = user_interests.religion_id

    bookname = BookGenre.query.filter_by(book_genre_id=user_book_genre_id).first()
    moviename = MovieGenre.query.filter_by(movie_genre_id=user_movie_genre_id).first()
    musicname = MusicGenre.query.filter_by(music_genre_id=user_music_genre_id).first()
    cuisinename = FavCuisine.query.filter_by(fav_cuisine_id=user_fav_cuisine_id).first()
    hobbyname = Hobby.query.filter_by(hobby_id=user_hobby_id).first()
    outdoorname = Outdoor.query.filter_by(outdoor_id=user_outdoor_id).first()
    religionname = Religion.query.filter_by(religion_id=user_religion_id).first()

    selected_interests.append(bookname.book_genre_name)
    selected_interests.append(moviename.movie_genre_name)
    selected_interests.append(musicname.music_genre_name)
    selected_interests.append(cuisinename.fav_cuisine_name)
    selected_interests.append(hobbyname.hobby_name)
    selected_interests.append(outdoorname.outdoor_activity)
    selected_interests.append(religionname.religion_name)

    return render_template('account.html', title='Account', selected_interests=selected_interests)

@app.route("/profile/<user>", methods=['GET', 'POST'])
@login_required
#Allows a user to view other user's profile page
def profile(user):
    selected_user=User.query.filter_by(username=user).first()
    user = selected_user.username
    return render_template('profile.html', selected_user=selected_user, user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.profilepic.data:
            picture_file = save_picture(form.profilepic.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.city = form.city.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.city.data = current_user.city
        form.phone.data = current_user.phone
        flash('Your photo has been uploaded! It is now your profile pic', 'success')
    image_file = url_for('static', filename='profilepics/' + current_user.image_file)
    return render_template('profileform.html', title='Edit Profile', form=form, image_file=image_file)

@app.route('/add_interests', methods=['GET', 'POST'])
@login_required
def add_interests():
    #form = InterestForm()
    all_interests = [all_book_genres(), all_movie_genres(),all_music_genres(),all_fav_cuisines(),all_hobbies(),
    all_religions(),all_outdoors()]

    user_id = current_user.id
    book_genre_id = request.form.get("Favorite book genre")
    movie_genre_id = request.form.get("Favorite movie genre")
    music_genre_id = request.form.get("Favorite music genre")
    fav_cuisine_id = request.form.get('Preferred cuisine type')
    hobby_id = request.form.get('Favorite hobby')
    outdoor_id = request.form.get('Favorite Outdoor activity')
    religion_id = request.form.get('Religion')

    if request.method == 'POST':
          #add user interests for the specific user
        interest = Interest(
            user_id=user_id,
            book_genre_id=book_genre_id,
            movie_genre_id=movie_genre_id,
            music_genre_id=music_genre_id,
            fav_cuisine_id=fav_cuisine_id,
            hobby_id=hobby_id,
            outdoor_id=outdoor_id,
            religion_id=religion_id
        )

        db.session.add(interest)
        db.session.commit()
        return redirect(url_for('account'))


    return render_template('interestform.html', title='Add Interests', all_interests=all_interests)

@app.route('/edit_interests', methods=['GET', 'POST'])
@login_required
def edit_interests():

    all_interests = [all_book_genres(), all_movie_genres(),all_music_genres(),all_fav_cuisines(),all_hobbies(),
    all_religions(),all_outdoors()]

    user_id = current_user.id
    book_genre_id = request.form.get("Favorite book genre")
    movie_genre_id = request.form.get("Favorite movie genre")
    music_genre_id = request.form.get("Favorite music genre")
    fav_cuisine_id = request.form.get('Preferred cuisine type')
    hobby_id = request.form.get('Favorite hobby')
    outdoor_id = request.form.get('Favorite Outdoor activity')
    religion_id = request.form.get('Religion')

    user_interest = Interest.query.filter_by(interest_id=user_id).first()

    if request.method == 'POST':
        #find the user interest corresponding to the user_id
        #edit that interest
        user_interest.book_genre_id = book_genre_id
        user_interest.movie_genre_id = movie_genre_id
        user_interest.music_genre_id = music_genre_id
        user_interest.fav_cuisine_id = fav_cuisine_id
        user_interest.hobby_id = hobby_id
        user_interest.outdoor_id = outdoor_id
        user_interest.religion_id = religion_id

        db.session.commit()
        return redirect(url_for('account'))

    return render_template('editinterests.html', title='Edit Interests', all_interests=all_interests)

@app.route('/generate_matches', methods=["GET"])
@login_required
def show_generate_matches_form():
    """Route for users to enter their zipcode and a time for meeting up!!.
    """

    return render_template("generate_matches.html")

@app.route('/generate_matches', methods=["POST"])
@login_required
def generate_matches():
    """This route
    - gets the time from the user who is logged in
    - gets the zipcode from the user
    """

    query_time = request.form.get('triptime')
    query_pin_code = request.form.get('pincode')
    user_id = session['user_id']
    #if this user is in the database for the same exact date, then go to show_matches
    session['query_pincode'] = query_pin_code
    session_time = clean_time(query_time)
    session['query_time'] = session_time

    date_out = datetime.datetime(*[int(v) for v in query_time.replace('T', '-').replace(':', '-').split('-')])

    trip =  PendingMatch(user_id=user_id,
                        query_pin_code=query_pin_code,
                        query_time=date_out,
                        pending=True)

    db.session.add(trip)
    db.session.commit()

    #at this point we will pass the information the yelper
    #yelper will end information to google and google will render
    # a map with relevant information

    return redirect("show_matches")

@app.route('/show_matches',methods=['GET'])
@login_required
def show_potential_matches():
    """ This route
        - accesses the session for a user_id and query_pin_code
        - accesses the matchmaker module for making matches
        -
    """

    # gets the user_id from the session
    userid = current_user.id
    # gets the pincode from the session
    pin = session.get('query_pincode')
    # gets the query_time from the session
    query_time = session.get('query_time')
    # gets a list of pending matches using the potential_matches from
    # the matchmaker module
    # potential_matches is  a list of user_ids
    # => [189, 181, 345, 282, 353, 271, 9, 9, 501, 9]
    potential_matches = find_valid_matches(userid, pin, query_time)

    # gets a list of tuples of match percents for the userid
    # uses the create_matches from the matchmaker
    # create_matches takes a list of user_ids as the first param
    # create_matches take the userid as the second param
    # create_matches([30,40,50],60)
    # => [(60, 30, 57.90407177363699), (60, 40, 54.887163561076605)]
    match_percents = create_matches(potential_matches, userid)

    user_info = get_user_info(userid)
    # this is the logged in user's info
    user_name = get_user_name(userid)
    # this is the logged in user's username

    match_info = []

    for user in match_percents:
        matched_username = get_user_name(user[1])
        user_info = get_user_info(user[1])
        matched_user_id = user[1]
        match_percent = round(user[2])
        #match_details = get_commons(user[1], userid)

        match_info.append((matched_username, match_percent,
                        matched_user_id, user_info))

    # match info is a list of tuples [(username,
    #                               match_percent,
    #                               matched_user_id,
    #                                user_info, match_details)]


    return render_template('show_matches.html',
                                user_name=user_name,
                                user_info=user_info,
                                match_info=match_info)

@app.route('/show_matches', methods=["POST"])
@login_required
def update_potential_matches():
    """ - Gets the user input for a confirm match
        - Updates the user input for a match to the db
    """


    matched = request.form.get("user_match")
    user_id_1 = current_user.id
    match_date = datetime.datetime.now()
    query_pincode = session['query_pincode']
    session['matched_user'] = matched


    match = UserMatch(user_id_1=user_id_1,
                    user_id_2=matched,
                    match_date=match_date,
                    user_2_status=False,
                    query_pincode=query_pincode)

    db.session.add(match)
    db.session.commit()
    return redirect('/confirmed')

@app.route('/match_console', methods=["POST"])
@login_required
def show_match_details():
    """ This route
        - displays the final match of user's choice
        - shows all the common interests to the user
        - gives the user a chance to message the match
        - gives the user a chance to choose a coffee shop
    """

    userid1 = current_user.id
    userid2 = request.form.get("match_details")
    user_info1 = get_user_info(userid1)
    username1 = get_user_name(userid1)
    user_info2 = get_user_info(userid2)
    username2 = get_user_name(userid2)
    match_info = get_commons(userid1, userid2)
    match_percent = round(make_match(userid1, userid2))

    return render_template("match_console.html", user_info1=user_info1,
                                                    username1=username1,
                                                    username2=username2,
                                                    user_info2=user_info2,
                                                    match_info=match_info,
                                                    match_percent=match_percent)

@app.route("/confirmed", methods=['GET'])
@login_required
def confirmed():
    return render_template('confirmed.html')

@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    recipient = user
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(sender=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('show_potential_matches', username=recipient))
    return render_template('send_message.html', title='Send Message',
                           form=form, recipient=recipient)

@app.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])
