import json 
import os

def create_project(session , Project , request , jsonify , db ):
    user_id =session.get("user_id")

    if request.method == "POST":
        try:
            if not user_id:
                return jsonify({"error":"unauthorized"}),401
            
            project_name = request.json["Name"]

            new_project = Project(user_id=user_id ,project_name=project_name)
            db.session.add(new_project)
            db.session.commit()

            #Todo: create a json file
            filename ="intent/"+new_project.project_id+".json"
            intent_data= open("intent/86477e97c27543f7ac24f14770f79b86.json" , "r")
            data = json.load(intent_data)
            intent_data.close()
            #add contents to the file
            save_file = open(filename,"w")
            json.dump(data ,save_file, indent=6)
            save_file.close()


            return jsonify({
                "Name": new_project.project_name,
                "project_Id": new_project.project_id,
                "user_Id": new_project.user_id

            })
        except Exception as e:
            print(e) 
            return jsonify({ "error": "something went wrong , try later"})
    
    if request.method == "GET":
        project = Project.query.filter_by(user_id=user_id).first()

        if not user_id:
            return jsonify({"error":"no project found"}),401

        if not project:
            return jsonify({"error":"unauthorized, no project id found"}),401

        return jsonify({

            "projectName": project.project_name,
            "projectId": project.project_id,
            "userId": project.user_id,
        })

    if request.method == "DELETE":
        try:
            project = Project.query.filter_by(user_id=user_id).first()
            project_id = project.project_id

            if not user_id:
                return jsonify({"error":"unauthorized"}),401

            if not project_id:
                return jsonify({"error":"unauthorized"}),401
            
            #delete project , intent file and bot model
            intent_path = project_id +"json"
            bot_path = project_id + ".pth"

            if os.path.exists(intent_path):
                os.remove(intent_path)

            if os.path.exists(bot_path):
                os.remove(bot_path)

            
            project = Project.query.filter_by(user_id=user_id).delete()
            db.session.commit()

            return jsonify({"message": "the project has been deleted"})
        
        except:
            return jsonify({ "error": "something went wrong , try later"})
        

    if request.method == "PUT":
        try:
            project = Project.query.filter_by(user_id=user_id).first()

            if not user_id:
                return jsonify({"error":"unauthorized"}),401

            if not project:
                return jsonify({"error":"unauthorized"}),401
            
            name = request.json["Name"]
            project.project_name = name
            db.session.commit()

            return jsonify({
                "Name": project.project_name,
                "project_Id": project.project_id,
                "user_Id": project.user_id

            })

        except Exception as error:
            print(error)
            return jsonify({ "error": "something went wrong , try later"})