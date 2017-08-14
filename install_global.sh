#! /bin/bash
mkdir pybison_tmp
cd pybison_tmp

# install dependencies
sudo apt-get install -y bison flex
sudo pip3 install cython 
sudo pip3 install six

# install Pyrex (converts from python2 to python3 code)
curl -L -O http://www.cosc.canterbury.ac.nz/greg.ewing/python/Pyrex/Pyrex-0.9.9.tar.gz
tar xzf Pyrex-0.9.9.tar.gz
cd Pyrex-0.9.9
2to3 -w .
sudo python3 setup.py install
cd ..
sudo rm -rf Pyrex-0.9.9*

# install PyBison (python3)
git clone https://github.com/da-h/pybison
cd pybison
sudo python3 setup.py install
cd ..
# mv pybison/doc pybison_doc
# mv pybison/examples pybison_examples
sudo rm -rf pybison/

# remove temporary folder
cd ..
rm -rf pybison_tmp
