import os
import cv2
import sys
import random
import numpy as np


def draw_rects(img, x1, y1, x2, y2, color):
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

class Eigenfaces(object):                                                       
    images = 400                                      
    m = 92                                                                      
    n = 112                                                                     
    mn = m * n                                                                  
    
    def __init__(self, limit = 0.85):
        self.limit = limit
        
        L = np.empty(shape=(self.mn, self.images), dtype='float64')

        i = 0
        for imgfolder in os.listdir('./Bioid/'):
            for filename in os.listdir('./Bioid/' + imgfolder):
                filename = './Bioid/' + imgfolder + '/'+ filename
                if (filename.lower().endswith(('.png', '.jpg', '.jpeg','.pgm'))):
                    img=cv2.imread(filename,0)

                    img = cv2.resize(img, (92,112), interpolation = cv2.INTER_AREA)

                    img_col = np.array(img, dtype='float64').flatten()
                    L[:, i] = img_col[:]                              
                    i += 1                                           

        self.mean_img = np.sum(L, axis=1) / self.images            
        
        for j in range(0, self.images):                                
            L[:, j] -= self.mean_img[:]

        covariance = np.matrix(L.transpose()) * np.matrix(L)      
        covariance /= self.images                                                             

        eigenvalues, eigenvectors = np.linalg.eig(covariance)                          
        sort = eigenvalues.argsort()[::-1]                             
        eigenvalues = eigenvalues[sort]                               
        eigenvectors = eigenvectors[sort]                             
        
        eigenvalues_sum = sum(eigenvalues[:])                                      
        eigenvalues_count = 0                                                       
        eigenvalues_limit = 0.0
        for eigenvalue in eigenvalues:
            eigenvalues_count += 1
            eigenvalues_limit += eigenvalue / eigenvalues_sum

            if eigenvalues_limit >= self.limit:
                break

        eigenvalues = eigenvalues[0:eigenvalues_count]                            
        eigenvectors = eigenvectors[0:eigenvalues_count]

        eigenvectors = eigenvectors.transpose()                               
        eigenvectors = L * eigenvectors                                       
        norms = np.linalg.norm(eigenvectors, axis=0)                          
        self.eigenvectors = eigenvectors / norms  
        self.W = self.eigenvectors.transpose() * L
        
    def classify(self, img):

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.equalizeHist(gray)

        
        img = cv2.resize(img,(92, 112), interpolation = cv2.INTER_AREA)   
        imgs = np.array(img, dtype='float64').flatten()  

        
        imgs -= self.mean_img
        imgs = np.reshape(imgs, (self.mn, 1))
        
        S = self.eigenvectors.transpose() * imgs                               
        
        diff = self.W - S                                                       
        
        norms = np.linalg.norm(diff, axis=0)

        liv = np.argmin(norms)                                     
        return liv,norms


if __name__ == "__main__":
    efaces = Eigenfaces()
    
    capture = 0
    
    cam = cv2.VideoCapture(0)
    images = []
    runtime = 0
    height1, width1, channels1 = 0,0,0
    import time
    start = time.time()
    
    while True:
        ret,img = cam.read()
        img = cv2.flip(img, 1)
        
        
        if ret == False:
            break
        if(runtime%2==0):
            
            height1, width1, channels1 = img.shape

            div = int(width1/150)

            if(div == 0):
                div = 1

            vis = cv2.resize(img,(int(width1/div), int(height1/div)), interpolation = cv2.INTER_AREA)
            height, width, channels = vis.shape

            x = 46
            y = 56

            nom=[]
            xy = []
            for i in range(1):
                w = 0
                for a in range(width):
                    h = 0
                    if((w + x)>width):
                        break
                    for b in range(height):
                        if((h + y)>height):
                            break
                        temp = vis[h : h + y, w : w + x]
                        liv,norms = efaces.classify(temp)
                        nom.append(norms[liv])
                        xy.append([h*div,y*div,w*div,x*div])

                        h += 5

                    w += 5
                x -= 10
                y -= 12

            low = np.argmin(nom)
            h,y,w,x=xy[low]
        
        runtime +=1
        if(nom[low]<=4000):  
            draw_rects(img, w,h,w + x-5,h + y-5, (255,0,0))

        images.append(img)
        
        cv2.imshow('cam',img)
        if cv2.waitKey(1) == 27: 
            break
    cv2.destroyAllWindows()
        
    done = time.time()
    elapsed = done - start
    print(elapsed)
    
    cam.release()
    
    if(capture==0):
        out = cv2.VideoWriter('output2.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 25, (width1,height1))

        for image in images:
            out.write(image)

        out.release()

