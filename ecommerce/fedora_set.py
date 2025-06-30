#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading

class FedoraSetupGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fedora Setup & Hardening GUI")
        self.geometry("480x520")
        self.configure(padx=20, pady=20)

        tk.Label(self, text="Fedora Setup & Privacy Hardening", font=("Arial", 16, "bold")).pack(pady=(0,15))

        # Checkbox variables
        self.privacy_var = tk.BooleanVar(value=True)
        self.devtools_var = tk.BooleanVar(value=True)
        self.drivers_var = tk.BooleanVar(value=True)
        self.network_var = tk.BooleanVar(value=False)
        self.firewall_var = tk.BooleanVar(value=True)
        self.reboot_var = tk.BooleanVar(value=False)
        self.darkmode_var = tk.BooleanVar(value=False)

        # Checkbuttons
        tk.Checkbutton(self, text="Privacy Hardening (firewall, dnscrypt)", variable=self.privacy_var).pack(anchor="w")
        tk.Checkbutton(self, text="Developer Tools (git, python, node, docker, VS Code)", variable=self.devtools_var).pack(anchor="w")
        tk.Checkbutton(self, text="Install Drivers (graphics, Wi-Fi, etc.)", variable=self.drivers_var).pack(anchor="w")
        tk.Checkbutton(self, text="Network Tools (Tor, Tailscale)", variable=self.network_var).pack(anchor="w")
        tk.Checkbutton(self, text="Enable Firewall", variable=self.firewall_var).pack(anchor="w")
        tk.Checkbutton(self, text="Reboot After Setup", variable=self.reboot_var).pack(anchor="w")
        tk.Checkbutton(self, text="Dark Mode UI", variable=self.darkmode_var, command=self.toggle_dark_mode).pack(anchor="w", pady=(15,10))

        # Status box
        self.status_text = tk.Text(self, height=10, state="disabled", bg="#f0f0f0")
        self.status_text.pack(fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Start Setup", command=self.start_setup).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Quit", command=self.quit).grid(row=0, column=1, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.quit)

    def toggle_dark_mode(self):
        if self.darkmode_var.get():
            self.configure(bg="#222222")
            self.status_text.configure(bg="#333333", fg="white")
        else:
            self.configure(bg="#f0f0f0")
            self.status_text.configure(bg="white", fg="black")

    def log(self, msg):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, msg + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

    def run_cmd(self, cmd):
        self.log(f"$ {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.log(result.stdout)
        except subprocess.CalledProcessError as e:
            self.log(f"Error: {e.output}")

    def detect_drivers(self):
        self.log("Detecting hardware for driver installation...")
        # Example: Check for NVIDIA GPU
        try:
            output = subprocess.check_output("lspci | grep -i nvidia", shell=True, text=True)
            if output.strip():
                self.log("NVIDIA GPU detected.")
                return "nvidia"
        except:
            pass
        # Check for AMD GPU
        try:
            output = subprocess.check_output("lspci | grep -i amd", shell=True, text=True)
            if output.strip():
                self.log("AMD GPU detected.")
                return "amd"
        except:
            pass
        self.log("No dedicated NVIDIA/AMD GPU detected or unable to detect.")
        return None

    def install_drivers(self):
        gpu = self.detect_drivers()
        self.log("Installing drivers...")
        # Enable RPM Fusion repos
        self.run_cmd("sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm")
        self.run_cmd("sudo dnf install -y https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm")

        if gpu == "nvidia":
            self.log("Installing NVIDIA drivers...")
            self.run_cmd("sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda")
        elif gpu == "amd":
            self.log("AMD drivers are usually included by default. Installing firmware packages...")
            self.run_cmd("sudo dnf install -y linux-firmware")
        else:
            self.log("No proprietary GPU drivers to install.")

        # Wi-Fi drivers
        self.log("Installing common Wi-Fi firmware packages...")
        self.run_cmd("sudo dnf install -y linux-firmware")

    def install_privacy_tools(self):
        self.log("Setting up privacy tools...")
        # Firewall
        if self.firewall_var.get():
            self.run_cmd("sudo systemctl enable --now firewalld")
        else:
            self.run_cmd("sudo systemctl disable --now firewalld")

        # dnscrypt-proxy
        self.run_cmd("sudo dnf install -y dnscrypt-proxy")
        self.run_cmd("sudo systemctl enable --now dnscrypt-proxy")

        # Disable telemetry (example)
        self.log("Disabling basic telemetry...")
        self.run_cmd('sudo bash -c "echo \'\\n[Unit]\\nDescription=Disable systemd-telemetry\\n[Service]\\nType=oneshot\\nExecStart=/bin/sh -c \\"systemctl mask systemd-telemetry.service\\"\\n[Install]\\nWantedBy=multi-user.target\\n\' > /etc/systemd/system/disable-telemetry.service"')
        self.run_cmd("sudo systemctl daemon-reload")
        self.run_cmd("sudo systemctl enable --now disable-telemetry.service")

    def install_dev_tools(self):
        self.log("Installing developer tools...")
        self.run_cmd("sudo dnf groupinstall -y 'Development Tools'")
        pkgs = "git python3 python3-pip nodejs npm vim curl gcc make docker docker-compose"
        self.run_cmd(f"sudo dnf install -y {pkgs}")

        # Enable and start Docker
        self.run_cmd("sudo systemctl enable --now docker")

        # VS Code repo and install
        self.run_cmd("sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc")
        self.run_cmd('sudo bash -c \'echo -e "[code]\\nname=Visual Studio Code\\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\\nenabled=1\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo\'')
        self.run_cmd("sudo dnf install -y code")

    def install_network_tools(self):
        self.log("Installing network tools (Tor, Tailscale)...")
        # Tor
        self.run_cmd("sudo dnf install -y tor")
        self.run_cmd("sudo systemctl enable --now tor")

        # Tailscale (install from official repo)
        self.run_cmd("curl -fsSL https://pkgs.tailscale.com/stable/fedora/tailscale.repo | sudo tee /etc/yum.repos.d/tailscale.repo")
        self.run_cmd("sudo dnf install -y tailscale")
        self.run_cmd("sudo systemctl enable --now tailscaled")
        self.run_cmd("sudo tailscale up")

    def start_setup(self):
        def task():
            self.log("Starting Fedora Setup...")
            if self.privacy_var.get():
                self.install_privacy_tools()
            if self.devtools_var.get():
                self.install_dev_tools()
            if self.drivers_var.get():
                self.install_drivers()
            if self.network_var.get():
                self.install_network_tools()

            self.log("Setup complete!")

            if self.reboot_var.get():
                self.log("Rebooting now...")
                self.run_cmd("sudo reboot")

            messagebox.showinfo("Done", "Fedora setup complete!")

        threading.Thread(target=task).start()


if __name__ == "__main__":
    app = FedoraSetupGUI()
    app.mainloop()
