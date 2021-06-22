from django.shortcuts import render
from django.http import *
import datetime
from django.core.files.storage import FileSystemStorage
import os
import cv2 as cv
import uuid
from pathlib import Path
import numpy as np
import zipfile
from zipfile import ZipFile
import io
from colormap import hex2rgb

def index(request):
    today = datetime.datetime.now()
    return render(request, 'index.html', {
        "today": today.strftime("%d-%m-%Y")
    })


def isFileOpen(request):
    stack = request.session['stack']
    if stack > 0 and request.session.get('name') != None and request.session.get('email') != None:
        return True
    else:
        return False


def getImage(request):
    if request.method == "GET" and request.session.has_key('stack'):
        stack = request.session['stack']
    if len(stack) > 0:
        fileToServe = stack[0]
        # fileToServe=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]))
        return FileResponse(open(fileToServe, 'rb'))
    return HttpResponse('')

#api for opening an image file uploaded by user
def openFile(request):
    if request.method == "POST":
        imageFile = request.FILES['fileName']
        fileSystemStorage = FileSystemStorage()
        imageFileName = fileSystemStorage.save(imageFile.name, imageFile)
        stack = []

        imagePath = os.path.abspath(os.path.join(os.path.dirname(
            __file__), '..', 'filestore/%s' % imageFileName))
        image = cv.imread(imagePath)
        (h, w) = image.shape[:2]
        r = 500/float(h)
        dim = (int(w*r), 500)

        stdImage = cv.resize(image, dim, interpolation=cv.INTER_AREA)
        stdImagePath = str(Path(imagePath).with_suffix('')) + \
            str(uuid.uuid4())[-3:]+'.png'
        cv.imwrite(stdImagePath, stdImage)
        stdFileName = stdImagePath.split('/')[-1]

        stack.append(stdFileName)
        request.session['stack'] = stack

    return JsonResponse({'fileName': imageFileName})


def getState(request):
    return JsonResponse({'state': 'none', 'name': '', 'email': '', 'fileName': ''})

#api for closing an image file uploaded by user
def closeFile(request):
    if request.method == "GET" and request.has_key('stack'):
        stack = request.session['stack']
        for file in stack:
            fileToDelete = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'filestore/%s' % file))
            os.remove(fileToDelete)
        request.session.pop('email')
        request.session.pop('stack')
        request.session.pop('name')
        return JsonResponse({'response': 'closed'})
    else:
        return HttpResponse('')


def toGrayscale(request):
    if request.method == "GET" and request.session.has_key('stack'):
        stack = request.session['stack']
        if len(stack) > 0:
            fileAbsolutePath = stack[0]
            grayScaleFilePath = str(
                Path(fileAbsolutePath).with_suffix(''))+str(uuid.uuid4())+'.png'
            grayScaleImage = cv.imread(fileAbsolutePath)
            grayScaleImage = cv.cvtColor(grayScaleImage, cv.COLOR_BGR2GRAY)
            cv.imwrite(grayScaleFilePath, grayScaleImage)
            grayFileName = grayScaleFilePath.split('/')[-1]
            stack.insert(0, grayFileName)

            request.session['stack'] = stack
            return JsonResponse({'response': 'convertedToGrayScale'})

        else:
            return HttpResponse()


def scaleIt(request):
    if request.method == "POST" and request.session.has_key('stack'):
        stack = request.session['stack']
        if len(stack) > 0:
            newX = int(request.POST['newWidth'])
            newY = int(request.POST['newHeight'])
            request.session['size'] = (newX, newY)
            fileAbsolutePath = stack[0]

            scaledFilePath = str(Path(fileAbsolutePath).with_suffix(
                ''))+str(uuid.uuid4())+'.png'
            originalImage = cv.imread(fileAbsolutePath)
            newImage = cv.resize(originalImage, (newX, newY),
                                 interpolation=cv.INTER_AREA)
            request.session['size'] = newImage.shape
            cv.imwrite(scaledFilePath, newImage)

            scaledFileName = scaledFilePath.split('/')[-1]
            stack.insert(0, scaledFileName)
            request.session['stack'] = stack
            return JsonResponse({'response': 'scaled'})

        else:
            return HttpResponse()


