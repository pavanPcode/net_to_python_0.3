import os
# import base64
from datetime import datetime
from flask import Flask, request, jsonify,render_template,send_from_directory,request
# from werkzeug.utils import secure_filename
#from db_mssql import insert_data_VehicleTransaction,insert_images,delete_old_records,GetPrevTransactionDetails,dbgetlasttransaction
#import db_mysql
from db_mysql import *
import models
import utilitys
import socket
import logging
import sys
from all_sql_quarys import *
from flask_socketio import SocketIO
import cv2
import base64
import requests
from engineio.async_drivers import gevent




app = Flask(__name__)
# socketio = SocketIO(app)
socketio = SocketIO(app)




port_num = 5000

txt_data = utilitys.read_data_from_file()
if 'log_path' in txt_data:
    log_path = txt_data['log_path']
if 'port' in txt_data:
    port_num = int(txt_data['port'])
if 'host' in txt_data:
    host_add = txt_data['host']
if 'templatefolder' in txt_data:
    templatefolder = txt_data['templatefolder']
if 'rtsp_camera_url' in txt_data:
    rtsp_camera_url = txt_data['rtsp_camera_url']


# Redirect Flask's output to a file
log_file = open(rf"{log_path}\flask_log.txt", "w")
sys.stdout = log_file
sys.stderr = log_file

#############################################################################################################################################

# @app.route('/')
# def index():
#     # You can pass data to the template as keyword arguments
#
#     return send_from_directory(templatefolder,'livefeed.html')

@app.route('/')
def index():
    return send_from_directory(templatefolder,'index1.html')


def generate_frames():
    # IP camera URL
    # camera_url = "rtsp://admin:intozi@123@192.168.0.63/live"
    camera_url = rtsp_camera_url

    # Initialize the camera capture
    cap = cv2.VideoCapture(camera_url)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)

        # Convert the frame to base64 for sending over WebSocket
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        # Send the frame to the client via WebSocket
        socketio.emit('frame', frame_base64)

# # Route to save captured images
# @app.route('/save_image', methods=['POST'])
# def save_image():
#     global captured_image_base64
#     data = request.get_json()
#
#     # Create a folder to store captured images if it doesn't exist
#     if not os.path.exists("captured_images"):
#         os.makedirs("captured_images")
#
#     captured_image_base64 = None  # Variable to store the captured image
#
#
#     if 'image_base64' in data:
#         captured_image_base64 = data['image_base64']
#         # Generate a unique filename (you can customize this)
#         filename = os.path.join("captured_images", "captured_image.jpg")
#
#
#         # Decode the base64 image data and save it as a JPEG file
#         with open(filename, "wb") as f:
#             f.write(base64.b64decode(captured_image_base64))
#
#         return "Image saved successfully"
#     else:
#         return "Image not provided"


# Route to save captured images
@app.route('/save_image', methods=['POST'])
def save_image():
    global captured_image_base64
    data = request.get_json()
    captured_image_base64 = None  # Variable to store the captured image


    if 'image_base64' in data:
        captured_image_base64 = data['image_base64']

        url = f'http://{host_add}:{port_num}/api/vehicle/onpremiseouttransaction'

        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

        # Data to be sent in the form
        data = {
            'vehicle_number': 'N/A-123456',
            'vehicle_image': captured_image_base64,
            'number_plate': captured_image_base64,
            'device_name': 'ANPR',
            'visited_datetime': formatted_datetime,
            'isCaptured' : 1
        }

        # Send the POST request with form data
        response = requests.post(url, data=data)

        if response.status_code == 200:
            return "Image saved successfully"
        else:
            return "Image not provided"
    else:
        return "Image not provided"




