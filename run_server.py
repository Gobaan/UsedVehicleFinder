import cherrypy
import os.path


class Root(object):
    def index(self):
        with open('index.html') as fp:
            return ' '.join(fp.readlines())

    def hide(self, id):
        with open('images/hidden.csv', 'a') as fp:
            fp.write(id + '\n')
        return id

    def color(self, id, color):
        with open('images/color.csv', 'a') as fp:
            fp.write('%s %s\n' % (id, color))
        return id

    hide.exposed = True
    color.exposed = True
    index.exposed = True


current_dir = os.path.dirname(os.path.abspath(__file__))
conf = {'/images':
        {'tools.staticdir.on': True,
         'tools.staticdir.dir': os.path.join(current_dir, 'images')}}

cherrypy.quickstart(Root(), '/', config=conf)
