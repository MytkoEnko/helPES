def write_updated_version_file():
    def get_file_version(with_v=True):
        from subprocess import check_output
        version = check_output('git describe --tags --abbrev=0', shell=True, encoding="utf-8").strip("v\n")
        tuple_version = tuple(list(int(n) for n in version.split(".")) + [0 if len(version.split(".")) == 3 else 0,0])
        if with_v:
            return 'v' + version
        else:
            return tuple_version
    with open('./file_version_info.txt', "w+b") as f:
        body = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx


VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers={get_file_version(False)},
    prodvers={get_file_version(False)},
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904b0',
        [StringStruct(u'CompanyName', u'https://github.com/MytkoEnko'),
        StringStruct(u'FileDescription', u'helPES App'),
        StringStruct(u'FileVersion', u'{get_file_version()}'),
        StringStruct(u'InternalName', u'helPES'),
        StringStruct(u'LegalCopyright', u'MytkoEnko © 2020'),
        StringStruct(u'OriginalFilename', u'helPES.exe'),
        StringStruct(u'ProductName', u'helPES'),
        StringStruct(u'ProductVersion', u'{get_file_version()}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        f.write(body.encode("utf-8"))
    with open('./version', "w") as f_v:
        version_file = f'{get_file_version()}'
        f_v.write(version_file)
write_updated_version_file()