# coding=utf-8
from __future__ import print_function

import os
import os.path

 
TypeEnum = {'TypeAnd': 'and', 'TypeOr': 'or', 'TypeTrueN': 'true', 'TypeNode': 'node', 'TypeNode_NEG': 'not'}


class DestCode(object):
    def __init__(self, isOfficial):
        self.code_list = []
        self.isOfficial = isOfficial
        self.index = 0

    def append(self, code, comment=""):
        if not self.isOfficial:
            code += comment
        self.code_list.append(code)

    def clear(self, isOfficial):
        self.code_list = []
        self.isOfficial = isOfficial
        self.index = 0

    def applyIndex(self):
        self.index += 1
        return self.index

class CodeGenExtendPoint(object):
    @staticmethod
    def genForNode(destnode, node_name):
        # you can modify anything here
        destnode.append("r0%s" % node_name)
        # destnode.append("calc_and_push_for_node%s" % node_name)
        """
        if('!!' in self.value): 
            ch = self.value.split('!!')[-1]
            GlobalDestCode.append("r0%s is(0) " %ch)
        else:
            GlobalDestCode.append("r0%s" %self.value)
        """


path_onechar = []
path_multichars = {}


def writelist2file(list1, filename):
    if list1:
        handle = open(filename, 'a+')  
        for each in list1:            
            handle.write(each)
            handle.write('\r\n')
        handle.close()
    return True
        

def writestr2file(s, filename='ptnsrc.txt'):
    if s:
        handle = open(filename, 'a+')  
        handle.write(s)
        handle.close()
    return True
    

class Stream:
    def __init__(self, lst):
        self.items = lst

    def read(self):
        a = self.items[0]
        self.items.pop(0)
        return a        

    def show(self):
        print(self.items)


