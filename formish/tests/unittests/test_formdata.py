import pdb
import validatish
from formish import *
from schemaish import *
import unittest


class TestFormData(unittest.TestCase):
    """Build a Simple Form and test that it doesn't raise exceptions on build and that the methods/properties are as expected"""

    schema_nested = Structure([
        ("one", Structure([
            ("a", String(validator=validatish.Required(), 
                description="This is a field with name a and title A and has a Required validator")),
            ("b", String(title='bee')),
            ("c", Structure([("x", String(title='cee')),("y", String())])),
            ])
         ),
        ])      

    
    def test_titles(self):

        form = Form(self.schema_nested, 'nested')

        assert form['one.b'].title == 'bee'
        assert form['one.c.x'].title == 'cee'
        form['one.b'].title = 'bee bee cee'
        assert form['one.b'].title == 'bee bee cee'
        form['one.c.x'].title = 'bee bee cee'
        assert form['one.c.x'].title == 'bee bee cee'

    def test_widgets(self):

        form = Form(self.schema_nested, 'nested')

        assert isinstance(form['one.a'].widget,Input)
        form['one.a'].widget = TextArea()
        assert isinstance(form['one.a'].widget,TextArea)

    def test_description(self):

        form = Form(self.schema_nested, 'nested')

        assert form['one.a'].description == "This is a field with name a and title A and has a Required validator"
        form['one.a'].description = "This is a new description"
        assert form['one.a'].description == "This is a new description"

    def test_value(self):

        form = Form(self.schema_nested, 'nested')
        self.assertRaises(KeyError, setattr, form['one.a'], 'value', 7)



class TestSequenceFormData(unittest.TestCase):

    schema = Structure()
    schema.add('a',Sequence(String(title='bee')))


    def test_widgets(self):
        form = Form(self.schema, 'sequences')
        form.defaults = {'a': ['1','2']}
        assert isinstance(form['a.0'].widget,Input)
        form['a.*'].widget = TextArea()
        assert isinstance(form['a.0'].widget,TextArea)
        

    def test_widgets_before_data(self):
        form = Form(self.schema, 'sequences')
        form['a.*'].widget = TextArea()
        form.defaults = {'a': ['1','2']}
        assert isinstance(form['a.0'].widget,TextArea)



        
        
if __name__ == '__main__':
    unittest.main()
