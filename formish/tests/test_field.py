import unittest
import schemaish
from formish.forms import Form



class TestField(unittest.TestCase):

    def test_default_title(self):
        f = Form("form", schemaish.Structure([('one', schemaish.String())]))
        self.assertEquals(f.one.title, "One")
        

    def test_explicit_title(self):
        f = Form("form", schemaish.Structure([('one', schemaish.String(title="Explicit"))]))
        self.assertEquals(f.one.title, "Explicit")        
        

    def test_no_title(self):
        f = Form("form", schemaish.Structure([('one', schemaish.String())]))
        f.one.title = None
        self.assertTrue(f.one.title is None)


if __name__ == '__main__':
    unittest.main()

