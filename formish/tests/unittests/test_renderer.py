import os
import shutil
import tempfile
import unittest
from formish.renderer import Renderer, _default_renderer


class TestRenderer(unittest.TestCase):

    def test_default_renderer(self):
        # Deliberately choose a template that needs no args.
        self.assertTrue('/form' in _default_renderer('formish/form/footer.html', {}))

    def test_custom_renderer(self):
        # Use a template that we know formish provides.
        template = 'formish/form/footer.html'
        # Create a template directory structure with an overriden template.
        tmpdir = tempfile.mkdtemp()
        tmptemplate = os.path.join(tmpdir, template)
        os.makedirs(os.path.dirname(tmptemplate))
        open(tmptemplate, 'w').write('custom')
        # Check the custom template directory is used first.
        renderer = Renderer([tmpdir])
        self.assertTrue(renderer('formish/form/footer.html', {}) == 'custom')
        # Cleanup
        shutil.rmtree(tmpdir)


if __name__ == '__main__':
    unittest.main()

