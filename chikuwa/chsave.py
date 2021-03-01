import os
import xml.etree.ElementTree as ET
import zipfile
import shutil
import uuid

import chclass
#from ElementTree_pretty import prettify
def expTofile(cv,path):
    dirname = os.path.dirname(path)
    filename = os.path.basename(path)
    tmpname = 'tmp_'+str(uuid.uuid4())
    tmppath = os.path.join(dirname,tmpname)
    xmlnames = ['shapes.xml','objs.xml','lines.xml','info.xml']
    xml_tmp_paths = []
    xml_zip_names = []
    for name in xmlnames:
        xml_tmp_paths.append(os.path.join(tmppath,name))
        xml_zip_names.append(os.path.join('data',name))
    zip_tmp_path = os.path.join(tmppath,tmpname+'.zip')
    os.chdir(dirname)
    try:
        os.mkdir(tmpname)
    except:
        return False
    else:
        dumpShapes(cv,xml_tmp_paths[0])
        dumpObjs(cv,xml_tmp_paths[1])
        with zipfile.ZipFile(zip_tmp_path,'w') as zf:
            zf.write(xml_tmp_paths[0],arcname=xml_zip_names[0])
            zf.write(xml_tmp_paths[1],arcname=xml_zip_names[1])
        shutil.move(zip_tmp_path,path)
        shutil.rmtree(tmppath)
        return True
def dumpObjs(cv,path):
    top = ET.Element('Properties',{'type':'objs'})
    for obj in cv.objs:
        child = ET.SubElement(top,'objs',{'uuid':str(obj.uuid)})
        p = {
            'text':obj.text,
            'textSize':obj.textSize,
            'visible':obj.visible,
            'isOutlineVisible':obj.isOutlineVisible,
        }
        c = {
            'outlineColor':obj.outlineColor,
            'textColor':obj.textColor,
            'bgColor':obj.bgColor,
        }
        decomposerCore(p,child)
        decomposerCoreColour(c,child)
        ET.SubElement(child,'pos',{'x':str(obj.pos[0]),'y':str(obj.pos[1])})
    string = ET.tostring(top,xml_declaration=True)
    with open(path,'bw') as f:
        f.write(string)
    return True
        

def dumpShapes(cv,path):
    top = ET.Element("Properties",{'type':'shapes'})
    sub = ET.SubElement(top,'Person')
    personDecomposer(cv.shapes,sub)
    sub2 = ET.SubElement(top,'Relation')
    fgComplexDecomposer(cv.shapeRelation.PairList,sub2)
    sub3 = ET.SubElement(top,'Siblings')
    fgComplexDecomposer(cv.shapeSiblings.SiblingList,sub3)
    sub4 = ET.SubElement(top,'PCRL')
    fgGroupDecomposer(cv.shapePCRL.pcRelationList,sub4)
    #cv.objs,cv.lines
    string = ET.tostring(top,xml_declaration=True)
    f = open(path, 'bw')
    f.write(string)
    f.close()
    return True
    
def fgGroupDecomposer(fggList,parent):
    for fgg in fggList:
        child = ET.SubElement(parent,'FGGroup',{'uuid':fgg.uuid})
        for fg in fgg.member:
            grandchild = ET.SubElement(child,'member',{'uuid':fg.uuid})

def fgComplexDecomposer(fgList,parent):
    for fg in fgList:
        fgDecomposer(fg,parent)
    
def fgDecomposer(fg,parent):
    top = ET.SubElement(parent,'FamilyGroup',{'uuid':fg.uuid})
    p = {
        'isParent':fg.isParent,
        'isDivorced':fg.isDivorced,
        'offsetYPercent':fg.offsetYPercent,
        'offsetXPercent':fg.offsetXPercent,
        'markOffsetXPercent':fg.markOffsetXPercent
    }
    decomposerCore(p,top)
    subtop = ET.SubElement(top,'member')
    for person in fg.member:
        child = ET.SubElement(subtop,'person',{'id':person.uuid})
        
    for multi in fg.MultiBirthList:
        subtop2 = ET.SubElement(top,'multi')
        for mem in multi.member:
            child = ET.SubElement(subtop2,'person',{'id':mem.uuid})
        child = ET.SubElement(subtop2,'isMonozygotic',{'value':str(int(multi.isMonozygotic))})
    
def personDecomposer(shapes,parent):
    for person in shapes:
        info = person.info
        pC = ET.SubElement(parent,'person',{'uuid':person.uuid,'type':str(type(person))})
        if type(person) is chclass.Person:
            ifcDecomposer(info,pC)
        elif type(person) is chclass.PreNotCT:
            iffDecomposer(info,pC)
        p = {"pos":person.pos,"adopFlag":person.adopFlag}
        for index,data in p.items():
            if index == 'pos':
                child = ET.SubElement(pC,index,{'x':str(data[0]),'y':str(data[1])})
            elif index == 'adopFlag':
                child = ET.SubElement(pC,index)
                child.text = str(int(data))  
    return True
    
    
def ifcDecomposer(info,parent):
    top = ET.SubElement(parent,'info')
    p = {
        "sex":info.sex,
        "age":info.age,
        "ageUnit":info.ageUnit,
        "statType":info.statType,
        "affType":info.affType,
        "isMarked":info.isMarked,
        "isAdopted":info.isAdopted
        #isDocumentedEval = False, # add*
        #examList=[],
        #diseaseList=[]
    }
    decomposerCore(p,top)
    disease = ET.SubElement(top,'disease')
    for yr,di in info.diseaseList:
        child = ET.SubElement(disease,'data',{'yr':str(yr),'di':di})

    return True

def iffDecomposer(info,parent):
    top = ET.SubElement(parent,'info')
    p = {
        "sex":info.sex,
        "age":info.age,
        "statType":info.statType,
        'affType':info.affType
    }
    decomposerCore(p,top)
    footer = ET.SubElement(top,'footer')
    footer.text = str(info.footer)
    return True

def decomposerCore(prop,parent):
    for index,data in prop.items():
        child = ET.SubElement(parent,index)
        child.text = str(data)
    return True

def decomposerCoreColour(prop,parent):
    for index,data in prop.items():
        cT = data.Get(includeAlpha=True)
        coldic = {'r':str(cT[0]),'g':str(cT[1]),'b':str(cT[2]),'a':str(cT[3])}
        child = ET.SubElement(parent,index,coldic)
    return True

    