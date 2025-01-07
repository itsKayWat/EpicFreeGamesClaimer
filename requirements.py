import subprocess
import sys

def install_requirements():
    print("Installing required packages...")
    requirements = [
        'selenium',
        'webdriver_manager',
        'configparser',
        'requests',
        'logging',
        'datetime'
    ]
    
    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("\nAll requirements installed successfully!")
    print("Note: Make sure you have Chrome browser installed.")
    print("The Chrome WebDriver will be automatically managed by webdriver_manager.")

if __name__ == "__main__":
    install_requirements()