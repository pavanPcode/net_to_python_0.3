import base64

class ResultStringModel:
    pass

class ImageOperations:
    @staticmethod
    def IsBase64(data):
        try:
            base64.b64decode(data)
            return True
        except Exception:
            return False

class FileUpload:
    FileName = ""
    Base64Content = ""


class VehicleOutput:
    pass



class VehicleTransaction:
    def VehicleTransactionImages(self):
        return []

class DbOperations:
    def GetPrevTransactionDetails(self):
        # Implement your logic here to fetch transaction details
        return VehicleTransaction()
