import gi, sys
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.nekorect.pythonclash")
        GLib.set_application_name('My Gtk Application')

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self, title="Hello World")
        window.present()


if __name__ == "__main__":
    app = Application()
    app.run()
    #exit_status = app.run(sys.argv)
