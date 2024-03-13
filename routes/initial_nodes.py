import json

def initial_reply_Nodes(request,Project,Workflow,jsonify):

    if request.method == 'POST':
        
        
        try:
            data = request.get_json()
            project_id = data['projectId']
            project = Project.query.filter_by(project_id = project_id).first()
            workflow = Workflow.query.filter_by(project_id= project_id).first()
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                return jsonify({
                    "nodes":[],
                    "edges":[]
                })
            
            startConvoNodes = []
            json_nodes = json.loads(workflow.nodes)
            json_edges = json.loads(workflow.edges)

            for node in json_nodes :

                if node['type'] == 'startConvoNode':
                    connected_reply_id = []

                    for edge in json_edges:
                        if edge['source'] == node['id']:

                            connected_reply_id.append(edge['target'])

                    startConvoNodes.append({
                        'node': node,
                        'connected_reply_id': connected_reply_id 
                    })

            print(startConvoNodes)
            return jsonify({
                'data':startConvoNodes
            })
            

        except Exception as e:
            print(e)
            return jsonify({"error":" something went wrong, try later"})