@app.route('/api/Vehicle/gettransactionintimespan', methods=['GET'])
def gettransactionintimespan():
    time_span_in_seconds = int(request.args.get('TimeSpaninSeconds'))

    item,status_code  = dbgetlasttransaction(time_span_in_seconds)
    #return item
    output_model = {}

    if item is not None and status_code  ==  200:
        output_model['id'] = item['id']
        output_model['machineId'] = item.get('machineId', 0)
        output_model['numberPlateImage'] = item['numberPlateImage']
        output_model['vehicleImage'] = item['vehicleImage']
        output_model['numberPlateImageb64'] = utilitys.convert_image_to_base64(item['numberPlateImage'])
        output_model['vehicleImageb64'] = utilitys.convert_image_to_base64(item['vehicleImage'])
        output_model['deviceId'] = item['deviceId']
        output_model['cardId'] = item['cardId']
        output_model['dateOfTransaction'] = item['dateOfTransaction'].strftime("%Y-%m-%dT%H:%M:%S")
    else:
        # Handle the case where item is None
        return {"id":0,"machineId":0,"deviceId":None,
                "cardId":None,"dateOfTransaction":"0001-01-01T00:00:00","vehicleImage":None,"numberPlateImage":None,
                "numberPlateImageb64":None,"vehicleImageb64":None}

    return jsonify(output_model), 200 if item else 400







############################################################################################################################################

@app.route('/api/Vehicle/getlasttransaction', methods=['GET'])
def get_vehicle_last_transactions():
    time_span_in_seconds = int(request.args.get('TimeSpaninSeconds'))

    item,status_code  = dbgetlasttransaction(time_span_in_seconds)
    #return item
    output_model = {}

    if item is not None and status_code  ==  200:
        output_model['id'] = item['id']
        output_model['machineId'] = item.get('machineId', 0)
        output_model['numberPlateImage'] = item['numberPlateImage']
        output_model['vehicleImage'] = item['vehicleImage']
        output_model['numberPlateImageb64'] = utilitys.convert_image_to_base64(item['numberPlateImage'])
        output_model['vehicleImageb64'] = utilitys.convert_image_to_base64(item['vehicleImage'])
        output_model['deviceId'] = item['deviceId']
        output_model['cardId'] = item['cardId']
        output_model['dateOfTransaction'] = item['dateOfTransaction'].strftime("%Y-%m-%dT%H:%M:%S")
    else:
        # Handle the case where item is None
        return {"id":0,"machineId":0,"deviceId":None,
                "cardId":None,"dateOfTransaction":"0001-01-01T00:00:00","vehicleImage":None,"numberPlateImage":None,
                "numberPlateImageb64":None,"vehicleImageb64":None}

    return jsonify(output_model), 200 if item else 400


#############test##########
@app.route('/uploadtest', methods=['POST'])
def upload():
    #print(request.form,'files',request.files)
    # Get data from form fields
    gm_transaction_id = request.form.get('gm_transaction_id')
    vehicle_numberplate_b64 = request.form.get('vehicle_numberplate_b64')
    vehicle_image_b64 = request.form.get('vehicle_image_b64')
    cardId = request.form.get('cardId')
    dateOfTransaction = request.form.get('dateOfTransaction')
    plate_path = request.form.get('plate_path')


    # Get the uploaded file
    vehicle_numberplate = request.files['vehicle_numberplate']
    vehicle_image = request.files['vehicle_image']
    print(cardId)
    print(plate_path)

    return "suss"

########################


#############################################################################################################################################
@app.route('/api/vehicle/deleteAnprRecordsInDb', methods=['POST'])
def deleteAnprRecordsInDb():
    success = delete_old_records()
    if success:
        return jsonify({"message": "Records older  days have been deleted."}), 200
    else:
        return jsonify({"error": "An error occurred while deleting records."}), 500

@app.route('/api/vehicle/deleteAnprVehicleImage', methods=['POST'])
def deleteAnprVehicleImage():
    success = utilitys.delete_files_older_than()
    if success:
        return jsonify({"message": "Images older than  have been deleted."}), 200
    else:
        return jsonify({"error": "An error occurred while deleting images."}), 500



#http://192.168.0.111:8020/api/vehicle/onpremisetransaction
@app.route('/api/vehicle/onpremiseouttransaction', methods=['POST'])
def onpremiseouttransaction():
    #res = models.ResultStringModel()
    vehNumber = request.form["vehicle_number"]

    vehicle_number = request.form.get("isCaptured")
    if vehicle_number is not None:
        isCaptured = int(request.form["isCaptured"])
    else:
        # The "vehicle_number" form field does not exist in the form data
        isCaptured = 0

    imageOperations = models.ImageOperations()

    if not imageOperations.IsBase64(request.form["number_plate"]) or not imageOperations.IsBase64(request.form["vehicle_image"]):
        #res.message = "succ"
        #return jsonify(res._dict_)
        return jsonify({"message":"succ"})
