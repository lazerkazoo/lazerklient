import tkinter as tk
import urllib.parse
from subprocess import check_output
from tkinter import messagebox, ttk

import pyperclip


class APIClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("API Client")

        self.params = []

        url_frame = ttk.Frame(root)
        url_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(url_frame, text="API URL:").pack(side="left")
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)

        self.params_frame = ttk.LabelFrame(root, text="Parameters")
        self.params_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Button(root, text="Add Parameter", command=self.add_param).pack(pady=5)

        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Send Request", command=self.send_request).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Copy as cURL", command=self.copy_curl).pack(
            side="left", padx=5
        )

        self.response_text = tk.Text(root, height=15)
        self.response_text.pack(fill="both", expand=True, padx=10, pady=5)

    def add_param(self, key="", value=""):
        frame = ttk.Frame(self.params_frame)
        frame.pack(fill="x", pady=2)

        key_entry = ttk.Entry(frame)
        key_entry.insert(0, key)
        key_entry.pack(side="left", fill="x", expand=True, padx=2)

        value_entry = ttk.Entry(frame)
        value_entry.insert(0, value)
        value_entry.pack(side="left", fill="x", expand=True, padx=2)

        def remove():
            frame.destroy()
            self.params.remove((key_entry, value_entry))

        ttk.Button(frame, text="X", command=remove).pack(side="right", padx=2)

        self.params.append((key_entry, value_entry))

    def get_params_dict(self):
        params = {}
        for key_entry, value_entry in self.params:
            key = key_entry.get().strip()
            value = value_entry.get().strip()
            if key:
                params[key] = value
        return params

    def send_request(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        params = self.get_params_dict()

        try:
            response = str(
                check_output(
                    ["curl", "-s", "-X", "GET", url + urllib.parse.urlencode(params)]
                )
            )
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert(tk.END, response)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def copy_curl(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        params = self.get_params_dict()

        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}" if query_string else url

        curl_cmd = f'curl -s -X GET "{full_url}"'

        pyperclip.copy(curl_cmd)
        messagebox.showinfo("Copied", "cURL command copied to clipboard!")


if __name__ == "__main__":
    root = tk.Tk()
    app = APIClientGUI(root)
    root.mainloop()
