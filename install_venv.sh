#! /bin/bash
mkdir pybison_tmp
cd pybison_tmp

# install dependencies
pip3 install cython 
pip3 install six

# install Pyrex (converts from python2 to python3 code)
curl -L -O http://www.cosc.canterbury.ac.nz/greg.ewing/python/Pyrex/Pyrex-0.9.9.tar.gz
tar xzf Pyrex-0.9.9.tar.gz
cd Pyrex-0.9.9
2to3 -w .
python3 setup.py install
cd ..
rm -rf Pyrex-0.9.9*

# install PyBison (python3)
git clone https://github.com/da-h/pybison
cd pybison
python3 setup.py install
cd ..
# mv pybison/doc pybison_doc
# mv pybison/examples pybison_examples
rm -rf pybison/

# remove temporary folder
cd ..
rm -rf pybison_tmp