#not (8 <= len(vehNumber) <= 12) or
    if (not vehNumber[0].isalpha() or vehNumber.isalpha()):
        # res.message = "succ"
        # return jsonify(res)
        return jsonify({"message": "succ"})

    item = {
        "SuperId": 10000,
        "MachineId": 1,
        "DeviceId": request.form["device_name"],
        "CardId": vehNumber,
        "DateOfTransaction": request.form["visited_datetime"],
        "Status": 2,
        "IsActive": True,
        "IsPushed": True,
        "VehiclePlateNo": vehNumber,
        "isCaptured" : isCaptured
    }

    #result = insert_data_into_sql_server(item)
    result = insert_data_VehicleTransaction(item)

    itemImage = {
        "VehicleTransactionId": result
    }

    # # Open the text file containing the file path
    # with open('filepath.txt', 'r') as file:
    #     # Read the file path from the text file
    #     UPLOAD_FOLDER = file.readline().strip()

    txt_data = utilitys.read_data_from_file()
    if 'file path' in txt_data:
        UPLOAD_FOLDER = txt_data['file path']



    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # Create a folder to save images if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    fileUpload = models.FileUpload()
    #print(item.DateOfTransaction)

    datetime_obj = datetime.strptime(item["DateOfTransaction"], "%Y-%m-%d %H:%M:%S")

    # Format the datetime object into the desired format
    timestamp = datetime_obj.strftime("%Y-%m-%d%H%M")
    #timestamp = datetime.strptime(item["DateOfTransaction"], "%Y-%m-%d%H:%M")
    #timestamp = (item.DateOfTransaction).strftime("%Y-%m-%d%H%M")

    # Save the number plate image
    fileUpload.FileName = f"NP_{result}_{timestamp}.jpg"
    fileUpload.Base64Content = request.form["number_plate"]
    itemImage["NumberPlateImage"] = utilitys.save_image(fileUpload)

    # Save the vehicle image
    fileUpload.FileName = f"VI_{result}_{timestamp}.jpg"
    fileUpload.Base64Content = request.form["vehicle_image"]
    itemImage["VehicleImage"] = utilitys.save_image(fileUpload)


    #insert_images(itemImage)
    insert_images(itemImage)

    # res.message = "succ"
    # return jsonify(res._dict_)
    return jsonify({"message": "succ"})

@app.route('/api/Vehicle/getlast15vehicletransaction', methods=['GET'])
def getLast15VehicleTransaction():
    output_model = models.VehicleOutput()
    try:
        item = GetDetailInList(getlast15vehtransactionquary)
        if item =={}:
            nodatafound = []
            return nodatafound

        return item
    except Exception as ex:
        output_model.error = str(ex)
        return jsonify(nodatafound), 400



@app.route('/api/Vehicle/getlast15requestvehicle', methods=['GET'])
def getlast15requestvehicle():
    output_model = models.VehicleOutput()
    try:
        item = GetDetailInList("select * from requestvehicle order by ID DESC LIMIT 15;")
        if item =={}:
            nodatafound = []
            return nodatafound

        return item
    except Exception as ex:
        output_model.error = str(ex)
        return jsonify(nodatafound), 400

@app.route('/api/Vehicle/getprevtransaction', methods=['GET'])
def get_prev_vehicle_transactions():
    output_model = models.VehicleOutput()
    try:
        item = GetPrevTransactionDetails(GetPrevTransactionDetailsquary)
        if item =={}:
            nodatafound = {"cardId": 0, "dateOfTransaction": "0001-01-01T00:00:00", "deviceId": None, "id": 0,
                           "machineId": None, "numberPlateImage": None, "numberPlateImageb64": None,
                           "vehicleImage": None,
                           "vehicleImageb64": None}
            return nodatafound

        item['dateOfTransaction'] = item['dateOfTransaction'].strftime("%Y-%m-%dT%H:%M:%S")
        item['numberPlateImageb64'] = utilitys.convert_image_to_base64(item['numberPlateImage'])
        item['vehicleImageb64'] = utilitys.convert_image_to_base64(item['vehicleImage'])

        return item
    except Exception as ex:
        output_model.error = str(ex)
        return jsonify(output_model.__dict__), 400


