import os
from werkzeug.utils import secure_filename
import base64
import datetime


def convert_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            # Read the image binary data
            image_binary = image_file.read()
            # Encode the binary data as base64
            base64_encoded = base64.b64encode(image_binary).decode('utf-8')

            return base64_encoded
    except Exception as e:
        print(f"Error converting image to base64: {str(e)}")
        return None



def save_image(file_upload):
    # Define the folder where images will be saved

    # Open the text file containing the file path
    # with open('filepath.txt', 'r') as file:
    #     # Read the file path from the text file
    #     UPLOAD_FOLDER = file.readline().strip()

    txt_data = read_data_from_file()
    if 'file path' in txt_data:
        UPLOAD_FOLDER = txt_data['file path']

    # Now, 'file_path' contains the path from the text file
    # print(f"File path from the text file: {UPLOAD_FOLDER}")

    # UPLOAD_FOLDER = r'C:\Users\saipa\Downloads\Anpr_testing_img'
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


    filename = secure_filename(file_upload.FileName)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Save the base64 image content as a file
    with open(file_path, 'wb') as f:
        f.write(base64.b64decode(file_upload.Base64Content))

    return file_path


def delete_files_older_than():
    """
    Delete files in a folder that are older than a specified number of days.

    Args:
        folder_path (str): The path to the folder containing the files.
        days (int): The threshold number of days. Files older than this will be deleted.

    Returns:
        int: The number of files deleted.
    """
    # Get the current date
    current_date = datetime.datetime.now()

    txt_data = read_data_from_file()
    if 'file path' in txt_data:
        folder_path = txt_data['file path']
    if 'count' in txt_data:
        days = txt_data['count']

    # Calculate the date threshold
    threshold_date = current_date - datetime.timedelta(days=int(days))

    # Initialize a counter for deleted files
    files_deleted = 0

    # with open('filepath.txt', 'r') as file:
    #     # Read the file path from the text file
    #     folder_path = file.readline().strip()




    # Iterate over files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if the file is a regular file and its creation time is older than the threshold
        if os.path.isfile(file_path):
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            if creation_time < threshold_date:
                # Delete the file
                os.remove(file_path)
                files_deleted += 1

    return files_deleted


def read_data_from_file():
    data = {}

    # Open the file for reading
    with open('filepath.txt', 'r') as file:
        for line in file:
            # Split each line into key and value pairs
            key, value = line.strip().split('=')
            # Remove leading and trailing spaces from key and value
            key = key.strip()
            value = value.strip()
            # Store the data in a dictionary
            data[key] = value

    return data