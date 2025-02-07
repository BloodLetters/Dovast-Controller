New-Item -ItemType Directory -Path .\Dovast-Compiled
pyinstaller --onefile --name Dovast --icon=..\assets\icon.ico --distpath Dovast-Compiled/Dist --workpath Dovast-Compiled/Build --specpath Dovast-Compiled --distpath .\Dovast-Compiled index.py
New-Item -ItemType Directory -Path .\Dovast-Compiled\keys

# Copy item
Copy-Item -Path .\config.json -Destination .\Dovast-Compiled\
Copy-Item -Path .\keys\mouse-example.json -Destination .\Dovast-Compiled\keys\
Copy-Item -Path .\keys\keyboard-example.json -Destination .\Dovast-Compiled\keys\
Copy-Item -Path .\keys\slide-example.json -Destination .\Dovast-Compiled\keys\

# Clearing Unused package
Remove-Item -Path .\Dovast-Compiled\Build -Recurse
Remove-Item -Path .\Dovast-Compiled\Dovast.spec

# Close
exit