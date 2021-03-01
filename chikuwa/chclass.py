import wx
import uuid

import chconst
RADIUS = chconst.RADIUS

class infoContainer(object):
    def __init__(
        self,
        sex=True,
        age=0,
        ageUnit=0,
        statType=0,
        affType=0,
        isMarked=True,
        isAdopted=False,
        #isDocumentedEval = False, # add*
        #examList=[],
        diseaseList=[]
        
    ):
        self.sex = sex #true= f false = m ig
        self.age = age
        self.ageUnit = ageUnit # 0=y,1=mo ig
        self.statType = statType  #0= alive 1=deceased
        self.affType = affType #0=none 1=affected 2=carrier 3=asymptomatic carrier
        self.isMarked = isMarked
        self.isAdopted = isAdopted
        #self.isDocumentedEval = isDocumentedEval # add*
        #self.examList = examList #list in list [type -> p=0 or n=1 or u=2, testname]
        self.diseaseList = diseaseList #list in list [yr,disease name]
        
    def updateByList(self,plist):
        self.sex = bool(plist[0])
        self.age = plist[1]
        self.ageUnit = plist[2]
        self.statType = plist[3]
        self.affType = plist[4]
        self.isMarked = bool(plist[5])
        self.isAdopted = bool(plist[6])
        self.diseaseList = plist[7]
        
class infoBabyContainer(object):
    def __init__(
        self,
        sex = True,
        age = 0,
        statType = 0,
        footer = 0,
        affType = 1
    ):
        self.sex = sex
        self.age = age
        self.footer = footer
        self.statType = statType #0=sab 1=top 2=ect 3=sb 4=p
        self.affType = affType #0=none 1=affected
        
    def updateByList(self,plist):
        self.sex = bool(plist[0])
        self.age = plist[1]
        self.statType = plist[2]
        self.affType = plist[3]
        self.footer = plist[4]

class CoreIndividual(object):
    def __init__(self):
        self.pos = (20,20) #absolute
        self.rad = RADIUS
        self.margin = 5
        self.width = self.rad*2 + self.margin
        self.height = self.rad*2 + self.margin
        self.isSelected = False
        self.bmp = self.CreateBmp()
        self.mdc = self.CreateShape()
        self.visible = True
        self.textSize = int(self.rad)
        self.uuid = str(uuid.uuid4())
    
    def CreateBmp(self):
        bmp = wx.Bitmap(self.width,self.height)
        return bmp
        
    def HitTest(self,pt): #absolute
        rect = self.GetRect()
        return rect.Contains(pt)
    
    def GetRect(self): #absolute
        rect = wx.Rect(self.pos[0],self.pos[1],self.width,self.height)
        #print(self.bmp.GetWidth())
        return rect
    
    def GetCenterPoint(self):
        cpnt = wx.Point(self.pos[0]+self.rad,self.pos[1]+self.rad)
        return cpnt
    
    def CreateShape(self): #relative
        mdc = wx.MemoryDC()
        bgcolour = wx.Colour(255,255,255)
        mdc.SelectObject(self.bmp)
        mdc.SetBackground(wx.Brush(bgcolour,wx.BRUSHSTYLE_SOLID))
        mdc.Clear()
        return mdc
    
    def returnTextPos(self):
        tposx = self.pos[0]-5
        tposy = self.pos[1]+self.height+5
        return (tposx,tposy)