class Tree(object): 
    def __init__(self, t, value, left, right, next=None):
        self.type = t
        self.value = value  
        
        self.leftChild = left
        self.rightChild = right
        self.next = next        
                
    def show(self, tab=1):
        if tab == 1:
            print("\n===========show Tree Begin========")
            print("Tree: %s" % self.expr())
        tabstr = "    "*tab
        if self.type == "and" or self.type == "or":
            self.leftChild.show(tab+1)
            print("%s%s" % (tabstr, self.type))
            self.rightChild.show(tab+1)
        if self.type == "true":
            print("%sTrue(%s)" % (tabstr, self.value))
            temp = self.leftChild
            while temp:
                temp.show(tab+1)
                temp = temp.next
        elif self.type == "node":
            print("%s'%s'" % (tabstr, self.value))
        if tab == 1:
            print("\n===========show Tree End  ========")
   
    def getcharpath(self, nodelist):   
        global path_onechar 
        global path_multichars 
        for each in nodelist:
            path_onechar = []
            self.searchpath(1, each)
            print(path_onechar)            
            path_multichars[each] = [] 
            path_multichars[each].extend(path_onechar)
        return path_multichars
        
    def searchpath(self, tab, nodechar):
        global path_onechar         
        if tab == 1:
            print("\n===========show searchpath Begin========")
            print("Tree: %s" % self.expr())
        tabstr = "    "*tab
        if self.type == "and" or self.type == "or":           
            print("%s%s" % (tabstr, self.type))
            path_onechar.append(self.type)
            self.leftChild.searchpath(tab+1, nodechar)
            self.rightChild.searchpath(tab+1, nodechar)
        if self.type == "true":
            temp = self.leftChild
            while temp:
                if temp.value == nodechar:
                    print("%sTrue(%s)" % (tabstr, self.value))
                    path_onechar.append("True(%s)" % self.value)
                temp.searchpath(tab+1, nodechar)
                temp = temp.next
        elif self.type == "node":
            if self.value == nodechar:
                print("%s'%s'" % (tabstr, self.value))
                path_onechar.append(self.value)
                tab = 1
                return 
        if tab == 1:
            print("\n===========show searchpath End  ========")

    def expr(self):
        if self.type == "and":
            return "("+self.leftChild.expr() + ")&(" + self.rightChild.expr() + ")"
        elif self.type == "or":
            return "("+self.leftChild.expr() + ")|(" + self.rightChild.expr() + ")"
        elif self.type == "true":
            tmpstr = "True(" + str(self.value)
            temp = self.leftChild
            while temp:
                tmpstr = tmpstr + "," + temp.expr()
                temp = temp.next
            return tmpstr+")"
        elif self.type == "node":
            return self.value
        return "?"

    def add(self, p):
        if self.leftChild:
            temp = self.leftChild
            while temp.next:
                temp = temp.next
            temp.next = p
        else:
            self.leftChild = p
        return self

    # myFatherHaveToldMeTheLabelId： If not 0, means that the parent function has created a labelId.
    def Traverse(self, destCode, myFatherHaveToldMeTheLabelId):
        if self.type == TypeEnum['TypeAnd'] or self.type == TypeEnum['TypeOr']:
            self.genCodeForAndOr(destCode, myFatherHaveToldMeTheLabelId)
        elif self.type == TypeEnum['TypeTrueN']:
            self.genCodeForTrueN(destCode, myFatherHaveToldMeTheLabelId)
        elif self.type == TypeEnum['TypeNode']:
            self.genCodeForNode(destCode)
        else:
            print('something error')

    def genCodeForNode(self, destCode):
        CodeGenExtendPoint.genForNode(destCode, self.value)

    def genCodeForAndOr(self, destCode, myFatherHaveToldMeTheLabelId):
        if myFatherHaveToldMeTheLabelId > 0:  # If label_id is assigned by my parents, then follow it.
            tmp_index = myFatherHaveToldMeTheLabelId
        else:
            tmp_index = destCode.applyIndex()  # otherwise build a label_id

        # if my left child tree is and same with me, then set my index id to left child tree
        if self.leftChild.type == self.type:
            self.leftChild.Traverse(destCode, tmp_index)
        else:
            self.leftChild.Traverse(destCode, 0)
        if self.type == TypeEnum['TypeAnd']:
            destCode.append(" jne(1) LABEL%d  " % tmp_index,
                                  "; if %s not true, need not to do %s, so goto LABEL%d"
                                  % (self.leftChild.expr(), self.rightChild.expr(), tmp_index))
        else:  # self.type == TypeEnum['TypeOr']:
            destCode.append(" je(1) LABEL%d   " % tmp_index,
                                  "; if %s is true, need not to do %s, so goto LABEL%d"
                                  % (self.leftChild.expr(), self.rightChild.expr(), tmp_index))

        #destCode.append("pop\n")

        if self.rightChild.type == self.type:  # if my  right child tree is "and" same with me, then set my index id to right child tree
            self.rightChild.Traverse(destCode, tmp_index)
        elif self.rightChild.type == TypeEnum["TypeTrueN"]:
            self.rightChild.Traverse(destCode, tmp_index)
        else:
            self.rightChild.Traverse(destCode, 0)
        if not myFatherHaveToldMeTheLabelId:  # If no parent set label_id, use my own
            destCode.append("\r\n:LABEL%d     " % tmp_index,
                                  "; finish calc: %s" % self.expr())

    def genCodeForTrueN(self, destCode, myFatherHaveToldMeTheLabelId):
        tmp_index = destCode.applyIndex()
        if myFatherHaveToldMeTheLabelId:
            tmp_index2 = myFatherHaveToldMeTheLabelId
        else:
            tmp_index2 = destCode.applyIndex()
        tmp = 0
        temp = self.leftChild
        pre_value = temp.value
        pre_temp = temp
        i = 0
        while temp:
            pre_value1 = pre_temp.value
            pre_temp = temp
            print("i:%d,pre_value1:%s" % (i, pre_value1))
            temp.Traverse(destCode, 0)
            if temp.next is None:
                destCode.append(" r0%s +  w0%s je(%s) LABEL%s" % (pre_value1, temp.value, self.value, tmp_index))
                break
            pre_value2 = temp.value
            temp = temp.next
            tmp += 1
            print("i:%d,pre_value2:%s" % (i, pre_value2))
            if temp == self.leftChild.next:
                print("no need to check first return value")
            elif temp is not None:
                destCode.append(" r0%s +  w0%s je(%s) LABEL%s" % (pre_value1, pre_value2, self.value, tmp_index))
            i += 1
        destCode.append(" push(0)     ",
                              ";result is false: %s" % self.expr())
        destCode.append(" goto LABEL%d" % tmp_index2)
        destCode.append("\r\n:LABEL%d     " % tmp_index,
                              ";result is true: %s" % self.expr())
        destCode.append(" push(1)")
        if not myFatherHaveToldMeTheLabelId:
            destCode.append("\r\n:LABEL%d    " % tmp_index2,
                                  "; finish calc: %s" % self.expr())

    def genCodeForTrueN2(self, destCode, myFatherHaveToldMeTheLabelId):
        tmp_index = destCode.applyIndex()
        tmp_index2 = destCode.applyIndex()
        if myFatherHaveToldMeTheLabelId:
            tmp_index2 = myFatherHaveToldMeTheLabelId
        else:
            tmp_index2 = destCode.applyIndex()

        temp = self.leftChild
        num = 0
        while temp:
            num += 1
            temp.Traverse(destCode, 0)
            if num > 1:
                destCode.append(" + je(%d) MY_LABEL_%d \n" % (self.value, tmp_index))
            temp = temp.next

        destCode.append("pop push(0) goto MY_LABEL_%d" % tmp_index2)
        destCode.append("")
        destCode.append(":MY_LABEL_%d    " % tmp_index)
                        #"; finish calc: %s" % self.expr())
        destCode.append("pop push(1)\n")

        #destCode.append(":MY_LABEL_%d    " % tmp_index2,
        #                "; finish calc: %s" % self.expr())

        if not myFatherHaveToldMeTheLabelId:
            destCode.append(":LABEL%d    " % tmp_index2,
                            "; finish calc: %s" % self.expr())

    def Go(self, destCode):
        self.Traverse(destCode, 0)
        destCode.append(" jne(1) END")

        '''destCode.append("\r\n:FOUND")
        destCode.append("       FeedbackFile ")
        destCode.append("       vs(1)")
        destCode.append("       ;vy ")
        destCode.append(" :END ")
        destCode.append("       vn")'''



