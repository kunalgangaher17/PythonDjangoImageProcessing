from django.shortcuts import render
from django.http import *
import datetime
from django.core.files.storage import FileSystemStorage
import os
import cv2 as cv
import uuid
from pathlib import Path


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
        print(stdImagePath)
        cv.imwrite(stdImagePath, stdImage)
        stdFileName = stdImagePath.split('/')[-1]

        stack.append(stdFileName)
        request.session['stack'] = stack
        print(image.shape)

    return JsonResponse({'fileName': imageFileName})


def getState(request):
    return JsonResponse({'state': 'none', 'name': '', 'email': '', 'fileName': ''})


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
            print("New X :"+str(newX)+", newY :"+str(newY))
            request.session['size'] = (newX, newY)
            fileAbsolutePath = stack[0]
            print(
                "File path from stack[0] from ScaleIt method :"+str(stack[0]))
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
            # here dirty coding......
            rotatefilepath = str(Path(fileAbsolutePath).with_suffix(
                ''))+str(uuid.uuid4())+'.png'
            rotateImage = cv.imread(fileAbsolutePath)
            (h, w) = rotateImage.shape[:2]
            center = (w/2, h/2)
            print(request.POST.__dict__)
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


def downloadFile(request):
    fileResponse = open(
        'F:\PythonDjangoProject\django\projiproc\iprocone\hello.zip', 'rb')
    return fileResponse
    # return JsonResponse({'response':'Download file'})

# Create your views here.
