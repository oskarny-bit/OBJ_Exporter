import pymel.core as pm
import maya.cmds as mc



#------------------------------------------------------------------------------------------#

def getVPoints(eachMesh, fAdd, spaceState):
    vPoints = eachMesh.getPoints(space = spaceState)
    for i in vPoints:
        fAdd.write("v ")
        for k in range(0, len(i)):
            fAdd.write(str(i[k])+" ")
        fAdd.write("\n")

def getUVTextureCoord(eachMesh, fAdd):
    uvTCForMesh = eachMesh.getUVs()
    list1 = uvTCForMesh[0]
    list2 = uvTCForMesh[1]
    for i in range(0, len(list1)):
        fAdd.write("vt "+str(list1[i])+" "+str(list2[i])+"\n")

def getVNormals(eachMesh, fAdd, spaceState):
    vnPoints = eachMesh.getNormals(space = spaceState)
    for i in vnPoints:
        fAdd.write("vn ")
        for k in range(0, len(i)):
            fAdd.write(str(i[k])+" ")
        fAdd.write("\n")
        
def getCounterV(eachMesh, spaceState, nrOfCV):
    vPoints = eachMesh.getPoints(space = spaceState)
    for i in vPoints:
        nrOfCV+=1
    return nrOfCV
    
def getCounterForVT(eachMesh, nrOfUV):
    vtPoints = eachMesh.getUVs()
    for i in vtPoints[0]:
        nrOfUV+=1
    return nrOfUV
    
def getCounterForVN(eachMesh, spaceState, nrOfNormals):
    vnPoints = eachMesh.getNormals(space = spaceState)
    for i in vnPoints:
        nrOfNormals+=1   
    return nrOfNormals

def getF(eachMesh, fAdd, nrOfCV, nrOfUV, nrOfNormals):
    faces = eachMesh.f
    for i in faces:
        faceVertIndices = i.getVertices()
        #print len(faceVertIndices)
        fAdd.write("f")
        for k in range(len(faceVertIndices)):
            fAdd.write(" "+str(faceVertIndices[k]+1 + nrOfCV)+"/"+str(i.getUVIndex(k)+1 + nrOfUV)+"/"+str(i.normalIndex(k)+1 + nrOfNormals))
        fAdd.write("\n") 
        
def TriangulateMesh(eachMesh):
        newList = eachMesh.f
        pm.polyTriangulate(newList)

def getMaterialInfo(material, materialFile, lambType, userFilePath):
    #Check to see if given material has a file attachment(data info)
    fileExists = False
    try:
        f = pm.listConnections(material, type="file")[0]
        fileExists = True
    except:
        pass

    if fileExists:
        fLocation = f.getAttr("fileTextureName")
        splitIntoWords = fLocation.split("/")
        nameOfLast = splitIntoWords[len(splitIntoWords)-1]
 
        refFile = ""
        for word in userFilePath[:len(userFilePath)-1:]:
            refFile += word+"/"
        refFile += nameOfLast
        
        #Binary Copy
        f2 = open(refFile, "wb")
        with open(fLocation, "rb")as f:
            while True:
                byte = f.read(1)
                if not byte:
                    break
                f2.write(byte[0])
        f2.close()
          
    materialFile.write("\nnewmtl ")
    materialFile.write(str(material))
    materialFile.write("\nillum 4")
    
    #Material Info Added To .mtl
    #Ka
    materialFile.write("\nKa ")
    ka = material.getAmbientColor()
    for i in ka[0:len(ka)-1:]:
        materialFile.write(str(i)+" ")
    materialFile.write("\n")
    #Kd
    materialFile.write("Kd ")
    kd = material.getColor()
    for i in kd[0:len(kd)-1:]:
        materialFile.write(str(i)+" ")
    materialFile.write("\n")
    #Transparency(Tf)
    tf = material.getTransparency()
    materialFile.write("Tf ")
    for i in tf[0:len(tf)-1:]:
        materialFile.write(str(round(1-i, 2))+" ")
    materialFile.write("\n")
    #map_Kd
    if fileExists:
        materialFile.write("map_Kd ")
        materialFile.write(nameOfLast)
    #Ni
    materialFile.write("\nNi ")
    materialFile.write(str(material.getRefractiveIndex()))   
    #Ks
    if lambType == False:
        materialFile.write("\nKs ")
        ks = material.getSpecularColor()
        for i in ks[0:len(ks)-1:]:
            materialFile.write(str(i))
            materialFile.write(" ")

def runAll(eachMesh, fAdd, spaceState, tGroup, nrOfCV, nrOfUV, nrOfNormals, material, withMaterials):
    getVPoints(eachMesh, fAdd, spaceState)
    getUVTextureCoord(eachMesh, fAdd)
    getVNormals(eachMesh, fAdd, spaceState)
    fAdd.write("s 1\ng ")
    fAdd.write(str(tGroup))
    if withMaterials:
        fAdd.write("\nusemtl ")
        fAdd.write(str(material))
    fAdd.write("\n")
    getF(eachMesh, fAdd, nrOfCV, nrOfUV, nrOfNormals)
    
#--------------------------------------------------------------------------------------------------------#    
   