class ParseLogic(object):
    def __init__(self):          
        self.logic_list = []
        self.input_list = []
        self.return_result = {'result': False, 'msg': ''}
        self.local_logicfile = 'ptnsrc.txt'
        self.input_list = []
        self.char_path = {}
        if os.path.exists(self.local_logicfile):
            os.remove(self.local_logicfile)
    
    def And(self, left, right):        
        return Tree(TypeEnum['TypeAnd'], '', left, right)
    
    def Or(self, left, right):        
        return Tree(TypeEnum['TypeOr'], '', left, right)
   
    def TrueN(self, TrueCount):
        return Tree(TypeEnum['TypeTrueN'], TrueCount, None, None)
                
    def Node(self, value):
        return Tree(TypeEnum['TypeNode'], value, None, None)
    
    def AndOr(self, op, l, r):
        if op == '&':
            return self.And(l, r)
        elif op == '|':
            return self.Or(l, r)
        return None
    
    def parse_input(self, myinput):
        temp_str = ""
        myinput = "(" + myinput + ")"
        # self.input_list.append('(')
        for ch in myinput:
            if ch == ' ' or ch == ',':
                if temp_str:
                    self.input_list.append(temp_str)
                    temp_str = ""
            elif ch == '&' or ch == '|' or ch == '(' or ch == ')':
                if temp_str:
                    self.input_list.append(temp_str)
                    temp_str = ""
                self.input_list.append(ch)
            else:
                temp_str += ch
        # self.input_list.append(')')

        print("original input: %s" % myinput)       
        for ch in self.input_list:
            print(ch, end=' ')
        # raw_input('Complete parse_input')
        return self.input_list
    
    def showParse2Log(self, lst, index, stackOpr, stackArg):
        print("[Proc]", end="")
        pos = 6
        for i, word in enumerate(lst):
            if i == index:
                print(word)
                break
            elif i < index:
                print(word, end=" ")
                pos += len(word)+1
        print("%s^" % (" "*pos))

        print("the stackOpr is: ", end="")
        for one in stackOpr:
            print(one, end=" ")
        print("\nthe stackArg is: ", end="")
        for one in stackArg:
            if isinstance(one, Tree):
                if one.type == TypeEnum["TypeNode"]:
                    print(one.value, end=" ")
                else:
                    print(one.type, end=" ")
            else:
                print(one, end=" ")
        print("\n")
   
    def parse2(self, lst, islog):
        stackOpr = []
        stackArg = []
        for index, word in enumerate(lst):
            if word == '(':
                stackOpr.append(word)
            elif word == '&' or word == '|':
                lastOpr = stackOpr[-1]
                if lastOpr == '&' or lastOpr == '|':
                    arg2 = stackArg.pop()
                    arg1 = stackArg.pop()
                    stackOpr.pop()
                    stackOpr.append(word)
                    stackArg.append(self.AndOr(lastOpr, arg1, arg2))
                elif lastOpr == '(' or lastOpr == 'True':
                    stackOpr.append(word)
            elif word == ')':
                lastOpr = stackOpr.pop()
                if lastOpr == '&' or lastOpr == '|':
                    arg2 = stackArg.pop()
                    arg1 = stackArg.pop()
                    stackOpr.pop()  # for '('
                    stackArg.append(self.AndOr(lastOpr, arg1, arg2))
                elif lastOpr == '(':
                    lastOpr2 = None
                    if stackOpr:
                        lastOpr2 = stackOpr.pop()

                    if lastOpr2 == "True":
                        arg = stackArg.pop()
                        arg_list = []
                        while isinstance(arg, Tree):
                            arg_list.insert(0, arg)
                            arg = stackArg.pop()
                        num = int(arg)
                        tree = self.TrueN(num)
                        for one in arg_list:
                            tree.add(one)
                        stackArg.append(tree)
            elif word == "True":
                stackOpr.append(word)
            else:
                if word.isdigit():
                    stackArg.append(word)
                else:
                    stackArg.append(self.Node(word))
            if islog:
                self.showParse2Log(lst, index, stackOpr, stackArg)
        # raw_input('Complete parse2')
        return stackArg[0]        

    def get_ptnlogic(self, input_str, is_official=0):
        # is_official: 0-has comments, 1-no comments in pattern source

        self.parse_input(input_str)
        
        node_list = []
        for each in self.input_list:
            each = each.strip(' ')
            if each not in ['(', ')', '&', '|', '!!', 'True']:
                if not each.isdigit() and len(each):
                    node_list.append(each)      
        try:
            # global INDEX
            # INDEX = 0
            # tree2 = Tree()
            tree2 = self.parse2(self.input_list, True)            
            tree2.show(1)            
            self.char_path = tree2.getcharpath(node_list)
            # print(self.char_path)
            destCode = DestCode(is_official)
            tree2.Go(destCode)
            for key in destCode.code_list:
                self.logic_list.append(key)
            self.return_result['result'] = True
            self.return_result['ptnlogic'] = self.logic_list
            self.return_result['charpath'] = self.char_path
            return self.return_result
        except Exception as e:
            print("exception %s" % str(e))
            self.return_result['msg'] = "exception %s" % str(e)
            raise
            #return self.return_result

                        
