pip uninstall -y coordtransform

python setup.py sdist bdist_wheel
pip install --force-reinstall  ./dist/coordtransform-1.0.0-py3-none-any.whl

rm -r ./build ./dist ./coordtransform.egg-info