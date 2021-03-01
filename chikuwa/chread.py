import xml.etree.ElementTree as ET
import wx
import os
import zipfile

import chclass

#ET.dump(tree)
def adjustValue(value):
    if value == 'True':
        return True
    elif value == 'False':
        return False
    else:
        return int(value)

def formPerson(root):
    person_list = {}
    for person_data in root.findall('person'):
        dlist = []
        if 'Person' in person_data.attrib['type']:
            person = chclass.Person()
            person.uuid = person_data.attrib['uuid'] #uuid
            
            person_info = person_data.find('info')
            info = chclass.infoContainer()
            #p = [info.sex,info.age,info.ageUnit,info.statType,info.affType,info.isMarked,info.isAdopted]
            p = []
            for index in range(7):
                text = person_info[index].text
                p.append(adjustValue(text))
            p.append([])
            for disease in person_info[7]:
                dlist = [int(disease.attrib['yr']),disease.attrib['di']]
                p[7].append(dlist)
                
            info.updateByList(p)
            
            person_pos = person_data.find('pos')
            pos = (int(person_pos.attrib['x']),int(person_pos.attrib['y']))
            person.pos = pos
            
            person_adopFlag = person_data.find('adopFlag').text
            person.adopFlag = int(person_adopFlag)
            person.update(info)
            person_list.update({person.uuid:person})
            
        elif 'PreNotCT' in person_data.attrib['type']:
            person = chclass.PreNotCT()
            person.uuid = person_data.attrib['uuid'] #uuid
            
            person_info = person_data.find('info')
            info = chclass.infoBabyContainer()
            #p = [info.sex,info.age,info.statType,info.affType,info.footer]
            p = []
            for index in range(4):
                text = person_info[index].text
                p.append(adjustValue(text))
            if person_info.find('footer').text is not None:
                p.append(person_info.find('footer').text)
            else:
                p.append("")
            person_pos = person_data.find('pos')
            pos = (int(person_pos.attrib['x']),int(person_pos.attrib['y']))
            person.pos = pos
            
            info.updateByList(p)
            person.update(info)
            
            person_list.update({person.uuid:person})
        else:
            return False
    return person_list
        
def formGroup(root,plist):
    group_list = {}
    for group_data in root.findall('FamilyGroup'):
        fg = chclass.familyGroup()
        fg.uuid = group_data.attrib['uuid']
        #p = [ fg.isParent,fg.isDivorced,fg.offsetYPercent,fg.offsetXPercent,fg.markOffsetXPercent]
        #for index in range(5):
            #p[index] = group_data[index].text
        fg.isParent = adjustValue(group_data[0].text)
        fg.isDivorced = adjustValue(group_data[1].text)
        fg.offsetYPercent = float(group_data[2].text)
        fg.offsetXPercent = float(group_data[3].text)
        fg.markOffsetXPercent = float(group_data[4].text)
        
        member_data = group_data.find('member')
        for member in member_data:
            uuid = member.attrib['id']
            fg.member.append(plist[uuid])
        group_list.update({fg.uuid:fg})
        multi_data = group_data.findall('multi')
        if len(multi_data) > 0:
            for multi in multi_data:
                multibirth = chclass.MultiBirth()
                for person in multi.findall('person'):
                    uuid = person.attrib['id']
                    multibirth.member.append(plist[uuid])
                isMonozygotic = multi.find('isMonozygotic')
                multibirth.isMonozygotic = bool(isMonozygotic.attrib['value'])
                fg.MultiBirthList.append(multibirth)
            
    return group_list

def formFGGroup(root,rel_list,sib_list):
    fgg_list = {}
    for fgg_data in root.findall('FGGroup'):
        fgg = chclass.fgGroup()
        fgg.uuid = fgg_data.attrib['uuid']
        par = fgg_data.findall('member')[0]
        chi = fgg_data.findall('member')[1]
        pard = rel_list[par.attrib['uuid']]
        chid = sib_list[chi.attrib['uuid']]
        fgg.member = [pard,chid]
        fgg_list.update({fgg.uuid:fgg})
    return fgg_list

def readChkw(cv,path):
    xmlnames = ['shapes.xml','objs.xml','lines.xml','info.xml']
    with zipfile.ZipFile(path,'r') as zf:
        with zf.open(os.path.join('data',xmlnames[0])) as xml:
            openShapes(cv,xml.read())
        with zf.open(os.path.join('data',xmlnames[1])) as xml:
            openObjs(cv,xml.read())
            
    cv.Refresh(eraseBackground=False)
    return True

def openShapes(cv,data):
    #tree = ET.parse(path)
    #properties = tree.getroot()
    properties = ET.fromstring(data)
    person_list = formPerson(properties[0])
    shapes = [i for i in person_list.values()]
    rel_list = formGroup(properties[1],person_list)
    rel_member = [i for i in rel_list.values()]
    sib_list = formGroup(properties[2],person_list)
    sib_member = [i for i in sib_list.values()]
    fgg_list = formFGGroup(properties[3],rel_list,sib_list)
    fgg_member = [i for i in fgg_list.values()]
    
    cv.shapes = shapes
    cv.shapeRelation.PairList = rel_member
    cv.shapeSiblings.SiblingList = sib_member
    cv.shapePCRL.pcRelationList = fgg_member
    
    return True

def openObjs(cv,data):
    #tree = ET.parse(path)
    #properties = tree.getroot()
    properties = ET.fromstring(data)
    obj_list = formObjs(properties)
    obj_member = [i for i in obj_list.values()]
    cv.objs = obj_member
    
    return True

def formObjs(properties):
    obj_list = {}
    for obj_data in properties.findall('objs'):
        obj = chclass.textBox()
        obj.uuid = obj_data.attrib['uuid']
        obj.text = obj_data.find('text').text
        obj.appendTextSize(float(obj_data.find('textSize').text))
        obj.visible = adjustValue(obj_data.find('visible').text)
        obj.isOutlineVisible = adjustValue(obj_data.find('isOutlineVisible').text)
        
        outlineColor = obj_data.find('outlineColor').attrib
        textColor = obj_data.find('textColor').attrib
        bgColor = obj_data.find('bgColor').attrib
        obj.appendColor(wxColornize(outlineColor),wxColornize(textColor),wxColornize(bgColor))
        
        obj_pos = obj_data.find('pos').attrib
        pos = (int(obj_pos['x']),int(obj_pos['y']))
        obj.pos = pos
        obj_list.update({obj.uuid:obj})
    return obj_list
        
def wxColornize(cdict):
    ct = translateColIntoTuple(cdict)
    return wx.Colour(ct[0],ct[1],ct[2],ct[3])
        
def translateColIntoTuple(cdict):
    clist = []
    for val in cdict.values():
        clist.append(int(val))
    return tuple(clist)
            
        
if __name__ == "__main__":
    pass
    