if __name__ == "__main__":        
    """
    #original check
    #detection_logic1 = "[and, and, A, True,2,3,B,C, D, and, E, or, F, G]
    #ret = ph.get_ptnlogic(detection_logic1)
    #if(ret['result']):
        #for key in  ret['ptnlogic']:
            #print key        
    """  
    # detection_logic1 = "A&B&C&True(2,E,F,G)"
    TestCase = []
    TestCase.append("A & B & True(2, C, D, E) & !!F")
    TestCase.append("A&B&C&D&E")
    TestCase.append("A&B&C&!!D")
    TestCase.append("True(3,A,B,C,D)")
    TestCase.append("A&B&C&True(2,D,E,F) & (G|H|I) &(K|L)")
    TestCase.append("True(2,A,B,True(3, C,D,E,F), True(2,G,H,I))")
    """    
    TestCase.append("A&B&C&D&E")
    TestCase.append("A&B&C&!!H")   
    TestCase.append("A&B&C&True(2,E,F,G) & (H|I|J) &(K|L)")
    TestCase.append("A&B&C&True(2,E,F,G)")
    TestCase.append("A&B&C&True(2,E,F,G) &H")
    TestCase.append("True(2,E,F,G)")
    TestCase.append("True(3,E,F,G,H)")
    TestCase.append("True(2,E,F,True(3, A,B,C,D), True(2,G,H,I))")  

    TestCase.append("True(2,A,B,C,D)&E&F&G")
    TestCase.append("True(2,A,B,C,D)|E|F|G")
    
    TestCase.append("A|True(2,D,E,F)")
    TestCase.append("A&True(2,D,E,F)")  
    TestCase.append("True(2,A,B,C, True(2,D,E,F))")
    """

    for i in range(0, len(TestCase)):
        filename = 'ptnsrc'+str(i)+'.txt' 
        if os.path.exists(filename):        
            os.remove(filename)
    for i in range(0, len(TestCase)):
        ph = ParseLogic() 
        tmp_input = TestCase[i]
        print("Try to handle %s" % tmp_input)
        ResultList = []
        ret = ph.get_ptnlogic(tmp_input, 0)
        if ret['result']:
            ResultList = ret['ptnlogic']
            dictList = ret['charpath']
            filename = 'ptnsrc'+str(i)+'.txt'            
            writestr2file(";%s\r\n" % tmp_input, filename)
            writelist2file(ResultList, filename)
            writestr2file(str(dictList), filename)
        # raw_input("Complete to handle %s" %tmp_input)

