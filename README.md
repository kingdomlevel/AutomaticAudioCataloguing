# Automatic Audio Cataloguing Tool
### University Summer Project
Code repository for my university summer project **_Automatic Tools for Populating Graph Representations of Multimedia Catalogues_**. Very much a research project, the code takes an audio file like *this*:
![audio image](https://68.media.tumblr.com/f0663534562661a96049ba09aa1e1bf3/tumblr_owh89zWXO01uoduy3o1_1280.png)

...automatically generates labels like *this*:
![labels image](https://68.media.tumblr.com/738971e3751e099662b23c42c2082cec/tumblr_owh89zWXO01uoduy3o2_1280.png)

...and automatically populates a graph database like **this**:
![database image](https://68.media.tumblr.com/96702df0f48807b0a37b72f22710c3ae/tumblr_owh89zWXO01uoduy3o3_1280.png)


---
### Prerequisites
* [OrientDB](https://orientdb.com/) database backend, preconfigured for FRBR-inspired audio ontology ([restore](https://orientdb.com/docs/2.1/Backup-and-Restore.html) from the backup `.zip` available [**here**](https://drive.google.com/open?id=0B4_JQ3-xFK6VTVNDTmNwR1pxYzg))
* [LIUM](http://www-lium.univ-lemans.fr/diarization/doku.php/welcome) toolbox (packaged `.jar` version)
* [Python 2.7](https://www.python.org/downloads/release/python-2714/)
* Packages as listed in `requirements.txt`

The code for this project has been specifically designed for use with the [Scottish Music Centre](http://www.scottishmusiccentre.com/)'s naming conventions, but will mostly work regardless of file naming protocol.

---

This project was undertaken as part fulfillment for my masters degree *MSc Software Developmet* from [University of Glasgow](http://www.gla.ac.uk/postgraduate/taught/softwaredevelopment/) during summer 2017. The project was supervised by [Dr. Bjørn Sand Jensen](http://www.gla.ac.uk/schools/computing/staff/bjornjensen/) and was supported by the [Scottish Music Centre](http://www.scottishmusiccentre.com/) by way of use of their digital archive.
