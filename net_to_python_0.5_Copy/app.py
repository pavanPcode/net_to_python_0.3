import os
# import base64
from flask import Flask, Response, render_template, request, redirect, url_for, send_from_directory,jsonify

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
import cv2



port_num = 5000

txt_data = utilitys.read_data_from_file()
if 'log_path' in txt_data:
    log_path = txt_data['log_path']
if 'port' in txt_data:
    port_num = txt_data['port']
if 'host' in txt_data:
    host_add = txt_data['host']
if 'templatefolder' in txt_data:
    templatefolder = txt_data['templatefolder']
if 'file path' in txt_data:
    file_path = txt_data['file path']
if 'rtsp_url' in txt_data:
    rtsp_url = txt_data['rtsp_url']

dir_name = file_path





app = Flask(__name__,template_folder=templatefolder)




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

#####################################################################################################################





# Function to capture frames from the RTSP stream
def generate_frames():
    cap = cv2.VideoCapture(rtsp_url)

    while True:
        success, frame = cap.read()
        if not success:
            break

        new_width = 680  # Specify the desired width
        new_height = 540  # Specify the desired height
        frame = cv2.resize(frame, (new_width, new_height))

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/capture')
# def capture():
#     # Capture an image
#     cap = cv2.VideoCapture(rtsp_url)
#     ret, frame = cap.read()
#     cap.release()
#
#     if ret:
#         # Generate a unique filename based on the timestamp
#         timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#         filename = os.path.join(dir_name, f"captured_{timestamp}.jpg")
#
#         print(frame)
#
#         ## Save the captured image
#         # cv2.imwrite(filename, frame)
#
#     return redirect(url_for('index'))




def capture():
    # Capture an image
    cap = cv2.VideoCapture(rtsp_url)
    ret, frame = cap.read()

    cap.release()
    if ret:

        item = {
            "SuperId": 10000,
            "MachineId": 1,
            "DeviceId": "ANPR",
            "CardId": " ",
            "DateOfTransaction": str(datetime.now()),
            "Status": 2,
            "IsActive": True,
            "IsPushed": True,
            "VehiclePlateNo": " ",
            "iscaptured": 1
        }

        # result = insert_data_into_sql_server(item)
        result = insert_data_VehicleTransaction(item)

        ######################################################################
        #----------------------------------------------------------------------------------------
        datetime_obj = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
        # Format the datetime object into the desired format
        timestamp = datetime_obj.strftime("%Y-%m-%d%H%M")
        # timestamp = datetime.strptime(item["DateOfTransaction"], "%Y-%m-%d%H:%M")
        # timestamp = (item.DateOfTransaction).strftime("%Y-%m-%d%H%M")

        # Save the number plate image
        NumberPlateImage = f"NP_{result}_{timestamp}.jpg"
        VehicleImage = f"VI_{result}_{timestamp}.jpg"

        NumberPlateImage = os.path.join(dir_name, NumberPlateImage)
        VehicleImage = os.path.join(dir_name, VehicleImage)

        # Save the captured image
        num_img = cv2.imwrite(NumberPlateImage, frame)
        veh_img = cv2.imwrite(VehicleImage, frame)


        itemImage = {
            "VehicleTransactionId": result, "NumberPlateImage": NumberPlateImage, "VehicleImage": VehicleImage
        }

        insert_images(itemImage)

        return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route('/capture')
def capture_api():
    return capture()



# @app.route('/captured_images/<path:filename>')
# def captured_image(filename):
#     return send_from_directory(dir_name, filename)

@app.route('/')
def index():
    return render_template('index.html')


###########################################################################################################################



@app.route('/api/vehicle/gettransactionintimespan', methods=['GET'])
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


@app.route('/api/Vehicle/getlastcapturetransactionintimespan', methods=['GET'])
def getlastcapturetransactionintimespan():
    time_span_in_seconds = int(request.args.get('TimeSpaninSeconds'))


    item,status_code  = dbgetlastcapturedtransaction(time_span_in_seconds)
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

@app.route('/api/Vehicle/getlastcapturedtransaction', methods=['GET'])
def getlastcapturedtransaction():
    #time_span_in_seconds = int(request.args.get('TimeSpaninSeconds'))


    item,status_code  = dbgetlastcaptureimages()
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

#################################################################################################################################


@app.route('/api/Vehicle/getlastbothtraansaction', methods=['GET'])
def getlastbothtraansaction():
    time_span_in_seconds = int(request.args.get('TimeSpaninSeconds'))


    item,status_code  = dbgetlastbothtraansaction(time_span_in_seconds)
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

        if int(item['iscaptured']) == 0 :
            type= 1
        else :
            type = 0
        output_model['type'] = type

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

    caputure_live_image = capture()

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
        "iscaptured": 0
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
    app.run(host=host_add, port=port_num)

