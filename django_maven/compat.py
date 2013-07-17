from django import VERSION


if VERSION > (1, 5,):
    from django.core.management.base import OutputWrapper
else:
    from django.utils.encoding import force_unicode

    class OutputWrapper(object):
        """
        Wrapper around stdout/stderr from django 1.5
        """
        def __init__(self, out, style_func=None, ending='\n'):
            self._out = out
            self.style_func = None
            if hasattr(out, 'isatty') and out.isatty():
                self.style_func = style_func
            self.ending = ending

        def __getattr__(self, name):
            return getattr(self._out, name)

        def write(self, msg, style_func=None, ending=None):
            ending = ending is None and self.ending or ending
            if ending and not msg.endswith(ending):
                msg += ending
            style_func = [f for f in (style_func, self.style_func, lambda x:x)
                          if f is not None][0]
            self._out.write(force_unicode(style_func(msg)))
