'''
Created on 14/feb/2011

@author: subbuglio
'''

class PictureDataPicker(object):
    '''
    Pick data from plots picking them and transforming value
    '''


    def __init__(self, x0_pix, x1_pix, deltax, y0_pix, y1_pix, deltay,
                 x0_val = 0., y0_val = 0., yreverse = True):
        '''
        Constructor
        '''
        self.__x0_pix = float(x0_pix)
        self.__x1_pix = float(x1_pix)
        self.__deltax = float(deltax)
        self.__y0_pix = float(y0_pix)
        self.__y1_pix = float(y1_pix)
        self.__deltay = float(deltay)
        self.__x0_val = float(x0_val)
        self.__y0_val = float(y0_val)
        self.__yreverse = float(yreverse)
        
    def getX(self, xpix):
        return (((xpix - self.__x0_pix)/(self.__x1_pix - self.__x0_pix))
                *self.__deltax) + self.__x0_val
    
    def getY(self, ypix):
        if self.__yreverse:
            return (((self.__y0_pix - ypix )/(self.__y0_pix - self.__y1_pix ))
                    *self.__deltay) + self.__y0_val
        else:
            return (((ypix - self.__y0_pix)/(self.__y1_pix - self.__y0_pix ))
                    *self.__deltay) + self.__y0_val
                    
    def getXY(self, xpix, ypix):
        return (self.getX(xpix), self.getY(ypix))
    
    def getErr(self,ypix, lo_ypix):
        return abs(self.getY(ypix)- self.getY(lo_ypix))
        
    def getXYErr(self, xpix, ypix, lo_ypix):
        return (self.getX(xpix), self.getY(ypix), self.getErr(ypix,lo_ypix))
    
    
    
if __name__ == "__main__":
    transformer = PictureDataPicker(84, 451, 7, 549, 426, 5, x0_val=1.)
    #this should give:
    #(2.659400545, 2,1414141414, 0,2828282828
    print transformer.getXYErr(171,496,503)
