# -*- coding: utf-8 -*-
import base
import unittest
import formish
import schemaish
from BeautifulSoup import BeautifulSoup
from datetime import date
import validatish

class TestFormExamples(base.TestCase):

    def test_string_form(self):
        """
        Form with a couple of string fields
        """
        schema = schemaish.Structure()
        schema.add('fieldOne',schemaish.String())
        schema.add('fieldTwo',schemaish.String())

        form_name = 'form_name'
        form = formish.Form(schema, form_name)

        request_data = {'fieldOne':'a','fieldTwo':'b'}
        expected_data = {'fieldOne':'a','fieldTwo':'b'}

        request = self.Request(form_name,request_data)
        data = form.validate(request)
        assert data == expected_data

        form.defaults = request_data
        htmlsoup = BeautifulSoup(form())
        assert htmlsoup.findAll(id='form_name-fieldOne--field')[0]['class'] == 'field form_name-fieldOne type-string widget-input'
        assert htmlsoup.findAll(id='form_name-fieldTwo--field')[0]['class'] == 'field form_name-fieldTwo type-string widget-input'
        assert htmlsoup.findAll(id='form_name-fieldOne')[0]['value'] == 'a'
        assert htmlsoup.findAll(id='form_name-fieldTwo')[0]['value'] == 'b'


    def test_integer_form(self):
        """
        Form with a couple of integer fields
        """
        schema = schemaish.Structure()
        schema.add('fieldOne',schemaish.Integer())
        schema.add('fieldTwo',schemaish.Integer())

        form_name = 'form_name'
        form = formish.Form(schema, form_name)

        request_data = {'fieldOne':'1','fieldTwo':'2'}
        expected_data = {'fieldOne':1,'fieldTwo':2}

        request = self.Request(form_name,request_data)

        data = form.validate(request)
        assert data == expected_data

        form.defaults = expected_data
        htmlsoup = BeautifulSoup(form())
        assert htmlsoup.findAll(id='form_name-fieldOne--field')[0]['class'] == 'field form_name-fieldOne type-integer widget-input'
        assert htmlsoup.findAll(id='form_name-fieldTwo--field')[0]['class'] == 'field form_name-fieldTwo type-integer widget-input'
        assert htmlsoup.findAll(id='form_name-fieldOne')[0]['value'] == '1'
        assert htmlsoup.findAll(id='form_name-fieldTwo')[0]['value'] == '2'
        
    def test_date_form(self):
        """
        Form with a date
        """
        schema = schemaish.Structure()
        schema.add('a',schemaish.Date())

        form_name = 'form_name'
        form = formish.Form(schema, form_name)

        request_data = {'a':'1966-12-18'}
        expected_data = {'a': date(1966,12,18)}

        request = self.Request(form_name,request_data)

        try:
            data = form.validate(request)
        except:
            pass
        assert data == expected_data

        form.defaults = expected_data
        htmlsoup = BeautifulSoup(form())
        assert htmlsoup.findAll(id='form_name-a--field')[0]['class'] == 'field form_name-a type-date widget-input'
        assert htmlsoup.findAll(id='form_name-a')[0]['value'] == '1966-12-18'
        
    def test_date_dateparts_form(self):
        """
        Form with a date
        """
        schema = schemaish.Structure()
        schema.add('a',schemaish.Date())

        form_name = 'form_name'
        form = formish.Form(schema, form_name)
        form['a'].widget = formish.DateParts()

        request = self.Request(form_name,{'a.year': '', 'a.month': '', 'a.day': ''})
        data = form.validate(request)
        assert data == {'a': None}

        request_data = {'a.day':'18', 'a.month':'12','a.year':'1966'}
        expected_data = {'a': date(1966,12,18)}

        request = self.Request(form_name,request_data)
        data = form.validate(request)
        assert data == expected_data

        form.defaults = expected_data
        htmlsoup = BeautifulSoup(form())
        assert htmlsoup.findAll(id='form_name-a--field')[0]['class'] == 'field form_name-a type-date widget-dateparts'
        assert htmlsoup.findAll(id='form_name-a')[0]['value'] == '18'


class TestErrorRendering(base.TestCase):

    def test_simple(self):
        """
        Check simple field templates emit errors correctly.
        """
        self._test(
                schemaish.Structure([
                    ('simple', schemaish.String()),
                    ]),
                'simple')

    def test_structure_error(self):
        """
        Check structure field templates emit errors correctly.
        """
        self._test(
                schemaish.Structure([
                    ('structure', schemaish.Structure([
                        ('string', schemaish.String())]
                        ))
                    ]),
                'structure')

    def test_sequence_error(self):
        self._test(
                schemaish.Structure([
                    ('sequence', schemaish.Sequence(schemaish.String()))
                    ]),
                'sequence')

    def _test(self, schema, attr):
        ERROR_TEXT = '!!!WOOP!!!WOOP!!!WOOP!!!'
        form = formish.Form(schema, errors={attr: validatish.Invalid(ERROR_TEXT)})
        html = form()
        element = BeautifulSoup(html).find(id='%s--field'%(attr.replace('.', '-'),))
        div_error = element.find('div',{'class': 'error'})
        span_error = element.find('span',{'class': 'error'})
        assert div_error or span_error
        if div_error:
            assert div_error.string == ERROR_TEXT 
        if span_error:
            assert span_error.string == ERROR_TEXT 


