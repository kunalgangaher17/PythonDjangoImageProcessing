import cv2 as cv
import uuid
from pathlib import Path

newX = int(400)
newY = int(400)
print("New X :"+str(newX)+", newY :"+str(newY))
fileAbsolutePath = "F:\\PythonDjangoProject\\django\\projiproc\\filestore\\MyImage.jpg"
scaledFilePath = str(Path(fileAbsolutePath).with_suffix(
    ''))+str(uuid.uuid4())+'.png'
print("Scaled file path :"+str(scaledFilePath))
originalImage = cv.imread(scaledFilePath)
print("Original image :"+str(originalImage))
newImage = cv.resize(originalImage, (newX, newY),
                     interpolation=cv.INTER_AREA)

scaledFileName = scaledFilePath.split('/')[-1]
print("Scaled file name :"+scaledFileName)
cv.imshow('exampleshq', newImage)
cv.waitKey(0)
cv.destroyAllWindows()