def export(self):
    spaceState = ""
    lambType = True
    material = ""
    triangulationTempt = False
    withMaterials = False
    nrOfCV = 0
    nrOfUV = 0
    nrOfNormals = 0
    directory = ""
    
    #UserInputPopup
    placeHolderDialog = str(pm.fileDialog(m = 1))
    
    userFilePath = placeHolderDialog.split("/")
    userFilePath[len(userFilePath)-1] = userFilePath[len(userFilePath)-1].replace("*", "obj")
    
    directory += userFilePath[0]
    for i in userFilePath[1:len(userFilePath):]:
        directory += "/"
        directory += i

    fAdd = open(directory, "a+")

    #SpaceMode
    if(mc.checkBoxGrp(checkBoxes,q=1,v4=1)):
        spaceState = "object"
        
    else:
        spaceState = "world"
    print " STATE:", spaceState
    
    #Selection
    if(mc.checkBoxGrp(checkBoxes,q=1,v1=1)):
        if(mc.checkBoxGrp(checkBoxes,q=1,v3=1)):
            fAdd.write("mtllib ")
            fAdd.write(userFilePath[len(userFilePath)-1].replace("obj", "mtl")+"\n")
        tGroup = pm.ls(sl = True)
        meshList = pm.listRelatives(tGroup, type="mesh")
        for eachMesh in meshList:
            tGroup = pm.listRelatives(eachMesh, p=True)[0]
            faces = eachMesh.f
            
            #Material
            if(mc.checkBoxGrp(checkBoxes,q=1,v3=1)):
                pathToMaterial = directory.replace("obj", "mtl")
                materialFile = open(pathToMaterial, "a+")
                shadingEngine = pm.listConnections(eachMesh, type="shadingEngine")
                print shadingEngine
                withMaterials = True
                
                #Tests to see what material is applied to shadingEngine
                try:
                    material = pm.listConnections(shadingEngine, type="blinn")[0]
                    lambType = False
                    
                except:
                    material = pm.listConnections(shadingEngine, type="lambert")[0]
                    lambType = True
                getMaterialInfo(material, materialFile, lambType, userFilePath)
                materialFile.close()
            
            #Triangulation of faces on each mesh
            if(mc.checkBoxGrp(checkBoxes,q=1,v2=1)):
                TriangulateMesh(eachMesh)
                triangulationTempt = True
            else:
                pass
                    
            fAdd.write("\ng default\n")
            #Input all info from checkBoxes
            runAll(eachMesh, fAdd, spaceState, tGroup, nrOfCV, nrOfUV, nrOfNormals, material, withMaterials)
            nrOfCV = getCounterV(eachMesh, spaceState, nrOfCV)
            nrOfUV = getCounterForVT(eachMesh, nrOfUV)
            nrOfNormals = getCounterForVN(eachMesh, spaceState, nrOfNormals)    
    else:
        #Material    
        if(mc.checkBoxGrp(checkBoxes,q=1,v3=1)):
            fAdd.write("mtllib ")
        fAdd.write(userFilePath[len(userFilePath)-1].replace("obj", "mtl")+"\n")
        meshList = pm.ls(type="mesh")
        for eachMesh in meshList:
            tGroup = pm.listRelatives(eachMesh, p=True)[0]
            faces = eachMesh.f 

            #Material
            if(mc.checkBoxGrp(checkBoxes,q=1,v3=1)):
                pathToMaterial = directory.replace("obj", "mtl")
                materialFile = open(pathToMaterial, "a+")
                shadingEngine = pm.listConnections(eachMesh, type="shadingEngine")
                withMaterials = True
                
                #Tests to see what material is applied to shadingEngine
                try:
                    material = pm.listConnections(shadingEngine, type="blinn")[0]
                    lambType = False
                    
                except:
                    material = pm.listConnections(shadingEngine, type="lambert")[0]
                    lambType = True
                getMaterialInfo(material, materialFile, lambType, userFilePath)
                materialFile.close()
                
            #Triangulation of faces on each mesh
            if(mc.checkBoxGrp(checkBoxes,q=1,v2=1)):
                TriangulateMesh(eachMesh)
                triangulationTempt = True
            else:
                pass
                     
            fAdd.write("\ng default\n")   
            #Input all info from checkBoxes
            runAll(eachMesh, fAdd, spaceState, tGroup, nrOfCV, nrOfUV, nrOfNormals, material, withMaterials)
            nrOfCV = getCounterV(eachMesh, spaceState, nrOfCV)
            nrOfUV = getCounterForVT(eachMesh, nrOfUV)
            nrOfNormals = getCounterForVN(eachMesh, spaceState, nrOfNormals)
    
    fAdd.close()
    
    if triangulationTempt:
        for eachMesh in meshList:
            pm.undo()

if mc.window('window1', exists =True):
    mc.deleteUI('window1')

window1 = mc.window(title = "Export Window", widthHeight=(500, 200) )
mc.frameLayout(l = "Basic Options", bgc = (0.3, 0.5, 0))
checkBoxes = mc.checkBoxGrp( numberOfCheckBoxes=4, labelArray4=['Export Selection', 'Triangulate', 'Export Material', "Space(Checked:'Local')"] )
mc.button( label='Export', c = export)
mc.showWindow(window1)