class Person(CoreIndividual):
    def __init__(self):
        CoreIndividual.__init__(self)
        self.info = infoContainer()
        self.adopFlag = False
    
    def update(self,info):
        self.info = info
        return True
    
    def getFooter(self):
        footer = ""
        if self.info.ageUnit == 0:
            footer  += "{}y. \r\n".format(self.info.age)
        elif self.info.ageUnit == 1:
            footer  += "{}mo. \r\n".format(self.info.age)
        
        if len(self.info.diseaseList) > 0:
            for time,disease in self.info.diseaseList:
                unit = ""
                if self.info.ageUnit == 0:unit = "y."
                if self.info.ageUnit == 1:unit = "mo. "
                footer += "{}{}   {}\r\n".format(time,unit,disease)
            
        return footer
    
    def Draw(self,dc,op=wx.COPY):
        color = ""
        if self.isSelected:
            self.mdc.Clear()
            color = "red"
        else:
            self.mdc.Clear()
            color = "black"
    
        self.mdc.SetPen(wx.Pen(color,2))
        self.mdc.SetBrush(wx.Brush(color,style=wx.BRUSHSTYLE_TRANSPARENT))

        
        if self.info.affType == 1:
            self.mdc.SetBrush(wx.Brush(color,style=wx.BRUSHSTYLE_SOLID))

        if not self.info.sex:
            self.mdc.DrawRectangle(int(self.margin/2),int(self.margin/2),self.rad*2,self.rad*2)
        else:
            self.mdc.DrawCircle(int(self.width/2),int(self.height/2),self.rad)

        if self.info.affType == 2:
            self.mdc.SetBrush(wx.Brush(color,style=wx.BRUSHSTYLE_SOLID))
            self.mdc.DrawCircle(int(self.width/2),int(self.height/2),2)
        elif self.info.affType == 3:
            self.mdc.DrawLine(int(self.width/2),0,int(self.width/2),self.height)
            
        if self.info.statType == 1:            
            self.mdc.DrawLine(0,self.height,self.width,0)
        dc.Blit(self.pos[0],self.pos[1],self.width,self.height,self.mdc,0,0,op,True)

