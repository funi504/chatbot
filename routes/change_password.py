
def change_user_password(token ,request , s , User , bcrypt ,db ,render_template):

    if request.method == 'POST':
        
        email = s.loads(token, salt='email-confirm-salt-wufksk12@58', max_age=3600)
        new_password = request.form.get("password")
        hashedPassword = bcrypt.generate_password_hash(new_password)
        user = User.query.filter_by(email=email).first()

        user.password = hashedPassword
        db.session.commit()
        #return '<h1>password changed</h1>'


    if request.method == 'GET':

        url = f"/change_password/{token}"
        return render_template("input.html",action = url)

    return render_template("chat.html")