class TestSequenceDefault(base.TestCase):

    def test_empty_checker(self):
        form = formish.Form(self._schema(),'form')
        form['seq'].widget = formish.SequenceDefault()
        # Structure should be in form ...
        self.assertTrue('seq.0.foo' in form())
        # ... but not in data
        self.assertEquals(form.validate(self.Request('form', {})), {'seq': []})

    def test_min_start_fields_default(self):
        form = formish.Form(self._schema(),'form')
        form['seq'].widget = formish.SequenceDefault()
        html = form()
        self.assertTrue('seq.0.foo' in html)
        self.assertTrue('seq.1.foo' not in html)

    def test_min_start_fields(self):
        for i in range(1, 5):
            form = formish.Form(self._schema(),'form')
            form['seq'].widget = formish.SequenceDefault(min_start_fields=i)
            html = form()
            for num in range(i):
                self.assertTrue('seq.%d.foo'%num in html)
            self.assertEquals(form.validate(self.Request('form', {})), {'seq': []})

    def test_min_start_with_data(self):
        form = formish.Form(self._schema(),'form')
        form['seq'].widget = formish.SequenceDefault()
        form.defaults = {'seq': [{'foo': 'bar'}]}
        html = form()
        self.assertTrue('seq.0.foo' in html)
        self.assertTrue('value="bar"' in html)
        self.assertTrue('seq.1.foo' not in html)

    def test_min_start_min_empty(self):
        form = formish.Form(self._schema(),'form')
        form['seq'].widget = formish.SequenceDefault(min_start_fields=1, min_empty_start_fields=1)
        html = form()
        self.assertTrue('seq.0.foo' in html)
        self.assertTrue('seq.1.foo' not in html)
        form.defaults = {'seq': [{'foo': 'bar'}]}
        html = form()
        self.assertTrue('seq.0.foo' in html)
        self.assertTrue('value="bar"' in html)
        self.assertTrue('seq.1.foo' in html)

    def test_first_entry(self):
        form = formish.Form(self._schema(),'form')
        form['seq'].widget = formish.SequenceDefault(min_start_fields=2)
        self.assertEquals(form.validate(self.Request('form', [('seq.0.foo', 'bar'), ('seq.1.foo', '')])), {'seq': [{'foo': 'bar'}]})

    def test_empty_first_entry(self):
        form = formish.Form(self._schema(),'form')
        form['seq'].widget = formish.SequenceDefault(min_start_fields=2)
        self.assertRaises(formish.FormError, form.validate, self.Request('form', [('seq.0.foo', ''), ('seq.1.foo', 'bar')]))

    def test_unicode_in_template(self):
        # Check that new item template encoding is ok with unicode characters.
        schema = schemaish.Structure([('seq', schemaish.Sequence(schemaish.String()))])
        form = formish.Form(schema)
        form['seq.*'].widget = formish.SelectChoice(options=[('GBP', '£'.decode('utf-8'))])
        form()

    def _schema(self):
        return schemaish.Structure([
                ('seq', schemaish.Sequence(
                    schemaish.Structure([
                        ('foo', schemaish.String(validator=validatish.Required()))
                    ])
                )),
            ])


class TestSelectChoice(base.TestCase):

    def test_default(self):
        form = formish.Form(
            schemaish.Structure([
                ('foo', schemaish.String()),
            ])
        )
        form['foo'].widget = formish.SelectChoice(['a', 'b'])
        self.assertTrue('selected="selected"' not in form())
        form.defaults = {'foo': 'a'}
        self.assertTrue('value="a"  selected="selected"' in form())

    def test_none_option(self):
        form = formish.Form(
            schemaish.Structure([
                ('foo', schemaish.String()),
            ])
        )
        form['foo'].widget = formish.SelectChoice(options=['a', 'b'])
        self.assertTrue('value=""' in form())
        form['foo'].widget = formish.SelectChoice(options=['a', 'b'], none_option=None)
        self.assertTrue('value=""' not in form())


class TestSelectWithOther(base.TestCase):

    def test_default(self):
        form = formish.Form(
            schemaish.Structure([
                ('foo', schemaish.String()),
            ])
        )
        form['foo'].widget = formish.SelectWithOtherChoice(['a', 'b'])
        self.assertTrue('selected="selected"' not in form())
        form.defaults = {'foo': 'b'}
        self.assertTrue('value="b" selected="selected"' in form())
        form.defaults = {'foo': 'c'}
        self.assertTrue('value="..." selected="selected"' in form())


if __name__ == '__main__':
    unittest.main()