def rotateIt(request):
    if request.method == "POST" and request.session.has_key('stack'):
        stack = request.session['stack']
        if len(stack) > 0:
            fileAbsolutePath = stack[0]
            rotatefilepath = str(Path(fileAbsolutePath).with_suffix(
                ''))+str(uuid.uuid4())+'.png'
            rotateImage = cv.imread(fileAbsolutePath)
            (h, w) = rotateImage.shape[:2]
            center = (w/2, h/2)
            angle = int(request.POST['angleRange'])
            scale = 1.0
            M = cv.getRotationMatrix2D(center, angle, scale)
            rotated180 = cv.warpAffine(rotateImage, M, (h, w))

            cv.imwrite(rotatefilepath, rotated180)
            gfilename = rotatefilepath.split('/')[-1]
            stack.insert(0, gfilename)
            request.session['stack'] = stack
            return JsonResponse({'response': 'rotated'})
    else:
        return HttpResponse()


def setBorder(request):
    if request.method == 'POST' and request.session.has_key('stack'):
        topBorderSize = int(request.POST['topBorderSize'])
        bottomBorderSize = int(request.POST['bottomBorderSize'])
        rightBorderSize = int(request.POST['rightBorderSize'])
        leftBorderSize = int(request.POST['leftBorderSize'])
        borderType = request.POST['borderType']
        borderColor=request.POST['borderColor']
        border=cv.BORDER_CONSTANT

        if borderType=='color':
            border=cv.BORDER_CONSTANT
        elif borderType=='reflect':
            border=cv.BORDER_REFLECT
        elif borderType=='replicate':
            border=cv.BORDER_REPLICATE

        stack = request.session['stack']
        request.session['topBorderSize'] = topBorderSize
        request.session['bottomBorderSize'] = bottomBorderSize
        request.session['leftBorderSize'] = leftBorderSize
        request.session['rightBorderSize'] = rightBorderSize
        fileAbsolutePath = stack[0]
        borderfilePath = str(Path(fileAbsolutePath).with_suffix(
            ''))+str(uuid.uuid4())+'.png'
        borderImage = cv.imread(fileAbsolutePath)
        row, col = borderImage.shape[:2]
        bottom = borderImage[row-2, row, 0:col]
        mean = cv.mean(bottom)[0]
        border = cv.copyMakeBorder(borderImage, top=topBorderSize, bottom=bottomBorderSize, left=leftBorderSize,
                                   right=rightBorderSize, borderType=border, value=[mean, mean, mean])

        cv.imwrite(borderfilePath, border)
        borderFileName = borderfilePath.split('/')[-1]
        stack.insert(0, borderFileName)
        request.session['stack'] = stack
        return JsonResponse({'response': 'Croped'})
    else:
        return HttpResponse('')

def enhanceImage(request):
    if request.method == 'POST' and request.session.has_key('stack'):
        brightnessValue=int(request.POST['brightnessInput'])
        contrastValue=int(request.POST['contrastInput'])
        stack = request.session['stack']
        fileAbsolutePath = stack[0]
        enahnceImagefilePath = str(Path(fileAbsolutePath).with_suffix(
            ''))+str(uuid.uuid4())+'.png'
        enhanceImage = cv.imread(fileAbsolutePath)

        enhancedImage=controller(enhanceImage,brightnessValue,contrastValue)
        cv.imwrite(enahnceImagefilePath, enhancedImage)
        enhancedImageFileName = enahnceImagefilePath.split('/')[-1]
        stack.insert(0, enhancedImageFileName)
        request.session['stack'] = stack
        return JsonResponse({'response': 'Croped'})
    else:
        return HttpResponse('')

