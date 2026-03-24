import urllib.parse
from subprocess import check_output

import gi
import pyperclip
from gi.repository import Adw, Gio, Gtk

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


class APIClientWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="API Client")
        self.set_default_size(700, 550)

        self.params = []

        # main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        self.set_content(main_box)

        # url
        url_box = Gtk.Box(spacing=6)
        main_box.append(url_box)

        url_label = Gtk.Label(label="API URL:")
        url_label.set_xalign(0)
        url_box.append(url_label)

        self.url_entry = Gtk.Entry()
        self.url_entry.set_hexpand(True)
        url_box.append(self.url_entry)

        # parameters
        params_group = Adw.PreferencesGroup(title="Parameters")
        main_box.append(params_group)

        self.params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        params_group.add(self.params_box)

        add_btn = Gtk.Button(label="Add Parameter")
        add_btn.connect("clicked", self.add_param)
        main_box.append(add_btn)

        # buttons
        btn_box = Gtk.Box(spacing=6)
        btn_box.set_halign(Gtk.Align.CENTER)
        main_box.append(btn_box)

        send_btn = Gtk.Button(label="Send Request")
        send_btn.add_css_class("suggested-action")
        send_btn.connect("clicked", self.send_request)
        btn_box.append(send_btn)

        curl_btn = Gtk.Button(label="Copy as cURL")
        curl_btn.connect("clicked", self.copy_curl)
        btn_box.append(curl_btn)

        # response
        self.response_view = Gtk.TextView()
        self.response_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.response_view.set_vexpand(True)

        scroll = Gtk.ScrolledWindow()
        scroll.set_child(self.response_view)
        main_box.append(scroll)

    def add_param(self, widget=None, key="", value=""):
        row = Gtk.Box(spacing=6)

        key_entry = Gtk.Entry()
        key_entry.set_placeholder_text("Key")
        key_entry.set_text(key)
        key_entry.set_hexpand(True)
        row.append(key_entry)

        value_entry = Gtk.Entry()
        value_entry.set_placeholder_text("Value")
        value_entry.set_text(value)
        value_entry.set_hexpand(True)
        row.append(value_entry)

        remove_btn = Gtk.Button(icon_name="user-trash-symbolic")

        def remove(btn):
            self.params_box.remove(row)
            self.params.remove((key_entry, value_entry))

        remove_btn.connect("clicked", remove)
        row.append(remove_btn)

        self.params_box.append(row)
        self.params.append((key_entry, value_entry))

    def get_params_dict(self):
        params = {}
        for key_entry, value_entry in self.params:
            key = key_entry.get_text().strip()
            value = value_entry.get_text().strip()
            if key:
                params[key] = value
        return params

    def show_message(self, text, error=False):
        dialog = Adw.MessageDialog.new(self, "Error" if error else "Info", text)
        dialog.add_response("ok", "OK")
        dialog.present()

    def send_request(self, widget):
        url = self.url_entry.get_text().strip()
        if not url:
            self.show_message("Please enter a URL", error=True)
            return

        params = self.get_params_dict()
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}" if query_string else url

        try:
            response = check_output(["curl", "-s", "-X", "GET", full_url])
            buffer = self.response_view.get_buffer()
            buffer.set_text(response.decode())
        except Exception as e:
            self.show_message(str(e), error=True)

    def copy_curl(self, widget):
        url = self.url_entry.get_text().strip()
        if not url:
            self.show_message("Please enter a URL", error=True)
            return

        params = self.get_params_dict()
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}" if query_string else url

        curl_cmd = f'curl -s -X GET "{full_url}"'
        pyperclip.copy(curl_cmd)

        self.show_message("cURL command copied to clipboard!")


class APIClientApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="Dog")

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = APIClientWindow(self)
        win.present()


if __name__ == "__main__":
    app = APIClientApp()
    app.run()
