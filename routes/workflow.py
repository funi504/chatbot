import json

def workflow(session , Project , request , Workflow , jsonify ,db ):
    user_id =session.get("user_id")
    if user_id is None:
        return jsonify({"error":"unauthorized"}),401

    if request.method == 'GET':
        
        
        try:
            project = Project.query.filter_by(user_id=user_id).first()
            workflow = Workflow.query.filter_by(user_id=user_id).first()

            if not user_id:
                return jsonify({"error":"unauthorized"}),401
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                return jsonify({
                    "nodes":[],
                    "edges":[]
                })
            
            return jsonify({
                "nodes": json.loads(workflow.nodes),
                "edges": json.loads(workflow.edges)
            })
            

        except Exception as e:
            print(e)
            return jsonify({"error":" something went wrong, try later"})

    if request.method == "POST":

        project = Project.query.filter_by(user_id=user_id).first()
        workflow = Workflow.query.filter_by(user_id=user_id).first()

        data = request.get_json()
        nodes = json.dumps(data['nodes'])
        edges = json.dumps(data['edges'])
        
        try:
            if not user_id:
                return jsonify({"error":"unauthorized"}),401
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                project_id = project.project_id
                new_workflow = Workflow(user_id=user_id ,project_id=project_id, nodes=nodes, edges=edges)
                db.session.add(new_workflow)
                db.session.commit()
            
                return jsonify({
                    "nodes":json.loads(new_workflow.nodes),
                    "edges": json.loads(new_workflow.edges),
                    "message": "first workflow"
                })
            
            workflow.nodes = nodes
            workflow.edges = edges
            db.session.commit()
            print(workflow.nodes)
            return jsonify({
                    "nodes":json.loads(workflow.nodes),
                    "edges":json.loads(workflow.edges),
                    "message": "workflow updated"
                })
            

        except Exception as e:
            print(e)
            return jsonify({"error":" something went wrong, try later"})

    if request.method == "DELETE":
        project = Project.query.filter_by(user_id=user_id).first()
        workflow = Workflow.query.filter_by(user_id=user_id)
        
        try:
            if not user_id:
                return jsonify({"error":"unauthorized"}),401
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            workflow = Workflow.query.filter_by(user_id=user_id).delete()
            db.session.commit()

            return jsonify({"message": "the workflow has been deleted"})
        
        except Exception as e:
            return jsonify({"error":" something went wrong, try later"})
