from pywinauto import Application, timings
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_element_info import UIAElementInfo
from pywinauto.uia_defines import IUIA
from pywinauto.uia_defines import get_elem_interface
import time
import comtypes.client
from comtypes.gen.UIAutomationClient import IUIAutomation, TreeScope_Descendants
from datetime import datetime
import csv
from pathlib import Path


def find_element_fast(root_element, automation_id, found_index=0):
    """
    Fast element search using direct UIA API
    10x faster than pywinauto's window() search
    """
    uia = comtypes.client.GetModule('UIAutomationCore.dll')
    iuia = comtypes.client.CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=IUIAutomation)
    
    condition = iuia.CreatePropertyCondition(30011, automation_id)  # AutomationId
    
    if found_index == 0:
        # Just find first
        element = root_element.FindFirst(TreeScope_Descendants, condition)
        return UIAWrapper(UIAElementInfo(element)) if element else None
    else:
        # Find all and return specific index
        elements_array = root_element.FindAll(TreeScope_Descendants, condition)
        if found_index < elements_array.Length:
            element = elements_array.GetElement(found_index)
            return UIAWrapper(UIAElementInfo(element))
        return None

def find_element_by_title(root_element, title):
    """Fast search by title/name"""
    uia = comtypes.client.GetModule('UIAutomationCore.dll')
    iuia = comtypes.client.CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=IUIAutomation)
    
    condition = iuia.CreatePropertyCondition(30005, title)  # Name property
    element = root_element.FindFirst(TreeScope_Descendants, condition)
    return UIAWrapper(UIAElementInfo(element)) if element else None

class Button_Repository:
    def __init__(self):
        # Connect once and reuse the app connection
        self.app = Application(backend="uia").connect(auto_id="frmOrpheus")
        # Get root element for fast searches
        self.root = self.app.top_window().element_info.element

    def Surface_Weight_Button(self):
        Surface_Weight_Button_Element = find_element_fast(self.root, "optSW")
        Surface_Weight_Button_Element.click_input()

    def Surface_Weight_Button_Value(self,value):
        SW_Pane = find_element_fast(self.root, "txtSW")
        SW_Value_Element = find_element_fast(SW_Pane.element_info.element, "txtData")
        SW_Value_Element.click_input()
        SW_Value_Element.type_keys("^a")  # Select all
        SW_Value_Element.type_keys(str(value))

    def Refresh(self):
        Refresh_Button = find_element_fast(self.root, "btnRefresh")
        Refresh_Button.click_input()


    def Bypass_Warning_Button(self):
        Bypass_Warning_Button1=find_element_fast(self.root, "btnOK")
        self.Bypass_Warning_Button1=Bypass_Warning_Button1

        self.Bypass_Warning_Button1.click_input()

        # Connect once and reuse the app connection
        self.app2 = Application(backend="uia").connect(auto_id="frmOrpheus")
        # Get root element for fast searches
        self.root2 = self.app2.top_window().element_info.element

        Bypass_Warning_Button2=find_element_fast(self.root2, "cmdOK")
        self.Bypass_Warning_Button2=Bypass_Warning_Button2

        self.Bypass_Warning_Button2.click_input()

    def FOE_Value(self):
        FOE_Button_Pane = find_element_fast(self.root, "txtFOE")
        FOE_Button_Element = find_element_fast(FOE_Button_Pane.element_info.element, "txtData")
        return FOE_Button_Element.get_value()
    
    def Depth_Value(self,value):
        Depth_Button_Pane = find_element_fast(self.root, "txtDepth")
        Depth_Button_Element = find_element_fast(Depth_Button_Pane.element_info.element, "txtData")
        Depth_Button_Element.click_input()
        Depth_Button_Element.type_keys("^a")  # Select all
        Depth_Button_Element.type_keys(value)

    def Depth_Value_get(self):
        Depth_Button_Pane = find_element_fast(self.root, "txtDepth")
        Depth_Button_Element = find_element_fast(Depth_Button_Pane.element_info.element, "txtData")
        return Depth_Button_Element.get_value()

    def Surface_Load(self):
        """Read the current surface load value"""
        Surface_Load_Pane = find_element_fast(self.root, "txtSW")
        Surface_Load_Element = find_element_fast(Surface_Load_Pane.element_info.element, "txtData")
        return Surface_Load_Element.get_value()
    
    def WOB_input_box(self, value):
        """Set WOB (Weight on Bit) value"""
        WOB_Pane = find_element_fast(self.root, "txtWOB")
        WOB_Element = find_element_fast(WOB_Pane.element_info.element, "txtData")
        WOB_Element.click_input()
        WOB_Element.type_keys("^a")  # Select all
        WOB_Element.type_keys(value)
    
    def Bottom_Up_Button(self):
        """Click the Bottom Up button to recalculate"""
        Bottom_Up_Button = find_element_fast(self.root, "optBU")
        Bottom_Up_Button.click_input()


if __name__ == "__main__":
    repo = Button_Repository()
    #repo.Surface_Weight_Button()
    repo.Surface_Weight_Button_Value(142000)
    repo.Refresh()
    # repo.Bypass_Warning_Button()
    # repo.FOE_Value()
    # print(repo.FOE_Value())
    #repo.Depth_Value(5000)