class PreNotCT(CoreIndividual):
    def __init__(self):
        CoreIndividual.__init__(self)
        self.info = infoBabyContainer()
        self.adopFlag = False
    
    def update(self,info):
        self.info = info
        return True
        
    def returnTextPos(self):#override
        tposx = self.pos[0]-5
        if self.info.statType < 3:tposy = self.pos[1]+int(self.height*2/3)
        else:tposy = self.pos[1]+self.height+5
        return (tposx,tposy)
    
    def getFooter(self):
        footer = ""
        if self.info.statType < 2:
            footer += "{}wks \r\n".format(self.info.age)
            footer += "{}".format(self.info.footer)
        elif self.info.statType == 2:
            footer += "ECT"
        elif self.info.statType == 3:
            footer += "SB \r\n"
            footer += "{}wks \r\n".format(self.info.age)
        elif self.info.statType == 4:
            footer += "{}wks \r\n".format(self.info.age)
            footer += "{}".format(self.info.footer)
            
        return footer
    def Draw(self,dc,op=wx.COPY):
        color = ""
        if self.isSelected:
            self.mdc.Clear()
            color = "red"
        else:
            self.mdc.Clear()
            color = "black"
    
        self.mdc.SetPen(wx.Pen(color,2))
        self.mdc.SetBrush(wx.Brush(color,style=wx.BRUSHSTYLE_TRANSPARENT))
        
        if self.info.affType == 1 and self.info.statType != 2:
            self.mdc.SetBrush(wx.Brush(color))
        
        if self.info.statType == 0:
            points = [(self.rad,0),(0,self.rad),(self.rad*2,self.rad)]
            self.mdc.DrawPolygon(points)            
        elif 0 < self.info.statType < 3:
            points = [(self.rad,0),(0,self.rad),(self.rad*2,self.rad)]
            self.mdc.DrawPolygon(points)
            self.mdc.DrawLine(0,int(self.height*2/3),int(self.width*2/3),0)        
        elif self.info.statType == 3:
            if not self.info.sex:
                self.mdc.DrawRectangle(int(self.margin/2),int(self.margin/2),self.rad*2,self.rad*2)
            else:
                self.mdc.DrawCircle(int(self.width/2),int(self.height/2),self.rad)
            self.mdc.DrawLine(0,self.height,self.width,0)
        elif self.info.statType == 4:
            if not self.info.sex:
                self.mdc.DrawRectangle(int(self.margin/2),int(self.margin/2),self.rad*2,self.rad*2)
            else:
                self.mdc.DrawCircle(int(self.width/2),int(self.height/2),self.rad)
            if self.info.affType == 0:
                self.mdc.SetTextForeground('black')
            elif self.info.affType == 1:
                self.mdc.SetTextForeground('white')
            font = wx.Font(self.textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            self.mdc.SetFont(font)
            self.mdc.DrawText("P",int(self.width/3),int(self.height/4))
            
        dc.Blit(self.pos[0],self.pos[1],self.width,self.height,self.mdc,0,0,op,True)
    
class MultiBirth():
    def __init__(self):
        self.member = []
        self.isMonozygotic = False
    
    def isContained(self,person):
        if person in self.member:
            return True
        else:
            return False
    
    def add(self,person):
        if not self.isContained(person):
            self.member.append(person)
            return True
        else:
            return False
    
    def delete(self,person):
        if self.isContained(person):
            self.member.remove(person)
            return True
        else:
            return False
    
    def length(self):
        return len(self.member)

class familyGroup():
    def __init__(self):
        self.member = []
        self.isParent = True
        self.isDivorced = False
        self.MultiBirthList = []
        self.offsetYPercent = 0
        self.offsetXPercent = 0
        self.markOffsetXPercent = 0
        self.uuid = str(uuid.uuid4())
        
        
    def convertFromList(self,plist):
        f = filter(lambda p: type(p) is not Person or not PreNotCT,plist)
        if len(list(f)) > 0:
            return False
        else:
            self.member = plist
            return True
    
    def isContainedMultiAll(self,person):
        for mlt in self.MultiBirthList:
            res = mlt.isContained(person)
            if res == True : return True
        return False
    
    def searchMultiByPerson(self,person): #return index!
        index = -1
        for mlt in self.MultiBirthList:
            index += 1
            res = mlt.isContained(person)
            if res == True : return index
        return None
        
    def append(self,person):
        if type(person) is Person or PreNotCT:
            self.member.append(person)
            return True
        else:
            return False
    
    def delete(self,person):
        if type(person) is Person or PreNotCT:
            index = self.searchMultiByPerson(person)
            if index is not None:
                self.MultiBirthList[index].delete(person)
                if self.MultiBirthList[index].length() < 2:
                    del self.MultiBirthList[index]
            self.member.remove(person)
            return True
        else:
            return False
    def deleteMultiByIndex(self,index):
        del self.MultiBirthList[index]
        return True
        
    def length(self):
        return len(self.member)
        
    def getXlist(self):
        fx = lambda p:p.pos[0]
        xlist = list(map(fx,self.member))
        return xlist
        
    def getYlist(self):
        fy = lambda p:p.pos[1]
        ylist = list(map(fy,self.member))
        return ylist
        
    def GetRect(self):
        xlist = self.getXlist()
        ylist = self.getYlist()
        x = min(xlist)
        y = min(ylist)
        width = max(xlist) - x + RADIUS*2
        height = max(ylist) - y + RADIUS*2
        rect = wx.Rect(x,y,width,height)
        return rect
    
    def HitTest(self,pt):
        rect = self.GetRect()
        return rect.Contains(pt)
    
    def getCenterPos(self):
        xlist = self.getXlist()
        ylist = self.getYlist()
        x = min(xlist)
        y = min(ylist)
        width = max(xlist) - x + RADIUS*2
        height = max(ylist) - y + RADIUS*2
        posx = int(x+width/2)
        posy = int(y+height/2)
        return (posx,posy)
    
    def getCenterMultiPos(self):
        result = []
        for multibirth in self.MultiBirthList:
            member = multibirth.member
            fg = familyGroup()
            fg.convertFromList(member)
            result.append(fg.getCenterPos())
        return result
    
    def returnIDself(self):
        return id(self)
    
    def isContained(self,person):
        if person in self.member:
            return True
        else:
            return False
    
    def isEmpty(self):
        if len(self.member) > 0:
            return False
        else:
            return True
    
    def setYpos(self,y):
        for person in self.member:
            person.pos = (person.pos[0],y)
        return True
    
    def isYSame(self):
        ylist = []
        for person in self.member:
            ylist.append(person.pos[1])
        #print("isYSame ylist {}".format(ylist))
        if max(ylist) == min(ylist):
            return True
        else:
            return False
        
    def addPersonToMulti(self,addPerson,toPerson):
        if self.isContained(addPerson) and not self.isContainedMultiAll(addPerson):
            index = self.searchMultiByPerson(toPerson)
            if index is None:
                self.createNewMulti([addPerson,toPerson])
            else:
                self.MultiBirthList[index].add(addPerson)
                return True
            
    def createNewMulti(self,personList):
        for person in personList:
            if self.isContained(person) and self.isContainedMultiAll(person):
                return False
        multibirth = MultiBirth()
        multibirth.member = personList
        self.MultiBirthList.append(multibirth)
        return True
    
    def searchByUUID(self,uuid):
        for person in member:
            if person.uuid == uuid:
                return person
            

class fgGroup:
    def __init__(self):
        self.member = []
        self.uuid = str(uuid.uuid4())
        
    def convertFromList(self,plist):
        f = filter(lambda p: type(p) is not familyGroup,plist)
        if len(list(f)) > 0:
            return False
        else:
            self.member = plist
            return True
        
    def convertFromDict(self,pdict):
        l = [pdict["relation"],pdict["sibling"]]
        f = filter(lambda p: type(p) is not familyGroup,l)
        if len(list(f)) > 0:
            return False
        else:
            self.member = l
            return True       
        
    def length(self):
        return len(self.member)
    
    def isContained(self,group):
        if group in self.member:
            return True
        else:
            return False
                
    def getXYlist(self):
        xlist = []
        ylist = []
        for group in self.member:
            xlist.extend(group.getXlist())
            ylist.extend(group.getYlist())
        return xlist,ylist
        
    def GetRect(self):
        xlist,ylist = self.getXYlist()
        x = min(xlist)
        y = min(ylist)
        width = max(xlist) - x + RADIUS*2
        height = max(ylist) - y + RADIUS*2
        rect = wx.Rect(x,y,width,height)
        return rect
    
    def HitTest(self,pt):
        rect = self.GetRect()
        return rect.Contains(pt)
    
    
    def returnIDself(self):
        return id(self)
    
    def searchByUUID(self,uuid):
        for fg in self.member:
            if fg.uuid == uuid:
                return fg

    
class siblingArguments:
    def __init__(self):
        self.SiblingList = []
    
    def searchSib(self,group): #type(group) -> familyGroup
        sg = set(group.member)
        res = None
        index = -1
        for g in self.SiblingList:
            index += 1
            if set(g.member) == sg: # found the same group in siblinglist
                res = index
        return res
    
    def searchMultipleSib(self,group):
        sg = set(group.member)
        res = False
        for g in self.SiblingList:
            if set(g.member) & sg: #found the same child in siblinglist
                res = True
        return res
    
    def searchSibByPerson(self,person):
        res = None
        index = -1
        for g in self.SiblingList:
            index += 1
            if g.isContained(person):
                res = index
        return res
    
    def searchSibAllByPerson(self,person):
        res = []
        index = -1
        for p in self.SiblingList:
            index += 1
            #print(p.isContained(person))
            if p.isContained(person):
                res.append(index)
        if len(res) == 0:
            return None
        return res
    
    def addSib(self,group):
        flag = self.searchMultipleSib(group)
        if flag == False:
            self.SiblingList.append(group)
            return True
        else:
            return False
    
    def deleteSib(self,group):
        index = self.searchSib(group)
        if index is None:
            return False
        else:
            del self.SiblingList[index]
            return True
        
    def addPersonFromSibIndex(self,person,index):
        sibling = self.SiblingList[index]
        flag = self.searchSibByPerson(person)
        if flag is None:
            result = sibling.append(person)
            return result
        else:
            return False
    
    def deletePersonFromSibIndex(self,person,index):
        sibling = self.SiblingList[index]
        if sibling.length() < 2:
            del self.SiblingList[index]
            return True
        else:
            result = sibling.delete(person)
            return result
    
    def deleteSibByIndex(self,index):
        del self.SiblingList[index]
        return True
    
    def isEmptySibByIndex(self,index):
        result = self.SiblingList[index].length() < 1
        return result
    
    def alignSibAll(self):
        for g in self.SiblingList:
            aveY = 0
            diffYs = []
            maxY = 0
            for p in g.member:
                aveY += p.pos[1]
                #print(len(s))
            aveY = int(aveY/len(g.member))
            for p in g.member:
                diffYs.append(p.pos[1] - aveY)
            maxY = max(diffYs,key=abs)+aveY
                
            for p in g.member:
                x = p.pos[0]
                ptt = (x,maxY)
                p.pos = ptt
        return True
    
    def alignSibByIndex(self,index,pos):
        y = pos[1]
        for i in index:
            fg = self.SiblingList[i]
            fg.setYpos(y)
        return True

    def diffYPosAllSib(self):
        res = []
        index = -1
        for fg in self.SiblingList:
            index += 1
            if not fg.isYSame():
                res.append(index)
        if len(res) == 0:
            return None
        else:
            return res
    
    def length(self):
        return len(self.SiblingList)

class relationArguments:
    def __init__(self):
        self.PairList = []
        
    def searchPair(self,pair): #type(pair) = familyGroup
        sp = set(pair.member)
        res = None
        index = -1
        for p in self.PairList:
            index += 1
            if set(p.member) == sp: #found a pair in pairlist
                res = index
        return res
    
    def searchPairByPerson(self,person):
        res = None
        index = -1
        for p in self.PairList:
            index += 1
            #print(p.isContained(person))
            if p.isContained(person):
                res = index
        return res
    
    def searchPairAllByPerson(self,person):
        res = []
        index = -1
        for p in self.PairList:
            index += 1
            #print(p.isContained(person))
            if p.isContained(person):
                res.append(index)
        if len(res) == 0:
            return None
        return res
    
    def addPair(self,pair):
        index = self.searchPair(pair)
        #print("aaaaaaa")
        if index is None:
            #print("aaa")
            self.PairList.append(pair)
            return True
        else:
            return False
    
    def deletePair(self,pair):
        index = self.searchPair(pair)
        if index is None:
            return False
        else:
            del self.PairList[index]
            return True
        
    def deletePersonFromPairIndex(self,person,index):
        pair = self.PairList[index]
        result = pair.delete(person)
        return result

    def deletePairByIndex(self,index):
        del self.PairList[index]
        return True
    
    def isEmptyPairByIndex(self,index):
        res = self.PairList[index].length() < 2
        return res
    
    def alignPairAll(self):
        for g in self.PairList:
            maxY = 0
            aveY = 0
            diffYs = []
            for p in g.member:
                aveY += p.pos[1]
            aveY = int(aveY/2)     
            maxY = aveY
            for p in g.member:
                x = p.pos[0]
                ptt = (x,maxY)
                p.pos = ptt
        return True
    
    def alignPairByIndex(self,indexList,pos):
        y = pos[1]
        for i in indexList:
            fg = self.PairList[i]
            fg.setYpos(y)
        return True
    
    def diffYPosAllPair(self):
        res = []
        index = -1
        for fg in self.PairList:
            index += 1
            if not fg.isYSame():
                res.append(index)
        if len(res) == 0:
            return None
        else:
            return res
    
    def length(self):
        return len(self.PairList)

class parentChildRelationArgument:
    def __init__(self):
        self.pcRelationList = []
    
    def search(self,group): #type(group) -> fgGroup
        sg = set(group.member)
        res = None
        index = -1
        for g in self.pcRelationList:
            index += 1
            if set(g.member) == sg: # found the same group in pcrl
                res = index
        return res
    
    def add(self,group):
        flag = self.search(group)
        if flag is None:
            self.pcRelationList.append(group)
            return True
        else:
            return False
    
    def delete(self,group):
        index = self.search(group)
        if index is None:
            return False
        else:
            del self.pcRelationList[index]
            return True
    
    def searchPCRLBySingularGroup(self,familyGroup):
        index = -1
        result = None
        for fgGrp in self.pcRelationList:
            index += 1
            if fgGrp.isContained(familyGroup):
                result = index
        return result
    
    def deleteByIndex(self,index):
        del self.pcRelationList[index]
        return True
    
    def length(self):
        return len(self.pcRelationList)

class lineShape:
    def __init__(self,spt,ept):
        self.spt = spt
        self.ept = ept
        self.height = self.getHeight()
        self.width = self.getWidth()
        self.opt = self.getOpt()
        self.penStyle = wx.PENSTYLE_SOLID
        self.thickness = 1
    
    def getLines(self):
        return (self.spt[0],self.spt[1],self.ept[1],self.ept[2])
    
    def getHeight(self):
        return abs(self.spt[1]-self.ept[1])
    
    def getWidth(self):
        return abs(self.spt[0]-self.ept[0])
    
    def getOpt(self):
        xl = (self.spt[0],self.ept[0])
        yl = (self.spt[1],self.ept[1])
        opt = (min(xl),min(yl))
        return opt

    def HitTest(self,pt): #absolute
        rect = self.GetRect()
        return rect.Contains(pt)
    
    def GetRect(self): #absolute
        rect = wx.Rect(self.opt[0],self.opt[1],self.width,self.height)
        return rect
    
    
class textBox:
    def __init__(self):
        self.text = "テキスト"
        self.textSize = 10
        self.font = wx.Font(self.textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.width = None
        self.height = None
        self.bmp = None
        self.mdc = None
        self.pos = (10,10)
        self.visible = True
        self.isOutlineVisible = True
        self.outlineColor = wx.Colour(0,0,0,255)
        self.textColor = wx.Colour(0,0,0,255)
        self.bgColor = wx.Colour(255,255,255,255)
        self.uuid = uuid.uuid4()
    
    def CreateBmp(self):
        bmp = wx.Bitmap(self.width,self.height)
        return bmp
        
    def HitTest(self,pt): #absolute
        rect = self.GetRect()
        return rect.Contains(pt)
    
    def GetRect(self): #absolute
        rect = wx.Rect(self.pos[0],self.pos[1],self.width,self.height)
        return rect
    
    def GetCenterPoint(self):
        cpnt = wx.Point(self.pos[0]+int(self.width/2),self.pos[1]+int(self.height/2))
        return cpnt
    
    def appendTextSize(self,size):
        self.textSize = size
        self.font.SetFractionalPointSize(size)
        return True
    
    def appendColor(self,OLcol,TXcol,BGcol):
        self.outlineColor = OLcol
        self.textColor = TXcol
        self.bgColor = BGcol
        return True

    def CreateShape(self): #relative
        mdc = wx.MemoryDC()
        mdc.SelectObject(self.bmp)
        brush = wx.Brush(self.bgColor,wx.BRUSHSTYLE_SOLID)
        mdc.SetBackground(brush)
        mdc.Clear()
        if self.isOutlineVisible:
            mdc.SetPen(wx.Pen(self.outlineColor,2))
        else:
            mdc.SetPen(wx.Pen(self.outlineColor,style=wx.PENSTYLE_TRANSPARENT))
        mdc.SetBrush(brush)
        mdc.DrawRectangle(0,0,self.width,self.height)
        mdc.SetFont(self.font)
        mdc.SetTextForeground(self.textColor)
        mdc.DrawText(self.text,0,0)
        return mdc
    
    def Draw(self,dc,op=wx.COPY):
        dc.SetFont(self.font)
        ext = dc.GetFullMultiLineTextExtent(self.text,self.font)
        self.width = ext[0]
        self.height = ext[1]+10
        self.bmp = self.CreateBmp()
        self.mdc = self.CreateShape()
        dc.Blit(self.pos[0],self.pos[1],self.width,self.height,self.mdc,0,0,op,True)
        
class MimeType():
    def __init__(self):
        self.mimetype = None
        self.mimelist = [
            ["JPEG (*.jpeg)","*.jpeg",wx.BITMAP_TYPE_JPEG],
            ["PNG (*.png)","*.png",wx.BITMAP_TYPE_PNG],
            ["GIF(*.gif)","*.gif",wx.BITMAP_TYPE_GIF]
        ]
    def getWildcard(self):
        wildcard = ""
        for desc,ext,wxmime in self.mimelist:
            wildcard += desc + "|" + ext + "|"
        wildcard = wildcard[:len(wildcard)-1]
        return wildcard
    def getWxMethod(self,index):
        wxmime = self.mimelist[index][2]
        return wxmime

