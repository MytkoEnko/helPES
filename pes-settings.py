import os, shutil

settings_path = os.path.expanduser('~/Documents/KONAMI/PRO EVOLUTION SOCCER 2019/')
settings_file = settings_path + 'settings.dat'
settings_backup = settings_path + 'settings.dat.pes-bkp'
settings_pesbot = 'settings.dat'

def isthere(a):
    if os.path.exists(a):
        return True
    else:
        return False
def makebkp():
    if isthere(settings_file) and isthere(settings_backup):
        print("There is settings and settings backup files. We can start playing")
        return True
    if isthere(settings_file) and not isthere(settings_backup):
        print("Creating backup and importing pes script ready settings file")
        os.rename(settings_file, settings_backup)
        print('Backup created: ', os.listdir(settings_path))
        shutil.copy(settings_pesbot,settings_file)
        print("Settings copied, folder contents: ", os.listdir(settings_path))
    else:
        print("Something is wrong, please check settings folder")
def revertbackup():
    if isthere(settings_backup) and isthere(settings_file):
        print("Backup is there, reverting:")
        os.remove(settings_file)
        print(settings_file, "removed, starting revert from ", settings_backup)
        os.rename(settings_backup,settings_file)
        print("Backup reverted", settings_file)
    else:
        print("No backup or something is wrong with file structure. Skipping")

#makebkp()
#revertbackup()