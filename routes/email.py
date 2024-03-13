
def send_email_to_user(request, EmailConfig , app , Mail , Message ,jsonify):
    #get data from form
    data = request.get_json()
    try:
        print(data)
        #get project id from 
        project_id = data['project_id']
        
        #email template
        sender_name = data['name']
        sender_email = data['email']
        sender_message = data['message']

        #get email config data of the onwer of the project from the main server
        #project_id = request.get_json(['project_id'])

        configData = EmailConfig.query.filter_by(project_id=project_id).first()

        print(configData)
        
        config_email = configData.email
        config_provider = configData.provider
        config_password = configData.password

        # Configure Flask-Mail here
        app.config['MAIL_SERVER'] = str(config_provider)
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = str(config_email)
        app.config['MAIL_PASSWORD'] = str(config_password)

        mail = Mail(app)

        

        subject= f"Message from {sender_name}"
        body = f"Sender's Email: {sender_email}\n\nMessage: {sender_message}"

        # Create and send the email
        #msg = Message(subject=subject, sender='nekhungunifunanani9@gmail.com', recipients=['nekhungunifunanani9@gmail.com'])
        msg = Message(subject=subject, sender= config_email , recipients=[ config_email ])
        msg.body = body
        mail.send(msg)

        return jsonify({"response":"email sent"})
    except Exception as e :

        return jsonify({"response": e })