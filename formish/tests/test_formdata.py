from formish import *
from schemaish import *
import unittest


class TestFormData(unittest.TestCase):
    """Build a Form and test that it doesn't raise exceptions on build and that the methods/properties are as expected"""

    name='nested'
    schema_nested = Structure([
        ("one", Structure([
            ("a", String(validator=NotEmpty, 
                description="This is a field with name a and title A and has a NotEmpty validator")),
            ("b", String(title='bee')),
            ("c", Structure([("x", String()),("y", String())])),
            ])
         ),
        ])      
    
    def test_titles(self):

        form = Form(self.schema_nested, self.name)
        form['one']['b'].title = 8
        assert form['one']['b'].title == 8
        assert form['one.b'].title == 8
        form['one.c']['x'].title = 6
        assert form['one.c.x'].title == 6
        
        
        
if __name__ == '__main__':
    unittest.main()