def controller(img, brightness=255, contrast=127):
    brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
    contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            max = 255
        else:
            shadow = 0
            max = 255 + brightness
        al_pha = (max - shadow) / 255
        ga_mma = shadow
        cal = cv.addWeighted(img, al_pha,img, 0, ga_mma)
    else:
        cal = img
    if contrast != 0:
        Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
        Gamma = 127 * (1 - Alpha)
        cal = cv.addWeighted(cal, Alpha, cal, 0, Gamma)
    cv.putText(cal, ''.format(brightness, contrast), (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return cal


def flipImageVertically(request):
    if request.method == 'GET' and request.session.has_key('stack'):
        stack = request.session['stack']
        if len(stack) > 0:
            fileAbsolutePath = stack[0]
            flipFilePath = str(
                Path(fileAbsolutePath).with_suffix(''))+str(uuid.uuid4())+'.png'
            flipImage = cv.imread(fileAbsolutePath)
            flipImage = cv.flip(flipImage, 0)

            cv.imwrite(flipFilePath, flipImage)
            grayFileName = flipFilePath.split('/')[-1]
            stack.insert(0, grayFileName)

            request.session['stack'] = stack
        return JsonResponse({'response': 'Flipped vertically'})
    else:
        return HttpResponse({'response':''})    


def flipImageHorizontally(request):
    if request.method == 'GET' and request.session.has_key('stack'):
        stack = request.session['stack']
        if len(stack) > 0:
            fileAbsolutePath = stack[0]
            flipFilePath = str(
                Path(fileAbsolutePath).with_suffix(''))+str(uuid.uuid4())+'.png'
            flipImage = cv.imread(fileAbsolutePath)
            flipImage = cv.flip(flipImage, 1)

            cv.imwrite(flipFilePath, flipImage)
            grayFileName = flipFilePath.split('/')[-1]
            stack.insert(0, grayFileName)

            request.session['stack'] = stack
        return JsonResponse({'response': 'Flipped vertically'})
    else:
        return HttpResponse({'response':''})    


def filterImage(request):
    if request.method=='POST' and request.session.has_key('stack'):
        stack=request.session['stack']
        filterType=request.POST['filterType']

        fileAbsolutePath = stack[0]
        filterFilePath = str(
                Path(fileAbsolutePath).with_suffix(''))+str(uuid.uuid4())+'.png'
        filterImage = cv.imread(fileAbsolutePath)

        if filterType=='Blur':
            filteredImage = cv.blur(filterImage,(10,10))
        elif filterType=='Sharpen':
            kernel_sharpening = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
            filteredImage = cv.filter2D(filterImage, -1, kernel_sharpening)
        elif filterType=='Negative':
            filteredImage = cv.bitwise_not(filterImage)
    
        cv.imwrite(filterFilePath,filteredImage)    
        filterFileName = filterFilePath.split('/')[-1]
        stack.insert(0, filterFileName)

        request.session['stack'] = stack
        return JsonResponse({'response': 'Flipped vertically'})
    else:
        return HttpResponse({'response':''})    


def downloadFile(request):
    fileResponse = open(
        'F:\PythonDjangoProject\django\projiproc\iprocone\hello.zip', 'rb')
    return fileResponse
    # return JsonResponse({'response':'Download file'})


def download_zipfile(request):
  stack=request.session['stack']
  zip_name="ImageProcessingTestImages.zip"
  byte_data=io.BytesIO()
  zipObj=zipfile.ZipFile(byte_data, 'w') 
  index=0
  for i in stack:
      fileName=os.path.basename(os.path.normpath(i))
      zipObj.write(i,fileName)
  zipObj.close()
  response = HttpResponse(byte_data.getvalue(), content_type='application/zip')
  response['Content-Disposition'] = 'attachment; filename=%s' %zip_name

  return response


def undo(request):
    if request.method=="GET" and request.session.has_key('stack') and len(request.session['stack'])>1:
        stack=request.session['stack']
        fileDelete=stack.pop(0)
        #fileDelete=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack.pop(0)))
        os.remove(fileDelete)
        request.session['stack']=stack
        return JsonResponse({"response":"undid"})
    else:
        return HttpResponse('')


def addWatermark(request):
    if request.method == 'POST' and request.session.has_key('stack'):
        xCoordinate = int(request.POST['xCoordinate'])
        yCoordinate = int(request.POST['yCoordinate'])
        Watermark = str(request.POST['Watermark'])
        transparencyValue=int(request.POST['transparencyRange'])

        request.session['xCoordinate'] = xCoordinate
        request.session['yCoordinate'] = yCoordinate
        request.session['Watermark'] = Watermark
        request.session['transparencyValue'] = transparencyValue

        stack = request.session['stack']
        fileAbsolutePath = stack[0]

        watermarkFilePath = str(Path(fileAbsolutePath).with_suffix(
                ''))+str(uuid.uuid4())+'.png'
        watermarkImage = cv.imread(fileAbsolutePath)

        if 'textRadio' in request.POST:
            textWatermark=str(request.POST['textRadio'])
            borderColor = request.POST['borderColor']
            thicknessValue = int(request.POST['thicknessRange'])
            fontScaleValue=int(request.POST['fontScaleRange'])

            request.session['borderColor'] = borderColor
            request.session['thicknessValue'] = thicknessValue
            request.session['fontScaleValue'] = fontScaleValue

            coordinates=(xCoordinate, yCoordinate)

            color = (255, 0, 0)
            font = cv.FONT_HERSHEY_SIMPLEX
            org = (50, 50)
            fontScale = 1
            color=hex2rgb(borderColor)

    #        color=tuple(int(borderColor[i:i+2], 16) for i in (0, 2, 4))
    #        color = (255, 0, 0)
            thickness = 2
            border = cv.putText(watermarkImage, Watermark, org, font, 
                    fontScale, color, thickness, cv.LINE_AA)
            #border = cv.putText(borderImage, Watermark, coordinates, cv.FONT_HERSHEY_SIMPLEX,fontScaleValue, color, thicknessValue,cv.LINE_AA)
        elif 'customRadio1' in request.POST:
            imageFile = request.FILES['fileName']
            fileSystemStorage = FileSystemStorage()
            imageFileName = fileSystemStorage.save(imageFile.name, imageFile)
            imagePath = os.path.abspath(os.path.join(os.path.dirname(
                __file__), '..', 'filestore/%s' % imageFileName))
            image = cv.imread(imagePath)
            (h, w) = image.shape[:2]
            r = 500/float(h)
            dim = (int(w*r), 500)

            stdImage = cv.resize(image, dim, interpolation=cv.INTER_AREA)
            stdImagePath = str(Path(imagePath).with_suffix('')) + \
                str(uuid.uuid4())[-3:]+'.png'
            cv.imwrite(stdImagePath, stdImage)

            logo = cv.imread(stdImagePath)
            h_logo, w_logo, _ = logo.shape

            img = watermarkImage
            h_img, w_img, _ = img.shape

            center_y = int(h_img / 2)
            center_x = int(w_img / 2)
            top_y = center_y - int(h_logo / 2)
            left_x = center_x - int(w_logo / 2)
            bottom_y = top_y + h_logo
            right_x = left_x + w_logo

            # Get ROI
            roi = img[top_y: bottom_y, left_x: right_x]
                # Add the Logo to the Roi
            result = cv.addWeighted(roi, 1, logo, 0.3, 0)
                # Replace the ROI on the image
            img[top_y: bottom_y, left_x: right_x] = result
            border=img

        cv.imwrite(watermarkFilePath, border)
        watermarkFileName = watermarkFilePath.split('/')[-1]
        stack.insert(0, watermarkFileName)
        request.session['stack'] = stack
        return JsonResponse({'response': 'Croped'})
    else:
        return HttpResponse('')
