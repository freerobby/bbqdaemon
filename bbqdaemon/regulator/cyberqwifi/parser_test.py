import os
import unittest

status_xml = """
<nutcstatus>
   <!--all temperatures are displayed in tenths F, regardless of setting of unit-->
   <!--all temperatures sent by browser to unit should be in F.  you can send tenths F with a decimal place, ex: 123.5-->  
   <OUTPUT_PERCENT>0</OUTPUT_PERCENT>
   <TIMER_CURR>00:00:00</TIMER_CURR>
   <COOK_TEMP>OPEN</COOK_TEMP>
   <FOOD1_TEMP>OPEN</FOOD1_TEMP>
   <FOOD2_TEMP>OPEN</FOOD2_TEMP>
   <FOOD3_TEMP>OPEN</FOOD3_TEMP>
   <COOK_STATUS>4</COOK_STATUS>
   <FOOD1_STATUS>4</FOOD1_STATUS>
   <FOOD2_STATUS>4</FOOD2_STATUS>
   <FOOD3_STATUS>4</FOOD3_STATUS>
   <TIMER_STATUS>0</TIMER_STATUS>
   <DEG_UNITS>0</DEG_UNITS>
   <COOK_CYCTIME>6</COOK_CYCTIME>
   <COOK_PROPBAND>300</COOK_PROPBAND>
   <COOK_RAMP>0</COOK_RAMP>
</nutcstatus>
"""

class TestParser(unittest.TestCase):
    def test_parse_status_xml(self):
        from bbqdaemon.regulator.cyberqwifi import parser
        data = parser(status_xml)
        self.assertEqual(len(data), 15)
        self.assertTrue('COOK_TEMP' in data)
        self.assertEqual(data['COOK_TEMP'], "OPEN")
        self.assertTrue('COOK_STATUS' in data)
        self.assertEqual(data['COOK_STATUS'], "ERROR")
