def login_user(configEmail,app,request,User,bcrypt,jsonify,Message,s,url_for,mail,session,flask):

    # Configure Flask-Mail here
    #configure email to send verification email
    configEmail(app)
    email =  request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None :
        return jsonify({"error": "unauthorized"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "unauthorized"}), 401

    if user.confirmed == False:

        token = s.dumps(email, salt='email-confirm-salt-wufksk12@58')

        msg = Message('Confirm Email', sender='nekhungunifunanani9@gmail.com', recipients=[email])

        link = url_for('confirm_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        return jsonify({"error": "confirm email first , confirm email sent"})

    session["user_id"] = user.id
    flask.session["userId"] = user.id

    return jsonify({
        "id": user.id,
        "email": user.email,
        "domain" : user.domain,
        "confirmed": user.confirmed
    })