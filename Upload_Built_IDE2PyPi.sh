# Clean and rebuild
python3 Build_AND_Upload_PyPi.py --clean
python3 Build_AND_Upload_PyPi.py  --build
python3 Build_AND_Upload_PyPi.py --test
python3 Build_AND_Upload_PyPi.py  --install

# Test the wheel locally first
pip uninstall bsg-ide -y


# Test the command
bsg-ide

# If it works, upload
python3 Build_AND_Upload_PyPi.py --upload-prod


# First, make sure twine is installed and up to date
pip install --upgrade twine

# Upload to Test PyPI first (recommended)
twine upload --repository testpypi dist/*

# Then upload to production PyPI
twine upload dist/*
