from flask import render_template, Response, request, jsonify
from config import verification_bp, face_mesh  # Import from our __init__.py
from verification_logic import generate_frames, verification_status

@verification_bp.route('/popup')
def popup():

    verification_status[0] = "Pending"
    print("--- New Session: Status reset to Pending ---")        
    #Serves the HTML for the pop-up window itself.
    ref_path = request.args.get('ref_path')
    if not ref_path:
        return "Error: No reference image path provided in URL.", 400
    # This will render 'live_verification/templates/verification_popup.html'
    return render_template('verification_popup.html',ref_path=ref_path)

@verification_bp.route('/video_feed')
def video_feed():
    #The video streaming route.
    ref_path = request.args.get('ref_path')
    if not ref_path:
        print("Error: Video feed requested without reference path.")
        return "Error: Missing ref_path", 400
    
    return Response(
        generate_frames(ref_path, face_mesh),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@verification_bp.route('/check_status')
def check_status():
    #API Endpoint for JavaScript Polling.
    #Returns JSON: {"status": "Pending"} or {"status": "VERIFIED"}
    
    # return the current status from the global variable
    current_status = verification_status[0]
    return jsonify({"status": current_status})