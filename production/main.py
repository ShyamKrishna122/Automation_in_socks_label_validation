from constants import Constants
import cv2
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import pytesseract
from pytesseract import Output
import re
from PIL import Image 
from numpy import asarray 
import time

start_time = time.time()

def setPytessaract():
    pytesseract.pytesseract.tesseract_cmd = Constants.tessaract_exe_path

class ProductionSet():
    def __init__(self,feature_pts,feature_types,test_img,model):
        self.feature_pts = feature_pts
        self.feature_types = feature_types
        setPytessaract()
        self.mas_img = cv.imread(f"{Constants.master_image_path}{model}.jpg")
        self.test_img =  cv.imread(test_img)
        self.test2 = self.test_img.copy()
        self.isValid = True
        self.correctCoordinates = []
        self.result = {}
        # self.checkAllFeatures()


    def templateMatching(self,template):

        img = self.test_img.copy()

        w, h = template.shape[1],template.shape[0]

        meth = 'cv.TM_CCOEFF_NORMED'

        method = eval(meth)

        res = cv.matchTemplate(img,template,method)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        top_left = max_loc

        bottom_right = (top_left[0] + w, top_left[1] + h)
        print(top_left,bottom_right)
        pts = top_left + bottom_right
        cv.rectangle(img,top_left, bottom_right, (255,0,0), 2)
        img = cv.resize(img,(300,800))
        cv.imshow('detected',img)

        cv.waitKey(0)

        return pts

    def extractText(self,image):

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # gray_image = image
        # converting it to binary image by Thresholding 
        # this step is require if you have colored image because if you skip this part 
        # then tesseract won't able to detect text correctly and this will give incorrect result
        threshold_img = gray_image
        cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # cv2.imshow('threshold image', threshold_img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        custom_config = r'--oem 3 --psm 6'

        details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang='eng')

        total_boxes = len(details['text'])
        for sequence_number in range(total_boxes):
            if int(details['conf'][sequence_number]) >30:
                (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number],  details['height'][sequence_number])
                threshold_img = cv2.rectangle(threshold_img, (x, y), (x + w, y + h), (255, 255, 0), 2)


        # cv2.imshow('master image', threshold_img)

        # cv2.waitKey(0)

        # cv2.destroyAllWindows()

        last_word = ''
        text = ''
        arr = []

        for word in details['text']:
            if word!='':
                last_word = word
                text+=word
                
            if (last_word!='' and word == '') or (word==details['text'][-1]):

                text = re.sub('[^a-zA-Z0-9/\\ \n]', '', text)
                arr.append(text)
                text = ''

        #print(arr)

        return arr


    def compareText(self,template,pts):

        a = self.extractText(template)
        b = self.extractText(self.test_img[pts[1]:pts[3],pts[0]:pts[2]])

        cnt = 0
        print(a)
        print(b)

        if(len(a)==len(b)):
            for i in range(len(a)):
                if(a[i]==b[i]): cnt+=1
            if(cnt >= len(a) - 3): print("Text equal")
            else: 
                print("Text not equal")
                self.isValid = False
        else:
            print("Text not equal")
            self.isValid = False

    def showColor(self,img1):
            
        numpydata1 = asarray(img1)  

        a = [0]*3   
        cnt = img1.shape[0]*img1.shape[1]

        for i in range(len(numpydata1)):

            for j in range(len(numpydata1[0])):

                a[0] += numpydata1[i][j][0]
                a[1] += numpydata1[i][j][1]
                a[2] += numpydata1[i][j][2]
                    
        a[0] = a[0]/cnt
        a[1] = a[1]/cnt
        a[2] = a[2]/cnt

        return a

    def compareColor(self,template,pts):
        
        a = self.showColor(template)
        b = self.showColor(self.test_img[pts[1]:pts[3],pts[0]:pts[2]])

        print(a)
        print(b)

        if(abs(a[0]-b[0]) <= 40 and abs(a[1]-b[1]) <= 40 and abs(a[2]-b[2]) <= 40):
            print("same color")
        else: self.isValid = False


    def mse(self,imageA, imageB):
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        return err

    def compare_images(self,imageA, imageB, title):
            
        m = self.mse(imageA, imageB)
            #s = ssim(imageA, imageB)
            #SSIM: %.2f,s
        fig = plt.figure(title)
        plt.suptitle("MSE: %.2f" % (m))
        print(m)

        if(m<=6000):
            # pass
            print("images are equal")   
        else:
            #pass
            print("images not equal")  
            self.isValid = False 
        
        # ax = fig.add_subplot(1, 2, 1)
        # plt.imshow(imageA) #cmap = plt.cm.gray
        # plt.axis("off")
            
        # ax = fig.add_subplot(1, 2, 2)
        # plt.imshow(imageB)  #, cmap = plt.cm.gray
        # plt.axis("off")
        # plt.show()       

    def featureMatching(self,template,pts):
        
        w,h = template.shape[1],template.shape[0]

        original = cv.cvtColor(template,cv.COLOR_BGR2RGB)
        
        duplicate = self.test_img[pts[1]:pts[3],pts[0]:pts[2]]
        # cv.imshow("dup",duplicate)
        duplicate = cv.cvtColor(duplicate,cv.COLOR_BGR2RGB)
        duplicate = cv.resize(duplicate,(w,h))

        fig = plt.figure("Images")
        images = ("Original", original), ("duplicate", duplicate)

        # for (i, (name, image)) in enumerate(images):
        #     ax = fig.add_subplot(1, 3, i + 1)
        #     ax.set_title(name)
        #     plt.imshow(image) #cmap = plt.cm.gray
        #     plt.axis("off")
        # plt.show()

        self.compare_images(original, duplicate, "Original vs. duplicate")

    def checkAllFeatures(self):

        for i in range(len(self.feature_pts)):   

            pts = self.feature_pts[i]
            ftype = self.feature_types[i]
            print(ftype+" feature "+str(i))

            template = self.mas_img[pts[1]:pts[3],pts[0]:pts[2]]


            detected_pts =  self.templateMatching(template)

            if(ftype == 'Image'): 
                self.featureMatching(template,detected_pts) 
            elif(ftype == 'Text'):
                self.compareText(template,detected_pts)
                if(self.isValid):
                    self.compareColor(template,detected_pts)
            
            if(not self.isValid):
                print("Stopped in feature "+str(i))
                print("INVALID CARD ELIMINATE !")
                self.result["Feature "+str(i+1)+" - "+str(ftype)] = ' Not matched '
                return detected_pts

            else:
                self.result["Feature "+str(i+1)+" - "+str(ftype)] = ' Matched ' 
            

            self.correctCoordinates.append(list(detected_pts))

        return self.correctCoordinates
        