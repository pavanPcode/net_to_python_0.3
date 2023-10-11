GetPrevTransactionDetailsquary = """SELECT vt.id id,
                               vt.machineId machineId,
                               vt.DeviceId deviceId,
                               vt.CardId cardId,
                               vt.dateOfTransaction dateOfTransaction,
                               vti.VehicleImage vehicleImage,
                               vti.VehicleImage numberPlateImage,
                               '' numberPlateImageb64,
                               '' vehicleImageb64
                        FROM VehicleTransaction vt
                        INNER JOIN VehicleTransactionImage vti ON vt.id = vti.VehicleTransactionId
                        WHERE vt.id = (SELECT MAX(id) FROM VehicleTransaction ORDER BY DateOfTransaction DESC
LIMIT 1)"""


getprevtransactionByvehicleNumberLast4digitsQaury = """SELECT  last_four_digits,DateOfTransaction,id,machineId,deviceId,cardId,dateOfTransaction,vehicleImage,numberPlateImage,
numberPlateImageb64,vehicleImageb64
FROM (
SELECT vt.id id,vt.machineId machineId, vt.DeviceId deviceId,vt.CardId cardId,vt.dateOfTransaction dateOfTransaction,
vti.VehicleImage vehicleImage, vti.VehicleImage numberPlateImage,'' numberPlateImageb64,'' vehicleImageb64,
SUBSTRING(VehiclePlateNo, -4) AS last_four_digits
FROM VehicleTransaction vt
INNER JOIN VehicleTransactionImage vti ON vt.id = vti.VehicleTransactionId
order by DateOfTransaction desc
) AS subquery
WHERE last_four_digits = '{0}' and DateOfTransaction >= DATE_SUB(NOW(), INTERVAL 500000 MINUTE) limit 1;"""

getprevtransactionByvehicleNumberQaury = """SELECT vt.id id,vt.machineId machineId, vt.DeviceId deviceId,vt.CardId cardId,vt.dateOfTransaction dateOfTransaction,
vti.VehicleImage vehicleImage, vti.VehicleImage numberPlateImage,'' numberPlateImageb64,'' vehicleImageb64,
SUBSTRING(VehiclePlateNo, -4) AS last_four_digits
FROM VehicleTransaction vt
INNER JOIN VehicleTransactionImage vti ON vt.id = vti.VehicleTransactionId
 where DateOfTransaction >= DATE_SUB(NOW(), INTERVAL 5 MINUTE) and CardId = '{0}' 
order by DateOfTransaction desc
limit 1;"""

getprevtransactionByRefNoQaury = """SELECT vt.id id,vt.machineId machineId, vt.DeviceId deviceId,vt.CardId cardId,vt.dateOfTransaction dateOfTransaction,
vti.VehicleImage vehicleImage, vti.VehicleImage numberPlateImage,'' numberPlateImageb64,'' vehicleImageb64
FROM VehicleTransaction vt
INNER JOIN VehicleTransactionImage vti ON vt.id = vti.VehicleTransactionId
inner join vehicleRefNumber ref on ref.vehicletransactionid = vt.id
where refno = '{0}'
order by DateOfTransaction desc
limit 1;"""


insertRefTableRecord = """INSERT INTO RequestVehicle (refno, RefNoDatetime,RefStatus,isActive)
VALUES ('{0}', CURRENT_TIMESTAMP,1,1);"""

updateRefTableRecordquary = """update vehicleRefNumber set isfind = 1,vehicletransactionId = {1},postStatus = 2 where id = {0}"""