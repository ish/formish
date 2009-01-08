import validatish
import formish
import schemaish
import unittest


class TestFormData(unittest.TestCase):
    """Build a Simple Form and test that it doesn't raise exceptions on build and that the methods/properties are as expected"""

    schema_nested = schemaish.Structure([
        ("one", schemaish.Structure([
            ("a", schemaish.String(validator=validatish.Required(), 
                description="This is a field with name a and title A and has a Required validator")),
            ("b", schemaish.String(title='bee')),
            ("c", schemaish.Structure([("x", schemaish.String(title='cee')),("y", schemaish.String())])),
            ])
         ),
        ])      

    
    def test_titles(self):

        form = formish.Form(self.schema_nested, 'nested')

        assert form['one.b'].title == 'bee'
        assert form['one.c.x'].title == 'cee'
        form['one.b'].title = 'bee bee cee'
        assert form['one.b'].title == 'bee bee cee'
        form['one.c.x'].title = 'bee bee cee'
        assert form['one.c.x'].title == 'bee bee cee'

    def test_widgets(self):

        form = formish.Form(self.schema_nested, 'nested')

        assert isinstance(form['one.a'].widget.widget,formish.Input)
        form['one.a'].widget = formish.TextArea()
        assert isinstance(form['one.a'].widget.widget,formish.TextArea)

    def test_description(self):

        form = formish.Form(self.schema_nested, 'nested')

        assert str(form['one.a'].description) == "This is a field with name a and title A and has a Required validator"
        form['one.a'].description = "This is a new description"
        assert str(form['one.a'].description) == "This is a new description"

    def test_value(self):

        form = formish.Form(self.schema_nested, 'nested')
        self.assertRaises(KeyError, setattr, form['one.a'], 'value', 7)



class TestSequenceFormData(unittest.TestCase):

    schema = schemaish.Structure()
    schema.add('a',schemaish.Sequence(schemaish.String(title='bee')))


    def test_widgets(self):
        form = formish.Form(self.schema, 'sequences')
        form.defaults = {'a': ['1','2']}
        assert isinstance(form['a.0'].widget.widget,formish.Input)
        form['a.*'].widget = formish.TextArea()
        assert isinstance(form['a.0'].widget.widget,formish.TextArea)
        

    def test_widgets_before_data(self):
        form = formish.Form(self.schema, 'sequences')
        form['a.*'].widget = formish.TextArea()
        form.defaults = {'a': ['1','2']}
        assert isinstance(form['a.0'].widget.widget,formish.TextArea)



        
        
if __name__ == '__main__':
    unittest.main()
