import pyodbc
from datetime import datetime, timedelta
import utilitys

server = 'localhost'
database = 'PC_Anpr'
username = 'sa'
password = 'sadguru'

def insert_data_VehicleTransaction(data_dict):

    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    connection = pyodbc.connect(connection_string)

    try:
        sql_insert = """
            INSERT INTO [dbo].[VehicleTransaction]
            ([SuperId], [MachineId], [DeviceId], [CardId], [DateOfTransaction],
            [VehiclePlateNo], [Status], [IsPushed], [IsActive])
            OUTPUT INSERTED.ID  -- Specify the column(s) whose values you want to return
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            data_dict['IsActive']
        )

        # Use a cursor to execute the SQL command
        cursor = connection.cursor()
        cursor.execute(sql_insert, values)
        inserted_id = cursor.fetchone()[0]  # Get the inserted ID from the result

        # Commit the transaction
        connection.commit()

        print(f"Data inserted successfully with ID: {inserted_id}")

        return inserted_id  # Return the inserted ID

    except Exception as e:
        print(f"Error: {str(e)}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()




def insert_images(data_dict):
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    connection = pyodbc.connect(connection_string)

    try:
        sql_insert = """
            INSERT INTO [dbo].[VehicleTransactionImage]
            ([VehicleTransactionId], [VehicleImage], [NumberPlateImage])
            VALUES (?, ?, ?)
        """

        values = (
            data_dict['VehicleTransactionId'],
            data_dict['VehicleImage'],
            data_dict['NumberPlateImage']
        )

        # Use a cursor to execute the SQL command
        #cursor = connection.cursor()
        connection.execute(sql_insert, values)

        # Commit the transaction
        connection.commit()

        print("Data inserted successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        connection.rollback()

    finally:
        #cursor.close()
        connection.close()


def delete_old_records():
    try:
        # Connect to the SQL Server database
        conn = pyodbc.connect(
            f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )

        cursor = conn.cursor()

        txt_data = utilitys.read_data_from_file()
        if 'file path' in txt_data:
            folder_path = txt_data['file path']
        if 'count' in txt_data:
            days = txt_data['count']

        # Calculate the date 20 days ago from today
        twenty_days_ago = datetime.now() - timedelta(days=int(days))

        # Delete records from VehicleTransactionImage older than 20 days
        cursor.execute(
            f"DELETE FROM [dbo].[VehicleTransactionImage] WHERE [VehicleTransactionId] IN (SELECT [Id] FROM [dbo].[VehicleTransaction] WHERE [DateOfTransaction] < ?)",
            twenty_days_ago)

        # Delete records from VehicleTransaction older than 20 days
        cursor.execute(f"DELETE FROM [dbo].[VehicleTransaction] WHERE [DateOfTransaction] < ?", twenty_days_ago)



        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(str(e))
        return False


def GetPrevTransactionDetails():

    try:
        conn = pyodbc.connect(
            f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )
        cursor = conn.cursor()

        # Your SQL query
        sql_query = """select vt.id id ,vt.machineId machineId ,vt.DeviceId deviceId,vt.CardId cardId,vt.dateOfTransaction dateOfTransaction,vti.VehicleImage vehicleImage
                        ,vti.VehicleImage numberPlateImage, '' numberPlateImageb64,'' vehicleImageb64
                        from VehicleTransaction vt
                        inner join VehicleTransactionImage vti on vt.id = vti.VehicleTransactionId where vt.id = (SELECT MAX(id) FROM VehicleTransaction)"""

        cursor.execute(sql_query)

        # Fetch the data
        data = cursor.fetchall()

        # Create a list of dictionaries where column names are keys and data values are values
        for row in data:
            result_dict = {}
            for column_name, value in zip(cursor.description, row):
                result_dict[column_name[0]] = value

        conn.close()
        return result_dict
    except Exception as e:
        print("Error:", str(e))
        return {}

# print(fetch_data())



def dbgetlasttransaction(seconds):
    try:
        # MSSQL connection settings


        conn = pyodbc.connect(
            f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )

        # Create a cursor
        cursor = conn.cursor()

        # Your SQL query (modified for MSSQL syntax)
        sql_query = f"""SELECT TOP 1 vt.id AS id,
           vt.machineId AS machineId,
           vt.DeviceId AS deviceId,
           vt.CardId AS cardId,
           vt.dateOfTransaction AS dateOfTransaction,
           vti.VehicleImage AS vehicleImage,
           vti.numberPlateImage AS numberPlateImage
        FROM VehicleTransaction vt
        INNER JOIN VehicleTransactionImage vti ON vt.id = vti.VehicleTransactionId
        WHERE vt.dateOfTransaction >= DATEADD(SECOND, -{seconds}, GETDATE())
        ORDER BY vt.dateOfTransaction DESC;"""

        cursor.execute(sql_query)

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            return None, 200  # No data found

        # Create a dictionary where column names are keys and data values are values
        result_dict = {}
        for column_name, value in zip([column[0] for column in cursor.description], data):
            result_dict[column_name] = value

        conn.close()
        print(result_dict)
        return result_dict, 200
    except pyodbc.Error as e:
        return {'error': str(e)}, 400  # Handle database errors
    except Exception as e:
        return {'error': str(e)}, 500  # Handle other exceptions
