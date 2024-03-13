def confirm_user_email(token , s ,User ,db , datetime , SignatureExpired):

    try:
        email = s.loads(token, salt='email-confirm-salt-wufksk12@58', max_age=3600)
        user = User.query.filter_by(email=email).first()
        user.confirmed = True
        user.confirmed_on = datetime.date.today()
        db.session.commit()

    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    return '<h1>email has been verified!, you can now log in</h1>'