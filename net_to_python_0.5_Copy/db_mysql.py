import mysql.connector
from datetime import datetime, timedelta
import utilitys
# MySQL server connection parameters


db_config = {}
with open('db_config.txt', 'r') as file:
    for line in file:
        key, value = line.strip().split('=')
        db_config[key.strip()] = value.strip()

host=db_config['host']
username=db_config['user']
password=db_config['password']
database=db_config['database']


def insert_data_VehicleTransaction(data_dict):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )
        cursor = connection.cursor()

        sql_insert = """
            INSERT INTO VehicleTransaction
            (SuperId, MachineId, DeviceId, CardId, DateOfTransaction,
            VehiclePlateNo, Status, IsPushed, IsActive,iscaptured)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data_dict['SuperId'],
            data_dict['MachineId'],
            data_dict['DeviceId'],
            data_dict['CardId'],
            data_dict['DateOfTransaction'],
            data_dict['VehiclePlateNo'],
            data_dict['Status'],
            data_dict['IsPushed'],
            data_dict['IsActive'],
            data_dict["iscaptured"]
        )

        cursor.execute(sql_insert, values)
        inserted_id = cursor.lastrowid  # Get the inserted ID

        connection.commit()


        return inserted_id

    except Exception as e:
        connection.rollback()

    finally:
        cursor.close()
        connection.close()

def insert_images(data_dict):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )
        cursor = connection.cursor()

        sql_insert = """
            INSERT INTO VehicleTransactionImage
            (VehicleTransactionId, VehicleImage, NumberPlateImage)
            VALUES (%s, %s, %s)
        """

        values = (
            data_dict['VehicleTransactionId'],
            data_dict['VehicleImage'],
            data_dict['NumberPlateImage']
        )

        cursor.execute(sql_insert, values)

        connection.commit()


    except Exception as e:
        connection.rollback()

    finally:
        cursor.close()
        connection.close()

# Function to delete records older than 20 days
def delete_old_records():
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )
        cursor = connection.cursor()
        #import datetime
        #current_date = datetime.datetime.now()

        txt_data = utilitys.read_data_from_file()
        if 'file path' in txt_data:
            folder_path = txt_data['file path']
        if 'count' in txt_data:
            days_count = txt_data['count']

        # Calculate the date 20 days ago from today
        twenty_days_ago = datetime.now() - timedelta(days=int(days_count))


        # Delete records from VehicleTransactionImage older than 20 days
        cursor.execute(
            "DELETE FROM VehicleTransactionImage WHERE VehicleTransactionId IN (SELECT Id FROM VehicleTransaction WHERE DateOfTransaction < %s)",
            (twenty_days_ago,))

        # Delete records from VehicleTransaction older than 20 days
        cursor.execute("DELETE FROM VehicleTransaction WHERE DateOfTransaction < %s", (twenty_days_ago,))


        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False


def GetPrevTransactionDetails(sql_query):
    try:
        # MySQL connection settings
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )


        cursor = conn.cursor()


        cursor.execute(sql_query)

        # Fetch the data
        data = cursor.fetchone()

        # Create a dictionary where column names are keys and data values are values
        result_dict = {}
        if data:
            for column_name, value in zip(cursor.column_names, data):
                result_dict[column_name] = value

        conn.close()
        return result_dict
    except Exception as e:
        return {'error':str(e)}

def GetDetailInList(sql_query):
    try:
        # MySQL connection settings
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )

        cursor = conn.cursor()

        cursor.execute(sql_query)

        # Fetch all the data
        data = cursor.fetchall()

        # Create a list of dictionaries where each dictionary represents a row
        result_list = []
        for row in data:
            row_dict = {}
            for column_name, value in zip(cursor.column_names, row):
                row_dict[column_name] = value
            result_list.append(row_dict)

        conn.close()
        return result_list
    except Exception as e:
        return [{'error': str(e)}]


def dbgetlastcapturedtransaction(seconds):
    try:
        # MySQL connection settings
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )

        # Connect to the MySQL database
        cursor = conn.cursor()

        # Your SQL query
        sql_query = f"""SELECT vt.id AS id,
           vt.machineId AS machineId,
           vt.DeviceId AS deviceId,
           vt.CardId AS cardId,
           vt.dateOfTransaction AS dateOfTransaction,
           vti.VehicleImage AS vehicleImage,
           vti.numberPlateImage AS numberPlateImage
        FROM VehicleTransaction vt
        INNER JOIN VehicleTransactionImage vti ON vt.id = vti.VehicleTransactionId
        WHERE vt.dateOfTransaction >= DATE_SUB(NOW(), INTERVAL {seconds} SECOND) and iscaptured = 1
        ORDER BY vt.dateOfTransaction DESC
        LIMIT 1;"""

        cursor.execute(sql_query)

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            return None, 200  # No data found

        # Create a dictionary where column names are keys and data values are values
        result_dict = {}
        for column_name, value in zip(cursor.column_names, data):
            result_dict[column_name] = value

        conn.close()
        print(result_dict)
        return result_dict, 200
    except mysql.connector.Error as e:
        return {'error': str(e)}, 400  # Handle database errors
    except Exception as e:
        return {'error': str(e)}, 500  # Handle other exceptions

def dbgetlasttransaction(seconds):
    try:
        # MySQL connection settings
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )

        # Connect to the MySQL database
        cursor = conn.cursor()

        # Your SQL query
        sql_query = f"""SELECT vt.id AS id,
           vt.machineId AS machineId,
           vt.DeviceId AS deviceId,
           vt.CardId AS cardId,
           vt.dateOfTransaction AS dateOfTransaction,
           vti.VehicleImage AS vehicleImage,
           vti.numberPlateImage AS numberPlateImage
        FROM VehicleTransaction vt
        INNER JOIN VehicleTransactionImage vti ON vt.id = vti.VehicleTransactionId
        WHERE vt.dateOfTransaction >= DATE_SUB(NOW(), INTERVAL {seconds} SECOND) and iscaptured = 0
        ORDER BY vt.dateOfTransaction DESC
        LIMIT 1;"""

        cursor.execute(sql_query)

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            return None, 200  # No data found

        # Create a dictionary where column names are keys and data values are values
        result_dict = {}
        for column_name, value in zip(cursor.column_names, data):
            result_dict[column_name] = value

        conn.close()
        return result_dict, 200
    except mysql.connector.Error as e:
        return {'error': str(e)}, 400  # Handle database errors
    except Exception as e:
        return {'error': str(e)}, 500  # Handle other exceptions


def dbgetlastbothtraansaction(time_span_in_seconds):
    try:
        # MySQL connection settings
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )

        # Connect to the MySQL database
        cursor = conn.cursor()

        # Your SQL query
        sql_query = f"""SELECT vt.id AS id,
           vt.machineId AS machineId,
           vt.DeviceId AS deviceId,
           vt.CardId AS cardId,
           vt.dateOfTransaction AS dateOfTransaction,
           vti.VehicleImage AS vehicleImage,
           vti.numberPlateImage AS numberPlateImage,vt.iscaptured
        FROM VehicleTransaction vt
        INNER JOIN VehicleTransactionImage vti ON vt.id = vti.VehicleTransactionId
        WHERE  vt.dateOfTransaction >= DATE_SUB(NOW(), INTERVAL {time_span_in_seconds} SECOND)
        ORDER BY vt.dateOfTransaction desc
        LIMIT 1;"""

        cursor.execute(sql_query)

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            return None, 200  # No data found

        # Create a dictionary where column names are keys and data values are values
        result_dict = {}
        for column_name, value in zip(cursor.column_names, data):
            result_dict[column_name] = value

        conn.close()
        return result_dict, 200
    except mysql.connector.Error as e:
        return {'error': str(e)}, 400  # Handle database errors
    except Exception as e:
        return {'error': str(e)}, 500  # Handle other exceptions

def dbgetlastcaptureimages():
    try:
        # MySQL connection settings
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )

        # Connect to the MySQL database
        cursor = conn.cursor()

        # Your SQL query
        sql_query = f"""SELECT vt.id AS id,
           vt.machineId AS machineId,
           vt.DeviceId AS deviceId,
           vt.CardId AS cardId,
           vt.dateOfTransaction AS dateOfTransaction,
           vti.VehicleImage AS vehicleImage,
           vti.numberPlateImage AS numberPlateImage
        FROM VehicleTransaction vt
        INNER JOIN VehicleTransactionImage vti ON vt.id = vti.VehicleTransactionId
        WHERE  iscaptured = 1
        ORDER BY vt.dateOfTransaction DESC
        LIMIT 1;"""

        cursor.execute(sql_query)

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            return None, 200  # No data found

        # Create a dictionary where column names are keys and data values are values
        result_dict = {}
        for column_name, value in zip(cursor.column_names, data):
            result_dict[column_name] = value

        conn.close()
        return result_dict, 200
    except mysql.connector.Error as e:
        return {'error': str(e)}, 400  # Handle database errors
    except Exception as e:
        return {'error': str(e)}, 500  # Handle other exceptions


def InsertRefRecord(sql_quary):
    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database=database
    )

    # Connect to the MySQL database
    cursor = conn.cursor()

    # Execute the INSERT statement
    cursor.execute(sql_quary)

    # Get the ID of the last inserted row
    cursor.execute("SELECT LAST_INSERT_ID()")
    inserted_id = cursor.fetchone()[0]

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # # Print the inserted ID
    # print(f"The ID of the inserted row is {inserted_id}")
    return inserted_id


def updateRedtableRecord(update_query):
    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database=database
    )

    # Connect to the MySQL database
    cursor = conn.cursor()

    cursor.execute(update_query)

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    return True
