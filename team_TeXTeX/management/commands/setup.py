from django.core.management.base import BaseCommand
import subprocess
import platform
import sys

class Command(BaseCommand):
    help = 'Sets up the TeX environment for production (installing latexmk, texlive, etc.)'

    def handle(self, *args, **options):
        system = platform.system()
        self.stdout.write(f"Detected OS: {system}")

        if system == "Linux":
            self.setup_linux()
        elif system == "Windows":
            self.setup_windows()
        else:
            self.stdout.write(self.style.WARNING(f"Unsupported OS for automatic setup: {system}. Please install TeX Live manually."))

    def setup_linux(self):
        self.stdout.write("Starting Linux setup...")
        # Check for apt-get (Debian/Ubuntu)
        try:
            subprocess.run(["which", "apt-get"], check=True, stdout=subprocess.DEVNULL)
            self.stdout.write("apt-get detected. Installing packages...")
            
            # Update apt
            self.run_command(["sudo", "apt-get", "update"])

            # Install Latexmk and TeX Live (Small + Japanese support)
            # texlive-lang-japanese roughly corresponds to collection-langjapanese
            packages = [
                "latexmk",
                "texlive-base",
                "texlive-latex-recommended",
                "texlive-fonts-recommended",
                "texlive-lang-japanese" 
            ]
            
            self.run_command(["sudo", "apt-get", "install", "-y"] + packages)
            self.stdout.write(self.style.SUCCESS("Linux setup completed successfully!"))
            
        except subprocess.CalledProcessError:
             self.stdout.write(self.style.ERROR("apt-get not found. Currently only Debian/Ubuntu based Linux is supported via this script."))

    def setup_windows(self):
        self.stdout.write("Starting Windows setup check...")
        # Check if latexmk is already installed
        if self.check_command("latexmk"):
             self.stdout.write(self.style.SUCCESS("latexmk is already installed."))
             return

        self.stdout.write(self.style.WARNING("Automatic full installation on Windows is complex."))
        self.stdout.write("It is recommended to install TeX Live manually from: https://www.tug.org/texlive/")
        self.stdout.write("Or use a package manager like Scoop or Chocolatey:")
        self.stdout.write("  > scoop install latexmk")
        self.stdout.write("  > scoop install texlive")

    def run_command(self, cmd):
        try:
            self.stdout.write(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"Command failed: {e}"))
            sys.exit(1)

    def check_command(self, cmd):
        from shutil import which
        return which(cmd) is not None
