
def forgot_user_password(configEmail , app , request , s ,Message , url_for , mail , jsonify):

    configEmail(app)
    email =  request.json["email"]
    try:
        token = s.dumps(email, salt='email-confirm-salt-wufksk12@58')

        msg = Message('Change password', sender='nekhungunifunanani9@gmail.com', recipients=[email])

        link = url_for('change_password', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        return jsonify({ "message": "change password email has been sent"})
    
    except :
        
        return jsonify({"error": "something went wrong"})