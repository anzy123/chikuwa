import wx
import wx.lib.scrolledpanel as scrolled
import chikuwa

MAX_HEIGHT = 800
MAX_WIDTH = 900
LENGTH_CHILD_LINE = 50
RADIUS = chikuwa.RADIUS
TEXT_SIZE = chikuwa.TEXT_SIZE
MARK_IMAGE_PATH = "./src/mark.png"
DIVORCE_IMAGE_PATH = "./src/divorce.png"

def crossPointGivenY(pt1,pt2,cpt,y):
    def giveRx(px,py,qx,qy,y):
        q = (y-py)/(qy-py)
        rX = (1-q)*px+q*qx
        return int(rX)
    r1x = giveRx(pt1[0],pt1[1],cpt[0],cpt[1],y)
    r2x = giveRx(pt2[0],pt2[1],cpt[0],cpt[1],y)
    r1 = (r1x,y)
    r2 = (r2x,y)
    return r1,r2

class testCanvas(wx.ScrolledCanvas):
   # binder = wx_utils.bind_manager()
    
    def __init__(self,parent,ID):
        wx.ScrolledCanvas.__init__(self,parent,ID)
        
        self.maxWidth = MAX_WIDTH
        self.maxHeight = MAX_HEIGHT
        self.textSize = TEXT_SIZE
        
 
        #self.binder.bindall(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_RIGHT_DOWN,self.OnRightDown)
        self.Bind(wx.EVT_RIGHT_UP,self.OnRightUp)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        #self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.SetBackgroundColour("white")
        
        #initialize buffer or sth
        self.buffer = wx.Bitmap(self.maxWidth,self.maxHeight)
        self.initBackground(self.buffer)

        self.shapes = []
        self.objs = []
        self.lines = []
        
        self.dragObj = None
        #sth to do with drag motion
        self.dragShape = None

        self.dragStartPos = None
        self.hiliteShape = None
        
        self.keyPressed = False
        self.whatKey = False
        
        self.selectedShapes = []
        self.selectedGroups = {
            "relation": None ,
            "sibling" : None
        }
        
        self.mousePositionForPopup = wx.Point()
        self.mousePosAbsolute = wx.Point()
        self.selectedShapeForPopup = None
        self.selectedSibForPopup = None
        self.selectedRelForPopup = None
        self.selectedObjForPopup = None
        self.selectedSibIndexForPopup = 0
        self.selectedRelIndexForPopup = 0
        
        self.shapeRelation = chikuwa.relationArguments()
        self.shapeSiblings = chikuwa.siblingArguments()
        self.shapePCRL = chikuwa.parentChildRelationArgument()
        
        self.isArrowShow = False
        self.isGenerationVisible = False
        
        self.statMode = None
        
        self.markBitmap = wx.Bitmap(MARK_IMAGE_PATH)
        self.divorceBitmap = wx.Bitmap(DIVORCE_IMAGE_PATH)
        #keyMap
        self.keyMap = {
            wx.WXK_SHIFT : "shift",
            wx.WXK_TAB : "tab",
            wx.WXK_UP : "up",
            wx.WXK_DOWN : "down",
            wx.WXK_LEFT : "left",
            wx.WXK_RIGHT : "right"
        }
        ###
        
        self.LineAppendFlag = False
        self.LineAppendSpt = 0
        
    def initBackground(self,buffer):
        dc = wx.MemoryDC()
        dc.SelectObject(self.buffer)
        dc.Clear()
    
    def DrawShapes(self,dc):
        for shape in self.shapes:
            if type(shape) is chikuwa.Person:
                if shape.visible:
                    shape.Draw(dc)
                    tpos = shape.returnTextPos()
                    dc.SetTextForeground('black')
                    font = wx.Font(self.textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                    dc.SetFont(font)
                    if shape.info.isMarked:
                        dc.DrawBitmap(self.markBitmap,tpos[0]-5,tpos[1]-self.textSize*2)
                    if shape.info.isAdopted:
                        halfrad = int(shape.rad/4) #nothalf haha
                        modh = shape.height+halfrad
                        wid = shape.width
                        modw = wid+halfrad
                        pos = shape.pos
                        shlines = (
                            (pos[0],pos[1]-halfrad,pos[0]-halfrad,pos[1]-halfrad),
                            (pos[0]-halfrad,pos[1]-halfrad,pos[0]-halfrad,pos[1]+modh),
                            (pos[0]-halfrad,pos[1]+modh,pos[0],pos[1]+modh),
                            (pos[0]+wid,pos[1]-halfrad,pos[0]+modw,pos[1]-halfrad),
                            (pos[0]+modw,pos[1]-halfrad,pos[0]+modw,pos[1]+modh),
                            (pos[0]+modw,pos[1]+modh,pos[0]+wid,pos[1]+modh)
                        )
                        dc.DrawLineList(shlines)
                    dc.DrawText(shape.getFooter(),tpos[0],tpos[1])
            elif type(shape) is chikuwa.PreNotCT:
                if shape.visible:
                    shape.Draw(dc)
                    tpos = shape.returnTextPos()
                    dc.SetTextForeground('black')
                    font = wx.Font(self.textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                    dc.SetFont(font)
                    dc.DrawText(shape.getFooter(),tpos[0],tpos[1])
                else:
                    pass
            else:
                pass
                
    def DrawArrow(self,dc,mode=0):
        mousePosAbs = self.mousePosAbsolute
        if mode == 0:
            spt = self.mousePositionForPopup
        else:
            spt = self.LineAppendSpt
        curPosAbs = wx.GetMousePosition()
        diffPos = (curPosAbs[0]-mousePosAbs[0],curPosAbs[1]-mousePosAbs[1])
        ept = (spt[0]+diffPos[0],spt[1]+diffPos[1])
        dc.SetPen(wx.Pen('pink',2,wx.PENSTYLE_DOT_DASH))
        dc.DrawLine(spt,ept)
        return True
        
    def DrawLineObjs(self,dc):
        for lineObj in self.lines:
            dc.SetPen(wx.Pen('black',lineObj.thickness,lineObj.penStyle))
            dc.DrawLine(lineObj.spt,lineObj.ept)
            
    def FindLineObj(self,pt):
        for lineObj in self.lines:
            if lineObj.HitTest(pt):
                return lineObj
        return None
        
    def DrawObjs(self,dc):
        for obj in self.objs:
            obj.Draw(dc)
        return True
    
    def FindObj(self,pt):
        for obj in self.objs:
            if obj.HitTest(pt):
                return obj
        return None
        
    def FindShape(self,pt):
        for shape in self.shapes:
            if shape.HitTest(pt):
                return shape
        return None
    
    def FindRelation(self,pt):
        if self.shapeRelation.length() > 0:
            for group in self.shapeRelation.PairList:
                if group.HitTest(pt):
                    return group
        return None
    
    def FindSibling(self,pt):
        if self.shapeSiblings.length() > 0:
            for group in self.shapeSiblings.SiblingList:
                if group.HitTest(pt):
                    return group
        return None
    
    def lineModifier(self,flag):
        if len(self.selectedShapes) < 2:
            return False
        elif len(self.selectedShapes) == 2:
            group = chikuwa.familyGroup()
            r = group.convertFromList(self.selectedShapes)
            if r:
                if flag:
                    self.shapeRelation.addPair(group)
                    return True
                elif not flag:
                    self.shapeRelation.deletePair(group)
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
                
    def sibModifier(self,flag):
        if len(self.selectedShapes) < 2:
            return False
        else:
            group = chikuwa.familyGroup()
            r = group.convertFromList(self.selectedShapes)
            if r:
                if flag:
                    self.shapeSiblings.addSib(group)
                    return True
                elif not flag:
                    self.shapeSiblings.deleteSib(group)
                    return True
                else:
                    return False
            else:
                return False
            
    def pcrlModifier(self,flag):
        if self.selectedGroups["relation"] is None or self.selectedGroups["sibling"] is None:
            return False
        else:
            group = chikuwa.fgGroup()
            r = group.convertFromDict(self.selectedGroups)
            if r:
                if flag:
                    self.shapePCRL.add(group)
                    return True
                elif not flag:
                    self.shapePCRL.delete(group)
                    return True
                else:
                    return False
            else:
                return False
    def OnLeftDown(self,event):
        if self.statMode == "createLine":
            self.appendLineObj(event)
        else:
            self.NormalOnLeftDown(event)
    
    def appendLineObj(self,event):
        pos = event.GetPosition()
        if not self.LineAppendFlag:
            self.LineAppendSpt = pos
            self.LineAppendFlag = True
            self.mousePosAbsolute = wx.GetMousePosition()
        else:
            lineObj = chikuwa.lineShape(self.LineAppendSpt,pos)
            self.LineAppendFlag = False
            self.LineAppendSpt = 0
            self.lines.append(lineObj)
            self.mousePosAbsolute = wx.Point()
            self.statMode = None
        return True
    
    def NormalOnLeftDown(self,event):
        pos = event.GetPosition()
        shape = self.FindShape(pos)
        relation = self.FindRelation(pos)
        sibling = self.FindSibling(pos)
        obj = self.FindObj(pos)
        flag = True
        if shape:
            shape.isSelected = True
            if self.keyPressed == False:
                if self.isArrowShow:
                    if self.statMode == "createPair":
                        group = chikuwa.familyGroup()
                        if type(shape) is chikuwa.Person:
                            l = [shape,self.selectedShapeForPopup]
                            r = group.convertFromList(l)
                            self.shapeRelation.addPair(group)
                    elif self.statMode == "createMulti":
                        self.selectedSibForPopup.addPersonToMulti(self.selectedShapeForPopup,shape)
                    elif self.statMode == "createSib":
                        index = self.shapeSiblings.searchSibByPerson(shape)
                        if index is None:
                            group = chikuwa.familyGroup()
                            l = [shape,self.selectedShapeForPopup]
                            r = group.convertFromList(l)
                            self.shapeSiblings.addSib(group)
                        else:
                            self.shapeSiblings.addPersonFromSibIndex(self.selectedShapeForPopup,index)
                    elif self.statMode == "createPCRL":
                        index = self.shapeSiblings.searchSibByPerson(shape)
                        if index is None:
                            group = chikuwa.familyGroup()
                            l = [shape]
                            r = group.convertFromList(l)
                            self.shapeSiblings.addSib(group)
                            index = self.shapeSiblings.searchSibByPerson(shape)
                        else:
                            pass
                        fgg = chikuwa.fgGroup()
                        fdict = {"relation": self.selectedRelForPopup ,"sibling" : self.shapeSiblings.SiblingList[index]}
                        fgg.convertFromDict(fdict)
                        self.shapePCRL.add(fgg)
                    else:
                        pass
                    self.isArrowShow = False
                    self.reInitialisedPupPar()
                    self.statMode = None
                    self.Refresh(eraseBackground=False)
                else:
                    self.dragShape = shape
                    self.dragStartPos = pos
                    self.selectedShapes =[]
                    self.Refresh(eraseBackground=False)
                return True
            elif self.keyPressed == True:
                self.selectedShapes.append(shape)
                if self.whatKey == "shift":
                    flag = True
                    self.lineModifier(flag)
                elif self.whatKey == "tab":
                    flag = False
                    self.lineModifier(flag)
                self.Refresh(eraseBackground=False)
                return True
            else:
                self.Refresh(eraseBackground=False)
                return False
        elif relation:
            if self.keyPressed == True:
                self.selectedGroups["relation"] = relation
                if self.whatKey == "left":
                    flag = True
                    a = self.pcrlModifier(flag)
                elif self.whatKey == "right":
                    flag = False
                    self.pcrlModifier(flag)
            return True
                    
        elif sibling:
            if self.keyPressed == True:
                self.selectedGroups["sibling"] = sibling
                if self.whatKey == "left":
                    flag = True
                    a = self.pcrlModifier(flag)
                elif self.whatKey == "right":
                    flag = False
                    self.pcrlModifier(flag)
            return True
        elif obj:
            self.dragObj = obj
            self.dragStartPos = pos
            return True
        else:
            if self.isArrowShow:
                self.isArrowShow = False
                self.reInitialisedPupPar()
                self.statMode = None
            self.Refresh(eraseBackground=False)
            return False
            
    def OnLeftUp(self,event):
        if self.dragShape:
            pairIndexList = self.shapeRelation.searchPairAllByPerson(self.dragShape)
            sibIndexList = self.shapeSiblings.searchSibAllByPerson(self.dragShape)
            if sibIndexList is not None:
                self.shapeSiblings.alignSibByIndex(sibIndexList,self.dragShape.pos)
            if pairIndexList is not None:
                self.shapeRelation.alignPairByIndex(pairIndexList,self.dragShape.pos)
            while(self.shapeRelation.diffYPosAllPair() is not None or self.shapeSiblings.diffYPosAllSib() is not None):
                dYPaindex = self.shapeRelation.diffYPosAllPair()
                dYSiindex = self.shapeSiblings.diffYPosAllSib()
                if dYSiindex is not None:
                    self.shapeSiblings.alignSibByIndex(dYSiindex,self.dragShape.pos)
                if dYPaindex is not None:
                    self.shapeRelation.alignPairByIndex(dYPaindex,self.dragShape.pos)        
            self.dragShape = None
            self.selectedFalseAll()
        elif self.dragObj:
            self.dragObj = None
        self.Refresh(eraseBackground=False)
        event.Skip()
        
    def OnMotion(self, event):
        if not event.Dragging() or not event.LeftIsDown():
            if self.isArrowShow or self.LineAppendFlag:
                self.Refresh(eraseBackground=False)
            return True

        if self.dragShape:
            tolerance = 2
            pt = event.GetPosition()
            dx = abs(pt.x - self.dragStartPos.x)
            dy = abs(pt.y - self.dragStartPos.y)
            if abs(dx) <= tolerance and abs(dy) <= tolerance:
                return
            self.dragShape.pos = pt.Get()
            self.Refresh(eraseBackground=False)
            
        if self.dragObj:
            tolerance = 2
            pt = event.GetPosition()
            dx = abs(pt.x - self.dragStartPos.x)
            dy = abs(pt.y - self.dragStartPos.y)
            if abs(dx) <= tolerance and abs(dy) <= tolerance:
                return
            self.dragObj.pos = pt.Get()
            self.Refresh(eraseBackground=False)
            
    #@binder(wx.EVT_PAINT)
    def OnPaint(self,event):
        dc = wx.BufferedPaintDC(self,self.buffer,wx.BUFFER_VIRTUAL_AREA)
        self.DrawToBuffer(dc)
        
    def DrawToBuffer(self,dc):
        dc.SetPen(wx.Pen('black'))        
        for linePair in self.shapeRelation.PairList:
            offsetY = int(linePair.offsetYPercent*RADIUS*2)
            offsetX = int(linePair.offsetXPercent*RADIUS*2)
            if offsetY != 0:
                for mem in linePair.member:
                    spt = mem.GetCenterPoint()
                    spt = (spt[0]+offsetX,spt[1])
                    ept = (spt[0],spt[1]+offsetY)
                    dc.DrawLine(spt,ept)
            spt = linePair.member[0].GetCenterPoint()
            spt = (spt[0]+offsetX,spt[1]+offsetY)
            ept = linePair.member[1].GetCenterPoint()
            ept = (ept[0]+offsetX,ept[1]+offsetY)
            dc.DrawLine(spt,ept)
            if linePair.isDivorced:
                disX = abs(spt[0]-ept[0])
                markoffsetX = int(linePair.markOffsetXPercent*disX)
                pos = linePair.getCenterPos()
                pos = (pos[0]+offsetX+markoffsetX,pos[1]-8+offsetY)
                dc.DrawBitmap(self.divorceBitmap,pos)
        
        for siblingGroup in self.shapeSiblings.SiblingList:
            pxl = []
            pyl = []
            aflgs = []
            mulCenterPos = siblingGroup.getCenterMultiPos()
            for child in siblingGroup.member:
                if siblingGroup.isContainedMultiAll(child):
                    continue
                #双子以外がpxlとpylに格納　→ memberindexとずれる！！
                #len(pxl)=len(pyl)=len(aflgs)が前提
                spt = child.GetCenterPoint()
                px = spt.Get()[0]
                pxl.append(px)
                py = spt.Get()[1]
                pyl.append(py)
                aflgs.append(child.adopFlag)
            for i in range(len(pxl)):
                spt = wx.Point(pxl[i],min(pyl)-LENGTH_CHILD_LINE)
                ept = wx.Point(pxl[i],pyl[i])
                if aflgs[i]:dc.SetPen(wx.Pen('black',style=wx.PENSTYLE_DOT))
                else:dc.SetPen(wx.Pen('black',style=wx.PENSTYLE_SOLID))
                #pxrl.append(pxl[i])
                dc.DrawLine(spt,ept)
            dc.SetPen(wx.Pen('black',style=wx.PENSTYLE_SOLID))
            for i in range(len(siblingGroup.MultiBirthList)):
                mb = siblingGroup.MultiBirthList[i] #mb.index = int →　mb.member = person
                pxml = []
                pyml = []
                #index = mb.index
                member = mb.member
                isMonozygotic = mb.isMonozygotic
                cpos = mulCenterPos[i]
                pxl.append(cpos[0])
                pyl.append(cpos[1])
                for m in member:
                    spt = wx.Point(cpos[0],cpos[1]-LENGTH_CHILD_LINE)
                    ept = m.GetCenterPoint()
                    pxml.append(ept[0])
                    pyml.append(ept[1])
                    dc.DrawLine(spt,ept)
                if isMonozygotic and not self.dragShape:
                    maxX = max(pxml)
                    minX = min(pxml)
                    pt1 = (maxX,pyml[pxml.index(maxX)])
                    pt2 = (minX,pyml[pxml.index(maxX)])
                    cpt = (cpos[0],cpos[1]-LENGTH_CHILD_LINE)
                    y = cpt[1]+10
                    spt,ept = crossPointGivenY(pt1,pt2,cpt,y)
                    dc.DrawLine(spt,ept)
            spt = wx.Point(min(pxl),min(pyl)-LENGTH_CHILD_LINE)
            ept = wx.Point(max(pxl),min(pyl)-LENGTH_CHILD_LINE)
            dc.DrawLine(spt,ept)
            
        for pcrl in self.shapePCRL.pcRelationList:
            if pcrl.member[1].length() > 1:
                spt = pcrl.member[0].getCenterPos()
                spt = (spt[0],spt[1]+int(pcrl.member[0].offsetYPercent*RADIUS*2))
                ept = (spt[0],pcrl.member[1].getCenterPos()[1]-LENGTH_CHILD_LINE)
            else:
                ept = (pcrl.member[1].getCenterPos()[0],pcrl.member[1].getCenterPos()[1]-LENGTH_CHILD_LINE)
                spt = (ept[0],pcrl.member[0].getCenterPos()[1]+int(pcrl.member[0].offsetYPercent*RADIUS*2))
            dc.DrawLine(spt,ept)
            
        if self.isArrowShow:
            self.DrawArrow(dc,mode=0)
        
        if self.LineAppendFlag == True and self.LineAppendSpt != 0:
            self.DrawArrow(dc,mode=1)
        
        self.DrawObjs(dc)
        
        self.DrawShapes(dc)
        if self.isGenerationVisible:
            self.generationShow(dc)
            
        self.DrawLineObjs(dc)
        ##
        del dc
        #del mdc
        self.initBackground(self.buffer)
        self.Refresh(False)
        self.Update()
        
    def OnKeyDown(self,event):
        keyCode = event.GetKeyCode()
        for val in self.keyMap.items():
            if keyCode == val[0]:
                self.keyPressed = True
                self.whatKey = val[1]
        event.Skip()
    
    def OnKeyUp(self,event):
        if self.whatKey == 'up':
            self.sibModifier(True)
        if self.whatKey == 'down':
            self.sibModifier(False)
        self.keyPressed = False
        self.whatKey = False
        if len(self.selectedShapes) > 0:
            for shape in self.selectedShapes:
                shape.isSelected = False
            self.selectedShapes =[]
        if self.selectedGroups["relation"] is not None or self.selectedGroups["sibling"] is not None:
            self.selectedGroups = {
            "relation": None ,
            "sibling" : None
            }
        event.Skip()
        
    def selectedFalseAll(self):
        for shape in self.shapes:
            shape.isSelected = False
        return True
        
    def OnContextMenu(self,event):
        pos = self.mousePositionForPopup
        shape = self.FindShape(pos)
        sRel = self.shapeRelation.searchPairByPerson(shape)
        sSib = self.shapeSiblings.searchSibByPerson(shape)
        Rela = self.FindRelation(pos)
        Sibl = self.FindSibling(pos)
        obj = self.FindObj(pos)
        lineObj = self.FindLineObj(pos)
        
        
        self.selectedShapeForPopup = shape
        
        
        menu = wx.Menu()
        if not hasattr(self,"pId1"):
            self.pId1 = wx.NewId()
            self.pId2 = wx.NewId()
            self.pId3 = wx.NewId()
            self.pId4 = wx.NewId()
            self.pId5 = wx.NewId()
            self.pId6 = wx.NewId()
            self.pId7 = wx.NewId()
            self.pId8 = wx.NewId()
            self.pId9 = wx.NewId()
            self.pId10 = wx.NewId()
            self.pId11 = wx.NewId()
            self.pId12 = wx.NewId()
            self.pId13 = wx.NewId()
            self.pId14 = wx.NewId()
            self.pId15 = wx.NewId()
            self.pId16 = wx.NewId()
            self.pId17 = wx.NewId()
            self.pId18 = wx.NewId()
            self.pId19 = wx.NewId()
            self.pId20 = wx.NewId()
            self.pId21 = wx.NewId()
            self.pId22 = wx.NewId()
            self.pId23 = wx.NewId()
            self.pId24 = wx.NewId()
        if shape is None:
            menu.Append(self.pId2,"新規作成")
            menu.Append(self.pId17,"テキスト新規作成")
            if Rela is not None:
                self.selectedRelForPopup = Rela
                menu.Append(self.pId7,"配偶者関係を削除")
                menu.Append(self.pId15,"婚姻ステータス変更")
                menu.Append(self.pId16,"y軸オフセット値調整")
                menu.Append(self.pId20,"x軸オフセット値調整")
                menu.Append(self.pId21,"マーク位置を調整")
                if self.shapePCRL.searchPCRLBySingularGroup(Rela) is None:
                    menu.Append(self.pId13,"子孫を追加")
                else:
                    menu.Append(self.pId14,"子孫関係を解消")
            if Sibl is not None:
                menu.Append(self.pId8,"兄弟姉妹関係を全削除")
                self.selectedSibForPopup = Sibl
            if obj is not None:
                self.selectedObjForPopup = obj
                menu.Append(self.pId18,"テキスト編集")
                menu.Append(self.pId19,"テキスト削除")
            if lineObj is not None:
                self.selectedLineObjForPopup = lineObj
                menu.Append(self.pId23,"線を削除")
                menu.Append(self.pId24,"線スタイル変更")
                
        else:
            shape.isSelected = True
            menu.Append(self.pId1,"削除")
            menu.Append(self.pId3,"情報を表示")
            menu.Append(self.pId4,"編集")
            if sSib is None:
                menu.Append(self.pId6,"兄弟姉妹関係に追加")
            else:
                menu.Append(self.pId9,"兄弟姉妹関係から離脱")
                menu.Append(self.pId22,"個人線を実線←→点線")
                self.selectedSibForPopup = self.shapeSiblings.SiblingList[sSib]
                if self.selectedSibForPopup.searchMultiByPerson(shape) is None: #双子の一部の場合
                    menu.Append(self.pId10,"双子の登録先を指定")
                else:
                    menu.Append(self.pId11,"一卵性←→多卵生")
                    menu.Append(self.pId12,"双子関係を削除")
                self.selectedSibIndexForPopup = sSib
            if sRel is None:
                if type(shape) is chikuwa.Person:
                    menu.Append(self.pId5,"配偶者を追加")
            else:
                pass
                
                
        menu.Bind(wx.EVT_MENU,self.menuSelector)
        self.PopupMenu(menu)
        menu.Destroy()
        #self.reInitialisedPupPar()


    def menuSelector(self,event):
        whatId = event.GetId()
        if whatId == self.pId1:
            self.deleteShape(self.selectedShapeForPopup)
            self.reInitialisedPupPar()
        elif whatId == self.pId2:
            self.addShape(self.mousePositionForPopup)
            self.reInitialisedPupPar()
        elif whatId == self.pId3:
            wx.MessageBox("{}".format(self.selectedShapeForPopup.getInfo()[0]))
            self.reInitialisedPupPar()
        elif whatId == self.pId4:
            self.editFrameOpen()
            self.reInitialisedPupPar()
        elif whatId == self.pId5:
            self.addPairByClick()
        elif whatId == self.pId6:
            self.addSibByClick()
        elif whatId == self.pId7:
            self.deletePairByMenu()
        elif whatId == self.pId8:
            self.deleteSibAllByClick()
        elif whatId == self.pId9:
            self.removeFromSibByClick()
        elif whatId == self.pId10:
            self.addMultiByClick()
        elif whatId == self.pId11:
            self.changeMultiType()
        elif whatId == self.pId12:
            self.deleteMulti()
        elif whatId == self.pId13:
            self.addPCRLByClick()
        elif whatId == self.pId14:
            self.deletePCRLByClick()
        elif whatId == self.pId15:
            self.changeDivorceFlagByClick()
        elif whatId == self.pId16:
            self.openOffsetYController()
        elif whatId == self.pId17:
            self.createNewObjByClick()
        elif whatId == self.pId18:
            self.openEditObjController()
        elif whatId == self.pId19:
            self.deleteObjByClick()
        elif whatId == self.pId20:
            self.openOffsetXController()       
        elif whatId == self.pId21:
            self.openMarkOffsetXController()
        elif whatId == self.pId22:
            self.changeLineType()
        elif whatId == self.pId23:
            self.deleteLineObjByClick()
        elif whatId == self.pId24:
            self.changeLineObjProp()
        else:
            return False
        
    def reInitialisedPupPar(self):
        self.mousePositionForPopup = wx.Point()
        self.selectedShapeForPopup = None
        self.selectedSibForPopup = None
        self.selectedRelForPopup = None
        self.selectedObjForPopup = None
        self.selectedLineObjForPopup = None
        self.selectedSibIndexForPopup = 0
        self.selectedRelIndexForPopup = 0
        return True
        
    def addShape(self,pos):
        shape = chikuwa.Person()
        shape.pos = pos
        self.shapes.append(shape)
        self.Refresh(eraseBackground=False)
    
    def addPersonByController(self,info):
        shape = chikuwa.Person()
        shape.update(info)
        self.shapes.append(shape)
        self.Refresh(eraseBackground=False)
        return shape
    
    def addPreNotCTByController(self,info):
        shape = chikuwa.PreNotCT()
        shape.update(info)
        self.shapes.append(shape)
        self.Refresh(eraseBackground=False)
        return shape
        
    def deleteShape(self,shape):
        if shape is None:
            return False
        self.shapes.remove(shape)
        sibIndex = self.shapeSiblings.searchSibByPerson(shape)
        pairIndex = self.shapeRelation.searchPairAllByPerson(shape)
        if sibIndex is not None:
            self.shapeSiblings.deletePersonFromSibIndex(shape,sibIndex)
            if self.shapeSiblings.isEmptySibByIndex(sibIndex):
                sib = self.shapeSiblings.SiblingList[sibIndex]
                pcrlIndex = self.shapePCRL.searchPCRLBySingularGroup(sib)
                if pcrlIndex is not None:
                    self.shapePCRL.deleteByIndex(pcrlIndex)
                self.shapeSiblings.deleteSibByIndex(sibIndex)
        if pairIndex is not None:
            for pIdx in sorted(pairIndex,reverse=True):
                self.shapeRelation.deletePersonFromPairIndex(shape,pIdx)
                if self.shapeRelation.isEmptyPairByIndex(pIdx):
                    pair = self.shapeRelation.PairList[pIdx]
                    pcrlIndex = self.shapePCRL.searchPCRLBySingularGroup(pair)
                    if pcrlIndex is not None:
                        self.shapePCRL.deleteByIndex(pcrlIndex)
                    self.shapeRelation.deletePairByIndex(pIdx)
        self.Refresh(eraseBackground=False)
        return True
    
    def deleteShapeByClick(self,event):
        pos = event.GetPosition()
        shape = self.FindShape(pos)
        if shape is not None:
            self.deleteShape(shape)
        self.Refresh(eraseBackground=False)
        
    def deletePairByMenu(self):
        pair = self.selectedRelForPopup
        pcrlIndex = self.shapePCRL.searchPCRLBySingularGroup(pair)
        if pcrlIndex is not None:self.shapePCRL.deleteByIndex(pcrlIndex)
        self.shapeRelation.deletePair(pair)
        self.reInitialisedPupPar()
        self.Refresh(eraseBackground=False)
        
    def editFrameOpen(self):
        if type(self.selectedShapeForPopup) is chikuwa.Person:
            typeIndv = "person"
        else:
            typeIndv = "PreNotCT"
        edFrame = editFrame(self,-1,typeIndv)
        edFrame.setShape(self.selectedShapeForPopup)
        edFrame.initComponents()
        edFrame.Show(True)
    
    def openOffsetYController(self):
        oYChanger = offsetYChanger(self,-1,pos=self.mousePosAbsolute)
        oYChanger.setGroup(self.selectedRelForPopup)
        oYChanger.setCanvas(self)
        oYChanger.initialise()
        oYChanger.Show(True)

    def openOffsetXController(self):
        oXChanger = offsetXChanger(self,-1,pos=self.mousePosAbsolute)
        oXChanger.setGroup(self.selectedRelForPopup)
        oXChanger.setCanvas(self)
        oXChanger.initialise()
        oXChanger.Show(True)
        
    def openMarkOffsetXController(self):
        moXChanger = markOffsetXChanger(self,-1,pos=self.mousePosAbsolute)
        moXChanger.setGroup(self.selectedRelForPopup)
        moXChanger.setCanvas(self)
        moXChanger.initialise()
        moXChanger.Show(True)
    #self.mousePosAbsolute
        
    def addPairByClick(self):
        self.isArrowShow = True
        self.statMode = "createPair"

    def addMultiByClick(self):
        self.isArrowShow = True
        self.statMode = "createMulti"
    
    def addSibByClick(self):
        self.isArrowShow = True
        self.statMode = "createSib"  
        
    def addPCRLByClick(self):
        self.isArrowShow = True
        self.statMode = "createPCRL"  
    
    def removeFromSibByClick(self):
        index = self.selectedSibIndexForPopup
        sib = self.selectedSibForPopup
        pcrlIndex = self.shapePCRL.searchPCRLBySingularGroup(sib)
        if sib.length() < 2 and pcrlIndex is not None:
            self.shapePCRL.deleteByIndex(pcrlIndex)
        self.shapeSiblings.deletePersonFromSibIndex(self.selectedShapeForPopup,index)
        self.Refresh(eraseBackground=False)
        
    def changeMultiType(self):
        index = self.selectedSibForPopup.searchMultiByPerson(self.selectedShapeForPopup)
        monozy = self.selectedSibForPopup.MultiBirthList[index].isMonozygotic
        if monozy:
            monozy = False
        else:
            monozy = True
        self.selectedSibForPopup.MultiBirthList[index].isMonozygotic = monozy
        self.Refresh(eraseBackground=False)
        return True
    
    def changeLineType(self):
        self.selectedShapeForPopup.adopFlag = not self.selectedShapeForPopup.adopFlag
        self.Refresh(eraseBackground=False)
        return True
    
    def deleteMulti(self):
        index = self.selectedSibForPopup.searchMultiByPerson(self.selectedShapeForPopup)
        self.selectedSibForPopup.deleteMultiByIndex(index)
        self.Refresh(eraseBackground=False)
        return True
    
    def deleteSibAllByClick(self):
        sib = self.selectedSibForPopup
        pcrlIndex = self.shapePCRL.searchPCRLBySingularGroup(sib)
        if pcrlIndex is not None:self.shapePCRL.deleteByIndex(pcrlIndex)
        self.shapeSiblings.deleteSib(sib)
        self.reInitialisedPupPar()
        self.Refresh(eraseBackground=False)
        
    def deletePCRLByClick(self):
        rel = self.selectedRelForPopup
        pcrlIndex = self.shapePCRL.searchPCRLBySingularGroup(rel)
        fgg = self.shapePCRL.pcRelationList[pcrlIndex]
        sib = fgg.member[1]
        if sib.length() < 2:
            self.shapeSiblings.deleteSib(sib)
        self.shapePCRL.deleteByIndex(pcrlIndex)
        return True
    
    def changeDivorceFlagByClick(self):
        flag = self.selectedRelForPopup.isDivorced
        if flag == True:
            flag = False
        else:
            flag = True
        self.selectedRelForPopup.isDivorced = flag
        self.reInitialisedPupPar()
        self.Refresh(eraseBackground=False)
    
    def addObj(self,pos):
        obj = chikuwa.textBox()
        obj.pos = pos
        self.objs.append(obj)
        return True
        
    def createNewObjByClick(self):
        self.addObj(self.mousePositionForPopup)
        self.reInitialisedPupPar()
        self.Refresh(eraseBackground=False)
        return True
    
    def deleteObjByClick(self):
        self.objs.remove(self.selectedObjForPopup)
        self.reInitialisedPupPar()
        self.Refresh(eraseBackground=False)
        return True
    
    def deleteLineObjByClick(self):
        self.lines.remove(self.selectedLineObjForPopup)
        self.reInitialisedPupPar()
        self.Refresh(eraseBackground=False)
        return True
    
    def changeLineObjProp(self):
        if self.selectedLineObjForPopup.penStyle == wx.PENSTYLE_DOT:
            self.selectedLineObjForPopup.penStyle = wx.PENSTYLE_SOLID
        else:
            self.selectedLineObjForPopup.penStyle = wx.PENSTYLE_DOT
        self.reInitialisedPupPar()
        self.Refresh(eraseBackground=False)
        return True

    def openEditObjController(self):
        eoController = textEditController(self,-1,pos=self.mousePosAbsolute)
        eoController.setObj(self.selectedObjForPopup)
        eoController.setCanvas(self)
        eoController.initialise()
        eoController.Show(True)
        return True
        
    def OnRightDown(self,event):
        self.mousePositionForPopup = event.GetPosition()
        self.mousePosAbsolute = wx.GetMousePosition()
        event.Skip()
    
    def OnRightUp(self,event):
        self.selectedFalseAll()
        event.Skip()
    
    def expToImage(self,path,mimeIndex=0):
        bmp = wx.Bitmap(self.maxWidth,self.maxHeight)
        mdc = wx.MemoryDC()
        mdc.SelectObject(bmp)
        brush = wx.Brush("white")
        mdc.SetBackground(brush)
        mdc.Clear()
        self.DrawToBuffer(mdc)
        img = bmp.ConvertToImage()
        mt = chikuwa.MimeType()
        wxmime = mt.getWxMethod(mimeIndex)
        result = img.SaveFile(path, wxmime)
        return result
    
    def deleteCanvas(self):
        self.shapes = []
        self.objs = []
        self.dragObj = None
        self.dragShape = None
        self.dragStartPos = None
        self.hiliteShape = None
        self.keyPressed = False
        self.whatKey = False
        self.selectedShapes = []
        self.selectedGroups = {
            "relation": None ,
            "sibling" : None
        }
        self.mousePositionForPopup = wx.Point()
        self.mousePosAbsolute = wx.Point()
        self.selectedShapeForPopup = None
        self.selectedSibForPopup = None
        self.selectedRelForPopup = None
        self.selectedObjForPopup = None
        self.selectedSibIndexForPopup = 0
        self.selectedRelIndexForPopup = 0
        self.shapeRelation = chikuwa.relationArguments()
        self.shapeSiblings = chikuwa.siblingArguments()
        self.shapePCRL = chikuwa.parentChildRelationArgument()
        self.isArrowShow = False
        self.statMode = None
        self.LineAppendFlag = False
        self.LineAppendSpt = 0
        
        self.lines = []
        self.Refresh(eraseBackground=False)
        
    def switchGenVisibility(self):
        if self.isGenerationVisible:#True
                self.isGenerationVisible = False
                for mem in self.shapes:
                    pos = (mem.pos[0]-30,mem.pos[1])
                    mem.pos = pos
        else:
                self.isGenerationVisible = True
                for mem in self.shapes:
                    pos = (mem.pos[0]+30,mem.pos[1])
                    mem.pos = pos
        self.Refresh(eraseBackground=False)
        return True
            
        
    def generationShow(self,dc):
        genYlist = self.genGenY()
        if len(genYlist) > 11:
            return False
        romanNum = ["I","II","III","IV","V","VI","VII","VIII","IX","X"]
        for gY in genYlist:
            i = genYlist.index(gY)
            gpos = (10,gY)
            dc.SetTextForeground('black')
            font = wx.Font(25,wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            dc.SetFont(font)
            dc.DrawText(romanNum[i],gpos)
        
        
    def genGenY(self):
        personYlist = []
        genYlist = []
        margin = 50
        for mem in self.shapes:
            personYlist.append(mem.pos[1])
        if len(personYlist) > 0:
            genYlist.append(min(personYlist))
            personYlist.sort()
            minY = min(personYlist)
            for pY in personYlist[:]:
                if minY <= pY and pY < minY+margin:
                    continue
                else:
                    genYlist.append(pY)
                    minY = pY
            return genYlist
        else:
            return genYlist
        
class offsetYChanger(wx.Frame):
    def __init__(self, parent, ID,title="y軸調整%", pos=wx.DefaultPosition,size=(130,200), style=wx.FRAME_TOOL_WINDOW|wx.CLOSE_BOX|wx.CAPTION):

        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        self.group = chikuwa.familyGroup()
        self.canvas = 0
        self.defaultOffsetY = 0
        
        panel = wx.Panel(self, -1)
        
        self.slider = wx.Slider(panel,value=0, minValue=-300, maxValue=300,style=wx.SL_VERTICAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        
        self.defaultButton = wx.Button(panel, -1, "最初の値へ")
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.slider, flag=wx.SHAPED | wx.ALIGN_CENTER)
        self.sizer.Add(self.defaultButton, flag=wx.SHAPED | wx.ALIGN_CENTER)
        panel.SetSizer(self.sizer)
        
        self.slider.Bind(wx.EVT_SLIDER, self.valueChange)
        self.defaultButton.Bind(wx.EVT_BUTTON, self.OnDefaultButton)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
    def initialise(self):
        self.defaultOffsetY = self.group.offsetYPercent*100
        self.setDefault()
        
    def setDefault(self):
        self.slider.SetValue(self.defaultOffsetY)
        return True
    
    def OnDefaultButton(self,event):
        self.setDefault()
        return True
        
    def setGroup(self,group):
        self.group = group
        return True
    
    def setCanvas(self,canvas):
        self.canvas = canvas
        return True
    
    def valueChange(self,event):
        valY = self.slider.GetValue()
        self.group.offsetYPercent = valY/100
        self.canvas.Refresh(eraseBackground=False)
        return True
    
    def OnCloseWindow(self,event):
        self.Destroy()
        
class offsetXChanger(wx.Frame):
    def __init__(self, parent, ID,title="x軸調整%", pos=wx.DefaultPosition,size=(260,100), style=wx.FRAME_TOOL_WINDOW|wx.CLOSE_BOX|wx.CAPTION):

        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        self.group = chikuwa.familyGroup()
        self.canvas = 0
        self.defaultOffsetX = 0
        
        panel = wx.Panel(self, -1)
        
        self.slider = wx.Slider(panel,value=0, minValue=-50, maxValue=50,style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        
        self.defaultButton = wx.Button(panel, -1, "最初の値へ")
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.slider, flag=wx.SHAPED | wx.ALIGN_CENTER)
        self.sizer.Add(self.defaultButton, flag=wx.SHAPED | wx.ALIGN_CENTER)
        panel.SetSizer(self.sizer)
        
        self.slider.Bind(wx.EVT_SLIDER, self.valueChange)
        self.defaultButton.Bind(wx.EVT_BUTTON, self.OnDefaultButton)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
    def initialise(self):
        self.defaultOffsetX = self.group.offsetXPercent*100
        self.setDefault()
        
    def setDefault(self):
        self.slider.SetValue(int(self.defaultOffsetX))
        return True
    
    def OnDefaultButton(self,event):
        self.setDefault()
        return True
        
    def setGroup(self,group):
        self.group = group
        return True
    
    def setCanvas(self,canvas):
        self.canvas = canvas
        return True
    
    def valueChange(self,event):
        valX = self.slider.GetValue()
        self.group.offsetXPercent = valX/100
        self.canvas.Refresh(eraseBackground=False)
        return True
    
    def OnCloseWindow(self,event):
        self.Destroy()
        
class markOffsetXChanger(offsetXChanger):
    def __init__(self, parent, ID,title="x軸調整%", pos=wx.DefaultPosition,size=(260,100), style=wx.FRAME_TOOL_WINDOW|wx.CLOSE_BOX|wx.CAPTION):
        offsetXChanger.__init__(self, parent, ID, title, pos, size, style)
        
    def initialise(self):
        self.defaultOffsetX = self.group.markOffsetXPercent*100
        self.setDefault()
    
    def valueChange(self,event):
        valX = self.slider.GetValue()
        self.group.markOffsetXPercent = valX/100
        self.canvas.Refresh(eraseBackground=False)
        return True
        
class leftPanel(wx.Panel):
    def __init__(self,parent,ID):
        wx.Panel.__init__(self,parent,ID)
        #self.SetBackgroundColour("grey")
        self.tb = wx.ToolBar(self,-1,style=wx.TB_VERTICAL|wx.TB_TEXT)
        self.initialise()
        self.canvas = 0
        self.controller = 0
    
    def initialise(self):
        component = [
            [10,"キャンパス新規作成","./src/c1.png","キャンパス新規作成",wx.ITEM_NORMAL],
            [20,"新規作成","./src/c2.png","新規作成",wx.ITEM_NORMAL],
            [30,"テキスト新規作成","./src/c3.png","テキスト新規作成",wx.ITEM_NORMAL],
            [40,"線描画","./src/c4.png","線描画",wx.ITEM_NORMAL],
            [50,"世代を表示","./src/c5.png","世代を表示する",wx.ITEM_CHECK],
            [60,"画像として保存","./src/c6.png","画像保存",wx.ITEM_NORMAL],
            [70,"保存","./src/c7.png","保存",wx.ITEM_NORMAL],
            [80,"開く","./src/c8.png","開く",wx.ITEM_NORMAL]
        ]
        for toolId,label,bitmap_path,shortHelp,kind in component:
            bitmap = wx.Bitmap(bitmap_path)
            self.tb.AddTool(toolId,label,bitmap,shortHelp=shortHelp,kind=kind)
            self.Bind(wx.EVT_TOOL, self.OnToolClick, id=toolId)
            #self.tb.AddSeparator()        
        self.tb.Realize()
        return True
    
    def setCanvas(self,canvas):
        self.canvas = canvas
        return True
    
    def setController(self,controller):
        self.controller = controller
        return True
    
    def OnToolClick(self,event):
        eid = event.GetId()
        if eid == 10:
            self.canvas.deleteCanvas()
        elif eid == 20:
            self.controller.masterNote.SetSelection(0)
        elif eid == 30:
            self.controller.masterNote.SetSelection(1)
        elif eid == 40:
            if self.canvas.statMode is None:
                self.canvas.statMode = "createLine"
            else:
                self.canvas.statMode = None
        elif eid == 50:
            self.canvas.switchGenVisibility()
        elif eid == 60:
            self.OnExpImage()
        elif eid == 70:
            self.OnExpZip()
        elif eid == 80:
            self.OnOpenChkwFile()
        return True
    
    def OnOpenChkwFile(self):
        dlg = wx.FileDialog(self, message="開くファイルを指定...",wildcard='Chikuwa (*.chkw)|*.chkw', style=wx.FD_OPEN| wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            chikuwa.readChkw(self.canvas,path)
            return True
        elif dlg.ShowModal() == wx.ID_CANCEL:
            dlg.Destroy()
            wx.MessageBox('キャンセルしました')
            return False
        
        
    def OnExpImage(self):
        mt = chikuwa.MimeType()
        wildcard = mt.getWildcard()
        dlg = wx.FileDialog(self, message="保存先を指定...",wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            mimeIndex = dlg.GetFilterIndex()
            dlg.Destroy()
        elif dlg.ShowModal() == wx.ID_CANCEL:
            dlg.Destroy()
            wx.MessageBox("キャンセルしました")
            return False
        result = self.canvas.expToImage(path,mimeIndex)
        if result:
            wx.MessageBox("保存しました")
        else:
            wx.MessageBox("保存に失敗しました")
        return True
    
    def OnExpZip(self):
        dlg = wx.FileDialog(self, message="保存先を指定...",wildcard='Chikuwa (*.chkw)|*.chkw', style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        dlg.SetFilterIndex(0)
        path = ''
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
        elif dlg.ShowModal() == wx.ID_CANCEL:
            dlg.Destroy()
            wx.MessageBox("キャンセルしました")
            return False
        result = chikuwa.expTofile(self.canvas,path)
        if result:
            wx.MessageBox("保存しました")
        else:
            wx.MessageBox("保存に失敗しました")
        return True
        
        
class textEditController(wx.Frame):
    def __init__(self, parent, ID,title="編集...", pos=wx.DefaultPosition,size=(300,300), style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        panel = wx.Panel(self, -1)
        self.obj = 0
        self.canvas = 0
        
        self.textControl = wx.TextCtrl(panel,-1,"",style=wx.TE_MULTILINE)
        self.fontSizer = wx.Slider(panel,value=1, minValue=1, maxValue=100,style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.cbOutlineVisible = wx.CheckBox(panel, -1, "外枠を表示")
        self.colTXButton = wx.Button(panel,-1,"文字色...")
        self.colBGButton = wx.Button(panel,-1,"背景色...")
        self.colOLButton = wx.Button(panel,-1,"外枠色...")
        self.previewButton = wx.Button(panel, -1, "プレビュー")
        self.editButton = wx.Button(panel, -1, "確定")
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer3 = wx.BoxSizer(wx.HORIZONTAL)

        self.sizer3.Add(self.colTXButton)
        self.sizer3.Add(self.colBGButton)
        self.sizer3.Add(self.colOLButton)
        
        self.sizer2.Add(self.previewButton)
        self.sizer2.Add(self.editButton)
        
        self.sizer.Add(self.textControl,10,flag=wx.GROW)
        self.sizer.Add(self.cbOutlineVisible)
        self.sizer.Add(wx.StaticLine(panel), flag=wx.GROW)
        self.sizer.Add(wx.StaticText(panel, -1, 'フォントサイズ'))
        self.sizer.Add(self.fontSizer,flag=wx.GROW)
        self.sizer.Add(wx.StaticLine(panel), flag=wx.GROW)
        self.sizer.Add(wx.StaticText(panel, -1, '色の変更'))
        self.sizer.Add(self.sizer3,flag=wx.ALIGN_CENTER)
        self.sizer.Add(wx.StaticLine(panel), flag=wx.GROW)
        self.sizer.Add(self.sizer2,flag=wx.ALIGN_CENTER|wx.TOP,border=20)
        panel.SetSizer(self.sizer)
        
        self.previewButton.Bind(wx.EVT_BUTTON, self.OnPreviewButton)
        self.colTXButton.Bind(wx.EVT_BUTTON, self.changeForegroundColor)
        self.colBGButton.Bind(wx.EVT_BUTTON, self.changeForegroundColor)
        self.colOLButton.Bind(wx.EVT_BUTTON, self.changeForegroundColor)
        self.editButton.Bind(wx.EVT_BUTTON, self.OnEditButton)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    
    def initialise(self):
        self.textControl.SetValue(self.obj.text)
        self.fontSizer.SetValue(self.obj.textSize)
        self.cbOutlineVisible.SetValue(self.obj.isOutlineVisible)
        self.colTXButton.SetForegroundColour(self.obj.textColor)
        self.colBGButton.SetForegroundColour(self.obj.bgColor)
        self.colOLButton.SetForegroundColour(self.obj.outlineColor)
        return True
    
    def setObj(self,obj):
        self.obj = obj
        return True
    
    def setCanvas(self,canvas):
        self.canvas = canvas
        return True
    
    def modify(self):
        self.obj.text = self.textControl.GetValue()
        self.obj.appendTextSize(float(self.fontSizer.GetValue()))
        self.obj.isOutlineVisible = self.cbOutlineVisible.GetValue()
        OLcol = self.colOLButton.GetForegroundColour()
        TXcol = self.colTXButton.GetForegroundColour()
        BGcol = self.colBGButton.GetForegroundColour()
        self.obj.appendColor(OLcol,TXcol,BGcol)
        return True
    
    def changeForegroundColor(self,event):
        button = event.GetEventObject()
        colour = button.GetForegroundColour()
        cld = wx.ColourData()
        cld.SetColour(colour)
        dlg = wx.ColourDialog(self,data=cld)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            color = data.GetColour()
            button.SetForegroundColour(color)
        dlg.Destroy()
    
    def OnPreviewButton(self,event):
        self.modify()
        self.canvas.Refresh(eraseBackground=False)
    
    def OnEditButton(self,event):
        self.modify()
        self.Close(True)
    
    def OnCloseWindow(self,event):
        self.Destroy()
        
class textNewControllerPanel(wx.Panel):
    def __init__(self,parent,ID):
        wx.Panel.__init__(self,parent,ID)
        self.obj = 0
        self.canvas = 0
        
        self.textControl = wx.TextCtrl(self,-1,"",style=wx.TE_MULTILINE)
        self.fontSizer = wx.Slider(self,value=15, minValue=1, maxValue=100,style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.cbOutlineVisible = wx.CheckBox(self, -1, "外枠を表示")
        self.colTXButton = wx.Button(self,-1,"文字色...")
        self.colBGButton = wx.Button(self,-1,"背景色...")
        self.colOLButton = wx.Button(self,-1,"外枠色...")
        self.createButton = wx.Button(self, -1, "作成")
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer3 = wx.BoxSizer(wx.HORIZONTAL)

        self.sizer3.Add(self.colTXButton)
        self.sizer3.Add(self.colBGButton)
        self.sizer3.Add(self.colOLButton)
        
        self.sizer2.Add(self.createButton)
        
        self.sizer.Add(self.textControl,10,flag=wx.GROW)
        self.sizer.Add(self.cbOutlineVisible)
        self.sizer.Add(wx.StaticLine(self), flag=wx.GROW)
        self.sizer.Add(wx.StaticText(self, -1, 'フォントサイズ'))
        self.sizer.Add(self.fontSizer,flag=wx.GROW)
        self.sizer.Add(wx.StaticLine(self), flag=wx.GROW)
        self.sizer.Add(wx.StaticText(self, -1, '色の変更'))
        self.sizer.Add(self.sizer3,flag=wx.ALIGN_CENTER)
        self.sizer.Add(wx.StaticLine(self), flag=wx.GROW)
        self.sizer.Add(self.sizer2,flag=wx.ALIGN_CENTER|wx.TOP,border=20)
        self.SetSizer(self.sizer)
        
        self.initialise()
        
        self.colTXButton.Bind(wx.EVT_BUTTON, self.changeForegroundColor)
        self.colBGButton.Bind(wx.EVT_BUTTON, self.changeForegroundColor)
        self.colOLButton.Bind(wx.EVT_BUTTON, self.changeForegroundColor)
        self.createButton.Bind(wx.EVT_BUTTON, self.OnCreateButton)
    
    
    def setCanvas(self,canvas):
        self.canvas = canvas
        return True
    
    def initialise(self):
        self.colTXButton.SetForegroundColour(wx.Colour(0,0,0,255))
        self.colBGButton.SetForegroundColour(wx.Colour(255,255,255,255))
        self.colOLButton.SetForegroundColour(wx.Colour(0,0,0,255))
    
    def modify(self):
        obj = chikuwa.textBox()
        obj.text = self.textControl.GetValue()
        obj.appendTextSize(float(self.fontSizer.GetValue()))
        obj.isOutlineVisible = self.cbOutlineVisible.GetValue()
        OLcol = self.colOLButton.GetForegroundColour()
        TXcol = self.colTXButton.GetForegroundColour()
        BGcol = self.colBGButton.GetForegroundColour()
        obj.appendColor(OLcol,TXcol,BGcol)
        self.canvas.objs.append(obj)
        return True
    
    def changeForegroundColor(self,event):
        button = event.GetEventObject()
        colour = button.GetForegroundColour()
        cld = wx.ColourData()
        cld.SetColour(colour)
        dlg = wx.ColourDialog(self,data=cld)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            color = data.GetColour()
            button.SetForegroundColour(color)
        dlg.Destroy()
    
    def OnCreateButton(self,event):
        self.modify()
        self.canvas.Refresh(eraseBackground=False)
        
    
class editFrame(wx.Frame):
    def __init__(self, parent, ID, typeIndv,title="編集...", pos=wx.DefaultPosition,size=(400,400), style=wx.CAPTION | wx.CLOSE_BOX):

        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        self.shape = chikuwa.Person()
        self.typeIndv = typeIndv
        if self.typeIndv == "person":
            self.panel = personPanelCompo(self,-1,1)
        else:
            self.panel = babyPanelCompo(self, -1,1)
        self.panel.editButton.Bind(wx.EVT_BUTTON,self.OnUpdateButton)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
    def setShape(self,shape):
        self.shape = shape
        return True
    
    def initComponents(self):
        info = self.shape.info
        if self.typeIndv == "person":
            self.panel.sexSelector.SetSelection(info.sex)
            self.panel.statusSelector.SetSelection(info.statType)
            self.panel.ageUnitSelector.SetSelection(info.ageUnit)
            self.panel.ageControl.SetValue(info.age)
            self.panel.markCheckbox.SetValue(info.isMarked)
            self.panel.adoptedCheckbox.SetValue(info.isAdopted)
            self.panel.affSelector.SetSelection(info.affType)
            self.panel.setDctrlbyList(info.diseaseList)
            return True
        else:
            self.panel.sexSelector.SetSelection(info.sex)
            self.panel.ageControl.SetValue(info.age)
            self.panel.affSelector.SetSelection(info.affType)
            self.panel.statusSelector.SetSelection(info.statType)
            self.panel.footerControl.SetValue(info.footer)
            return True
        
    def OnUpdateButton(self,event):
        panel = self.panel
        if self.typeIndv == "person":
            sex = panel.sexSelector.GetSelection()
            statType = panel.statusSelector.GetSelection()
            ageUnit = panel.ageUnitSelector.GetSelection()
            affType = panel.affSelector.GetSelection()
            age = panel.ageControl.GetValue()
            isMarked = panel.markCheckbox.GetValue()
            isAdopted = panel.adoptedCheckbox.GetValue()
            diseaseList = panel.getDList()
            info = chikuwa.infoContainer(sex=sex,
                                       age=age,
                                       ageUnit=ageUnit,
                                       statType=statType,
                                       affType=affType,
                                       isMarked=isMarked,
                                       isAdopted=isAdopted,
                                      diseaseList=diseaseList
                                      )
        else:
            sex = panel.sexSelector.GetSelection()
            statType = panel.statusSelector.GetSelection()
            affType = panel.affSelector.GetSelection()
            age = panel.ageControl.GetValue()
            footer = panel.footerControl.GetValue()
            info = chikuwa.infoBabyContainer(sex=sex,age=age,statType=statType,footer=footer,affType=affType)
        self.shape.update(info)
        self.Close(True)        
    
    def OnCloseWindow(self,event):
        self.Destroy()

class personPanelCompo(wx.Panel):
    def __init__(self,parent,ID,mode=0):
        wx.Panel.__init__(self,parent,ID)
        self.shape = 0
        self.canvas = 0
        self.parentFrame = 0
        
        self.sexes = ["男","女"]
        self.affs = ["健康","発症","キャリア","無症候キャリア"]
        self.stats = ["生存","死亡"]
        self.sexSelector = wx.Choice(self,-1,choices=self.sexes)
        self.statusSelector = wx.Choice(self,-1,choices=self.stats)
        self.affSelector = wx.Choice(self,-1,choices=self.affs)
        self.ageControl = wx.SpinCtrl(self, -1,"0")
        self.ageUnitSelector = wx.Choice(self,-1,choices=["歳","ヶ月"])
        self.markCheckbox = wx.CheckBox(self, -1, "マーク")
        self.adoptedCheckbox = wx.CheckBox(self,-1,"")
            ######
        #self.ageSizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.ageSizer.Add
        component = [
                [self.sexSelector,"性別"],
                [self.statusSelector,"状態"],
                [self.affSelector,"キャリアの有無"],
                [self.ageControl,"年齢"],
                [self.ageUnitSelector,"年齢の単位"],
                [self.markCheckbox,"発端者か相談者を表す矢印"],
                [self.adoptedCheckbox,"養子"]
        ]
        #self.sizer2 = wx.GridSizer(len(component),2,10,0)
        self.sizer2 = wx.BoxSizer(wx.VERTICAL)
        for widget,label in component:
            self.sizer2.Add(wx.StaticText(self, -1, label))
            self.sizer2.Add(widget,flag=wx.ALIGN_RIGHT)
            self.sizer2.Add(wx.StaticLine(self), flag=wx.EXPAND)
            
        self.plusButton = wx.Button(self, -1, "+")
        self.plusButton.Bind(wx.EVT_BUTTON,self.addDctrl)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sizer2,flag=wx.EXPAND)
        self.sizer.Add(wx.StaticText(self, -1, "既往症"))
        self.sizer.Add(self.plusButton)
        self.dSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.dSizer,flag=wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)
        self.dCtrl = []
        
        if mode == 0:
            self.createButton = wx.Button(self, -1, "作成")
            self.sizer.Add(self.createButton,flag=wx.ALIGN_CENTER)
        elif mode == 1:
            self.editButton = wx.Button(self, -1, "確定")
            self.sizer.Add(self.editButton,flag=wx.ALIGN_CENTER)
            
        self.SetSizer(self.sizer)
        
    def dctrlUpdate(self):
        self.dSizer.Layout()
        self.sizer.Layout()
        if self.parentFrame != 0:
            self.parentFrame.sizer.Layout()
        
    def addDctrl(self,event):
        if len(self.dCtrl) < 10:
            self.dCtrl.append([wx.SpinCtrl(self, -1,"0"),wx.TextCtrl(self,-1,"既往症"),wx.Button(self, -1, "-")])
            last = self.dCtrl[-1]
            s = wx.BoxSizer(wx.HORIZONTAL)
            s.Add(last[0])
            s.Add(last[1])
            s.Add(last[2])
            last[2].Bind(wx.EVT_BUTTON,self.deleteDCtrl)
            self.dSizer.Add(s)
            self.dctrlUpdate()
    
    def deleteDCtrl(self,event):
        button = event.GetEventObject()
        for dctrl in self.dCtrl:
            if button in dctrl:
                index = self.dCtrl.index(dctrl)
                self.dSizer.Remove(index)
                for obj in dctrl:
                    obj.Destroy()
                del self.dCtrl[index]
        self.dctrlUpdate()
    
    def setDctrlbyList(self,dlist):
        if len(dlist) > 0:
            for yr,di in dlist:
                self.addDctrl(None)
                last = self.dCtrl[-1]
                last[0].SetValue(yr)
                last[1].SetValue(di)
            self.Refresh(eraseBackground=False)
            return True
        else:
            return False
        
    def getDList(self):
        dlist = []
        for yr,di,_ in self.dCtrl:
            li = []
            li.append(yr.GetValue())
            li.append(di.GetValue())
            dlist.append(li)
        return dlist
        
class addPersonPanel(personPanelCompo):
    def __init__(self,parent,ID):
        personPanelCompo.__init__(self,parent,ID,0)
        self.createButton.Bind(wx.EVT_BUTTON,self.createChild)
       
    def setCanvas(self,canvas):
        self.canvas = canvas
        return True
    
    def createChild(self,event):        
        sex = self.sexSelector.GetSelection()
        statType = self.statusSelector.GetSelection()
        ageUnit = self.ageUnitSelector.GetSelection()
        affType = self.affSelector.GetSelection()
        age = int(self.ageControl.GetValue())
        isMarked = self.markCheckbox.GetValue()
        isAdopted = self.adoptedCheckbox.GetValue()
        diseaseList = self.getDList()
        info = chikuwa.infoContainer(sex=sex,
                                       age=age,
                                       ageUnit=ageUnit,
                                       statType=statType,
                                       affType=affType,
                                       isMarked=isMarked,
                                       isAdopted=isAdopted,
                                      diseaseList=diseaseList
                                      )
        self.canvas.addPersonByController(info)
        return True
    
class babyPanelCompo(wx.Panel):
    def __init__(self,parent,ID,mode=0):
        wx.Panel.__init__(self,parent,ID)
        self.shape = 0
        self.canvas = 0
        self.sexes = ["男","女"]
        self.affs = ["健康","罹患"]
        self.stats = ["自然流産","妊娠中絶","子宮外妊娠","死産","妊娠"]
        
        self.sexSelector = wx.Choice(self,-1,choices=self.sexes)
        self.statusSelector = wx.Choice(self,-1,choices=self.stats)
        self.affSelector = wx.Choice(self,-1,choices=self.affs)
        self.ageControl = wx.SpinCtrl(self, -1,"0")
        self.footerControl = wx.TextCtrl(self,-1,"",style=wx.TE_MULTILINE)
        
        
        component = [
                [self.sexSelector,"性別"],
                [self.statusSelector,"状態"],
                [self.affSelector,"健康状態"],
                [self.ageControl,"週数"],
                [self.footerControl,"備考欄"],
        ]
        self.sizer2 = wx.BoxSizer(wx.VERTICAL)
        for widget,label in component:
            self.sizer2.Add(wx.StaticText(self, -1, label))
            self.sizer2.Add(widget,flag=wx.ALIGN_RIGHT)
            self.sizer2.Add(wx.StaticLine(self),flag=wx.EXPAND)
        ######
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sizer2,flag=wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)        
        if mode == 0:
            self.createButton = wx.Button(self, -1, "作成")
            self.sizer.Add(self.createButton,flag=wx.ALIGN_CENTER)
        elif mode == 1:
            self.editButton = wx.Button(self, -1, "確定")
            self.sizer.Add(self.editButton,flag=wx.ALIGN_CENTER)
            
        self.SetSizer(self.sizer)
        
class addPreNotCTPanel(babyPanelCompo):
    def __init__(self,parent,ID):
        babyPanelCompo.__init__(self,parent,ID,0)
        self.canvas = 0
        self.createButton.Bind(wx.EVT_BUTTON,self.createChild)
        
    def setCanvas(self,canvas):
        self.canvas = canvas
        return True
    
    def createChild(self,event):
        sex = self.sexSelector.GetSelection()
        statType = self.statusSelector.GetSelection()
        affType = self.affSelector.GetSelection()
        age = self.ageControl.GetValue()
        footer = self.footerControl.GetValue()
        info = chikuwa.infoBabyContainer(sex=sex,age=age,statType=statType,footer=footer,affType=affType)
        self.canvas.addPreNotCTByController(info)
    
class SubFrame(wx.Panel):
    def __init__(self,parent,ID):
        wx.Panel.__init__(self,parent,ID)
        self.canvas = 0
        self.masterNote = wx.Notebook(self,-1)
        self.notebook = wx.Notebook(self.masterNote,-1)
        self.panel1_1 = addPersonPanel(self.notebook,-1)
        self.panel1_2 = addPreNotCTPanel(self.notebook,-1)
        self.notebook.InsertPage(0,self.panel1_1,"通常")
        self.notebook.InsertPage(1,self.panel1_2,"妊娠/妊娠中/死産")
        self.panel2_1 = textNewControllerPanel(self.masterNote,-1)
        self.masterNote.InsertPage(0,self.notebook,"人物")
        self.masterNote.InsertPage(1,self.panel2_1,"文字")
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.masterNote,flag=wx.GROW)
        self.SetSizer(self.sizer)
        
    def setCanvas(self,canvas):
        self.canvas = canvas
        self.panel1_1.setCanvas(canvas)
        self.panel1_1.parentFrame = self
        self.panel1_2.setCanvas(canvas)
        self.panel2_1.setCanvas(canvas)
        return True
        
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,-1,'Test',size=(int(MAX_WIDTH*4/3),MAX_HEIGHT))
        self.InitialiseComponents()
    def InitialiseComponents(self):
        base = wx.Panel(self)
        toolbar = leftPanel(base,-1)
        canvas = testCanvas(base,-1)
        subframe = SubFrame(base,-1)
        subframe.setCanvas(canvas)
        toolbar.setCanvas(canvas)
        toolbar.setController(subframe)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(toolbar,0,wx.EXPAND)
        sizer.Add(canvas,4,wx.EXPAND)
        sizer.Add(subframe,0,wx.EXPAND)
        
        base.SetSizer(sizer)
        
if __name__ == "__main__":
    app = wx.App()
    """
    def onSize(event,panel=window,canvas=canvas):
        canvas.SetSize(panel.GetSize())
    
    #window.Bind(wx.EVT_SIZE,onSize)
    
    #window.Show()
    """
    
    MainFrame().Show(True)
    app.MainLoop()