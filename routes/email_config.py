
def emailConfiguration(request, session, EmailConfig ,jsonify , Project , db ):

    data = request.get_json()
    project_id = data['project_id']
    user_id =session.get("user_id")
    
    if request.method== 'GET' :
        
        configData = EmailConfig.query.filter_by(project_id=project_id).first()
        if not configData:
            return jsonify({'error':'config not found'}),401
        return jsonify({
            "email": configData.email,
            "provider": configData.provider,
            "projectId": project_id
        })
    
    if request.method== 'POST' :
        
        try:
            if not user_id:
                return jsonify({"error":"not authorized"}),401
            
            email = data['email']
            provider = data['provider']
            password = data['password']
            project_id = data['project_id']
            config = EmailConfig.query.filter_by(project_id=project_id).first()
            project = Project.query.filter_by(project_id = project_id).first()

            if not project:
                return jsonify({"error":"not authorized"}),401

            if not config:
                new_emailConfig = EmailConfig(email=email , provider=provider , password=password,
                            project_id=project_id, user_id=user_id
                            )
                db.session.add(new_emailConfig)
                db.session.commit()

                return jsonify({
                "email": new_emailConfig.email,
                "provider": new_emailConfig.provider
                })
            

            config = EmailConfig.query.filter_by(project_id=project_id).first()
            config.email = email
            config.provider = provider
            config.password = password

            db.session.commit()

            return jsonify({
                "email": config.email,
                "provider": config.provider
                })
        except:
            return jsonify({"error":"the was an error"}),404

    if request.method == 'PUT':
        data = request.get_json()
        user_id =session.get("user_id")

        try:
            if not user_id:
                return jsonify({"error":"not authorized"})
            
            email = data['email']
            provider = data['provider']
            password = data['password']
            project_id = data['project_id']

            config = EmailConfig.query.filter_by(project_id=project_id).first()
            config.email = email
            config.provider = provider
            config.password = password

            db.session.commit()


        except:
            return 404

    if request.method == "DELETE":
        try:
            config = EmailConfig.query.filter_by(project_id=project_id).first()
            db.session.delete(config)
            db.session.commit()

            return jsonify({"message": "the config has been deleted"})
        except:
            return jsonify({"error":"config  not found"})