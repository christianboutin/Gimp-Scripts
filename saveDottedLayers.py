##-----------------------------------------------------------------------------
##This source file is part of Exequor Studios' Gimp Scripts
##For the latest info, see http://exequor.com/
##
##Copyright (c) 2011 Exequor Studios Inc.
##
##Permission is hereby granted, free of charge, to any person obtaining a copy
##of this software and associated documentation files (the "Software"), to deal
##in the Software without restriction, including without limitation the rights
##to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
##copies of the Software, and to permit persons to whom the Software is
##furnished to do so, subject to the following conditions:
##
##The above copyright notice and this permission notice shall be included in
##all copies or substantial portions of the Software.
##
##THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
##IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
##FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
##AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
##LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
##OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
##THE SOFTWARE.
##-----------------------------------------------------------------------------

from gimpfu import *
import time
import os
import sys
import traceback
import xml.dom
import xml.dom.minidom


gettext.install("gimp20-python", gimp.locale_directory, unicode=True)

class layerGroup:
    mName=""
    mX=0
    mY=0
    mW=0
    mH=0
    mLayer=[]

    def __init__(self, i,img):
        self.mLayer=[]
        self.mName = groupNameFromLayer(i,img)
        self.mX=i.offsets[0]
        self.mY=i.offsets[1]
        self.mW=i.width
        self.mH=i.height
        self.mLayer.append(i)

    def addLayer(self,i):
        self.mLayer.append(i)
        log("mLayer size is now %(x)d"%{"x":len(self.mLayer)})

        #deconstructing XYWH into X1Y1X2Y2 for easier reading/understanding
        
        myX1 = self.mX
        myY1 = self.mY
        myX2 = self.mX+(self.mW-1)
        myY2 = self.mY+(self.mH-1)

        newX1 = i.offsets[0]
        newY1 = i.offsets[1]
        newX2 = i.offsets[0]+(i.width-1)
        newY2 = i.offsets[1]+(i.height-1)

        if (myX1 > newX1):
            myX1 = newX1

        if (myY1 > newY1):
            myY1 = newY1

        if (myX2 < newX2):
            myX2 = newX2

        if (myY2 < newY2):
            myY2 = newY2

        self.mX = myX1
        self.mY = myY1

        self.mW = (myX2-myX1)+1
        self.mH = (myY2-myY1)+1

    def turnOffLayers(self):
        log("-------------")
        log("Turning off : ")
        for i in self.mLayer:
            log(i.name)
            pdb.gimp_drawable_set_visible(i, False)
        log("-------------")
        
    def turnOnLayers(self):
        log("-------------")
        log("Turning on : ")
        for i in self.mLayer:
            log(i.name)
            pdb.gimp_drawable_set_visible(i, True)
        log("-------------")
        
def isDotted(layer):
    if (layer.name.find(".")!= -1):
        return True;
    else:
        return False;
        

def groupNameFromLayer(layer, img):
    if (layer.name.find(".")== -1):
        return ""
    elif (layer.name.find("$")!= -1):
        return layer.name.split("|")[0].replace("$",img.filename.split(".")[0].rsplit("\\",1)[1])
    else:
        return layer.name.split("|")[0]

def log(string):
        ffile = open("C:\\temp\\saveDottedLayersLog.txt","at+")
        ffile.write(string+"\n")
        ffile.close()
    