@app.route('/api/Vehicle/requestlastvehicledetails', methods=['POST'])
def RequestLastVehicleDetails():
    output_model = models.VehicleOutput()
    try:
        data = request.json
        refno = data['refno']
        key_to_check = 'timestamp'

        current_time = datetime.now()

        if data.get(key_to_check) is not None:
            #print(f"The key '{key_to_check}' exists in the dictionary.")
            insertInRefTable = InsertRefRecord(insertRefTableRecord.format(refno,data['timestamp']))
        else:
            #print(f"The key '{key_to_check}' does not exist in the dictionary.")
            insertInRefTable = InsertRefRecord(insertRefTableRecord.format(refno,current_time))





        nodatafound = {"cardId": 0, "dateOfTransaction": "0001-01-01T00:00:00", "deviceId": None, "id": 0,
                       "machineId": None, "numberPlateImage": None, "numberPlateImageb64": None, "vehicleImage": None,
                       "vehicleImageb64": None,'refno':refno}
        return nodatafound

        # if refno != '':
        #     nodatafound
        # # if  vehicleNumber:
        # #     #return getprevtransactionByvehicleNumberQaury.format(vehicleNumber)
        # #     item = GetPrevTransactionDetails(getprevtransactionByvehicleNumberQaury.format(vehicleNumber))
        # #     print(item)
        # # elif vehicleLast4digits:
        # #     item = GetPrevTransactionDetails(getprevtransactionByvehicleNumberLast4digitsQaury.format(vehicleLast4digits))
        # #
        # #
        # # else:
        # #     return nodatafound
        #
        # item = GetPrevTransactionDetails(getprevtransactionByvehicleNumberQaury.format(refno))
        #
        # if item == {}:
        #     return nodatafound
        #
        # item['dateOfTransaction'] = item['dateOfTransaction'].strftime("%Y-%m-%dT%H:%M:%S")
        # item['numberPlateImageb64'] = utilitys.convert_image_to_base64(item['numberPlateImage'])
        # item['vehicleImageb64'] = utilitys.convert_image_to_base64(item['vehicleImage'])
        #
        # #updateRedtableRecord(updateRefTableRecordquary.format(insertInRefTable,item['id']))
        #
        # return item
    except Exception as ex:
        #output_model.error = str(ex)
        return jsonify(nodatafound), 400


@app.route('/api/Vehicle/getLastTransactionsByVehicle')
def getLastTramsactionsByVehicle():
    output_model = models.VehicleOutput()
    try:
        # vehicleNumber = request.args.get('vehicleNumber')
        # vehicleLast4digits = request.args.get('vehicleLast4digits')
        refno = request.args.get('refno')

        #postStatus  1 . created ,1.notsend--but found,2.send succesfully


        nodatafound = {"cardId": 0, "dateOfTransaction": "0001-01-01T00:00:00", "deviceId": None, "id": 0,
                       "machineId": None, "numberPlateImage": None, "numberPlateImageb64": None, "vehicleImage": None,
                       "vehicleImageb64": None}
        if refno != '':
            nodatafound

        item = GetPrevTransactionDetails(getprevtransactionByRefNoQaury.format(refno))


        if item == {}:
            return nodatafound

        item['dateOfTransaction'] = item['dateOfTransaction'].strftime("%Y-%m-%dT%H:%M:%S")
        item['numberPlateImageb64'] = utilitys.convert_image_to_base64(item['numberPlateImage'])
        item['vehicleImageb64'] = utilitys.convert_image_to_base64(item['vehicleImage'])
        return item

    except Exception as ex:
        #output_model.error = str(ex)
        return jsonify(nodatafound), 400

#
# def get_ip_address():
#     try:
#         # Create a socket object and connect to a remote host (e.g., Google's DNS server)
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 80))
#         ip_address = s.getsockname()[0]
#         s.close()
#         return ip_address
#     except Exception as e:
#         print(f"Error getting IP address: {str(e)}")
#         return "127.0.0.1"  # Default to localhost if an error occurs
#
# # Use the system's IP address as the host
# ip_address = get_ip_address()




if __name__ == '__main__':
    #app.run(host=host_add,port=port_num)
    # Start streaming the video frames when the application starts
    socketio.start_background_task(generate_frames)
    socketio.run(app,host='0.0.0.0',port=port_num,allow_unsafe_werkzeug=True)

