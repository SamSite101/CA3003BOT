import pkg_resources
import os

def check_required_packages(requirements_file='requirements.txt'):
    """
    Überprüft, ob alle in der requirements.txt-Datei gelisteten Pakete installiert sind.
    """
    if not os.path.exists(requirements_file):
        print(f"Fehler: Die Datei '{requirements_file}' wurde nicht gefunden.")
        return

    print(f"Überprüfe Pakete aus '{requirements_file}'...")
    
    missing_packages = []
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}

    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Versuche, Paketnamen und Version zu trennen
            # Berücksichtigt Fälle wie 'package==version', 'package>=version', 'package'
            package_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip().lower()

            if package_name and package_name not in installed_packages:
                missing_packages.append(line)

    if missing_packages:
        print("\nDie folgenden Pakete aus requirements.txt sind NICHT installiert oder haben die falsche Version:")
        for pkg in missing_packages:
            print(f"- {pkg}")
        print("\nBitte führen Sie 'pip install -r requirements.txt' im Terminal aus, um sie zu installieren.")
    else:
        print("\nAlle erforderlichen Pakete aus requirements.txt sind installiert.")

if __name__ == "__main__":
    check_required_packages()