def saveLayer(img, layer):
    output_path = "."
    exportGroup=[]
    previousStatus=[]
    ffile = open("C:\\temp\\saveDottedLayersLog.txt","wt+")
    ffile.close()
    try:
        img.undo_group_start()
        root_name = img.filename.split(".")[0]
        output_path = img.filename.rsplit("\\", 1)[0]
        try:
            pfile = open(root_name+".txt","rt+")
            output_path = output_path + "\\"+ pfile.readline()
            pfile.close()
        except IOError:
            output_path = output_path # duh
        

        doc = xml.dom.minidom.Document()
        elem = doc.createElementNS("root", "root")
        doc.appendChild(elem)

        for i in img.layers:
            previousStatus.append(pdb.gimp_drawable_get_visible(i))
            if isDotted(i):
                groupName = groupNameFromLayer(i, img)
                found = False
                if (groupName != ""):
                    for j in exportGroup:
                        if j.mName == groupName:
                            log("Adding : "+i.name+" to "+j.mName)
                            j.addLayer(i)
                            found = True

                if (found == False):
                    newGroup = layerGroup(i,img)
                    log("Creating group for layer : "+i.name+" with name "+newGroup.mName)
                    exportGroup.append(newGroup) # If it's not part of a group, then it is its own group
                pdb.gimp_drawable_set_visible(i, False)

                
        log("---")
        log("%(x)d"%{"x":len(exportGroup)})
        log("---")
        for i in exportGroup:
            newElem = doc.createElementNS("","coord")
            newElem.setAttribute("id", i.mName)
            newElem.setAttribute("x", "%(x)i"%{"x":i.mX})
            newElem.setAttribute("y", "%(x)i"%{"x":i.mY})
            newElem.setAttribute("w", "%(x)i"%{"x":i.mW})
            newElem.setAttribute("h", "%(x)i"%{"x":i.mH})
            i.turnOnLayers()
            pdb.gimp_rect_select(img, i.mX, i.mY, i.mW, i.mH, 2, False, 0)
            pdb.gimp_edit_copy_visible(img)
            new_img = gimp.Image(i.mW,i.mH,RGB)
            new_img.filename = i.mName
            layer_one = pdb.gimp_layer_new(new_img, i.mW, i.mH, 1, "LAYER01", 100, NORMAL_MODE)
            pdb.gimp_image_add_layer(new_img, layer_one, -1)
            pdb.gimp_edit_clear(layer_one)
            gimp.displays_flush()
            pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(layer_one, False))
            log(output_path+"\\"+i.mName)
            log("Type : "+i.mName[-4:])
            #pdb.gimp_file_save(new_img, layer_one, output_path+"\\"+i.mName, output_path+"\\"+i.mName)
            if (i.mName[-4:].lower() == ".jpg"):
                pdb.file_jpeg_save(new_img, layer_one, output_path+"\\"+i.mName, output_path+"\\"+i.mName,.95,0,1,1,"exequor.com",0,0,0,0)
            if (i.mName[-4:].lower() == ".png"):
                pdb.file_png_save(new_img, layer_one, output_path+"\\"+i.mName, output_path+"\\"+i.mName,0,5,1,1,1,1,1)
            else:
                pass
                #pdb.gimp_file_save(new_img, layer_one, output_path+"\\"+i.mName, output_path+"\\"+i.mName)
            
            i.turnOffLayers()
            pdb.gimp_image_delete(new_img)
            elem.appendChild(newElem)
            
            
##        for i in img.layers:
##            name = i.name
##            if (i.name.find(".")!= -1):
##                newElem = doc.createElementNS("","coord")
##                newElem.setAttribute("id", i.name)
##                newElem.setAttribute("x", "%(x)i"%{"x":i.offsets[0]})
##                newElem.setAttribute("y", "%(x)i"%{"x":i.offsets[1]})
##                newElem.setAttribute("w", "%(x)i"%{"x":i.width})
##                newElem.setAttribute("h", "%(x)i"%{"x":i.height})
##                pdb.gimp_drawable_set_visible(i, True)
##                pdb.gimp_rect_select(img, i.offsets[0], i.offsets[1], i.width, i.height, 2, False, 0)
##                pdb.gimp_edit_copy_visible(img)
##                new_img = gimp.Image(i.width,i.height,RGB)
##                new_img.filename = i.name
##                layer_one = pdb.gimp_layer_new(new_img, i.width, i.height, 1, "LAYER01", 100, NORMAL_MODE)
##                pdb.gimp_image_add_layer(new_img, layer_one, -1)
##                pdb.gimp_edit_clear(layer_one)
##                gimp.displays_flush()
##                pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(layer_one, False))
##                pdb.gimp_file_save(new_img, layer_one, output_path+"\\"+i.name, output_path+"\\"+i.name)
##                pdb.gimp_drawable_set_visible(i, False)
##                pdb.gimp_image_delete(new_img)
##                elem.appendChild(newElem)

        ofile = open(output_path+"\\"+pdb.gimp_image_get_name(img).split(".")[0]+"_coord.xml","wt+")
        ofile.writelines(doc.toprettyxml())
        ofile.close()
        for i in img.layers:
            pdb.gimp_drawable_set_visible(i,previousStatus.pop(0))
        img.undo_group_end()            


        
    except Exception, details:
        ffile = open(output_path+"\\saveDottedLayersException.txt","wt+")
        ffile.write("- Exception -")
        ffile.writelines(traceback.format_exc())
        ffile.write("-------------")
        ffile.close()

register(
    "python-fu-saveDottedLayers",
    N_("Save every dotted layers (ex: layer01.png) to a separate, cropped image."),
    "Save every dotted layers (ex: layer01.png) to a separate, cropped image.",
    "Christian Boutin",
    "Christian Boutin",
    "2008",
    N_("_Save Dotted Layers..."),
    "RGB*, GRAY*",
    [
        (PF_IMAGE, "image",       "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None)
    ],
    [],
    saveLayer,
    menu="<Image>/Export",
    domain=("gimp20-python", gimp.locale_directory)
    )

main()

