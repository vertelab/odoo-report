how to get glabels working with EAN-13 barcodes:

links: 

    https://bugs.launchpad.net/ubuntu/+source/glabels/+bug/1901164
    https://www.ccoderun.ca/programming/2019-08-16_Zint/
    https://bugs.launchpad.net/ubuntu/+source/barcode/0.99-4

Uninstall the packages:

    * barcode (0.99-3) [universe]
    * glabels (3.4.1-1.2) [universe]
    * glabels-data (3.4.1-1.2) [universe]

Download and Install the barcode package from groovy (using dpkg -i):

    * barcode (0.99-4) [universe] https://ubuntu.pkgs.org/20.10/ubuntu-universe-amd64/barcode_0.99-4_amd64.deb.html

allow to download sources:

    * sudo nano /etc/apt/sources.list
    * uncomment all the deb-src lines
    * sudo apt update

install dependencies:

    * sudo apt install autotools-dev autoconf-archive cdbs debhelper intltool gtk-doc-tools yelp-tools libgtk-3-dev librsvg2-dev libcairo2-dev libpango1.0-dev libebook1.2-dev libiec16022-dev cmake devscripts libqrencode-dev gnome-desktop3-data gnome-doc-utils

install annoying dependency:

    * download libzint: https://sourceforge.net/projects/zint/
    * tar zxvf ~/Downloads/zint-2.6.3_final.tar.gz
    * cd zint-2.6.3.src/
    * mkdir build
    * cd build
    * cmake -DCMAKE_BUILD_TYPE=Release ..
    * make
    * sudo make install

Rebuild the glabels package from Source:

    * mkdir glabels-build
    * cd glabels-build/
    * apt source glabels
    * cd glabels-3.4.1/
    * debchange -i
    * dpkg-source --commit
    * debuild -us -uc -i -I
    * sudo debi

python stuff:
    * sudo pip3 install unicodecsv
