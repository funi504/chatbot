
# Using regex, gt and length validators 
import gladiator as gl 

def register_user( configEmail , app ,request ,bcrypt ,User, jsonify ,db , s , Message ,url_for ,mail , datetime):
    try:
        #configure email to send verification email
        configEmail(app)
        email =  request.json["email"]
        domain = request.json["domain"]
        password = request.json["password"]
        print(email)

        data = {
            'email':email,
            'domain': domain,
            'password':password
        }

        field_validations = ( 
                ('email', gl.required, gl.format_email), 
                ('password', gl.required, gl.length_min(5)), 
                ('domain', gl.required, gl.type_(str))
            )

        if not gl.validate(field_validations, data) :
            return jsonify({"error": "validation error",})


        hashedPassword = bcrypt.generate_password_hash(password)
        date =  datetime.date.today()

        user_exists = User.query.filter_by(email=email).first() is not None

        if user_exists:
            return jsonify({"error": "email already exists"}), 409

        new_user = User(email=email , domain=domain , password=hashedPassword,
                        created_on=date, 
                        )
        db.session.add(new_user)
        db.session.commit()

        #session["user_id"] = new_user.id

        token = s.dumps(email, salt='email-confirm-salt-wufksk12@58')

        msg = Message('Confirm Email', sender='nekhungunifunanani9@gmail.com', recipients=[email])

        link = url_for('confirm_my_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        return jsonify({
            "id": new_user.id,
            "email": new_user.email,
            "domain" : new_user.domain,
            "message":"email confirmation sent , confirm email before 1 hours"
        })

    except Exception as e :
        print(e)
        return jsonify({"error": "the was an error registering your account",})
