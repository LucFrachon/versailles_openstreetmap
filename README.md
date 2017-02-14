# versailles_openstreetmap
Data Wrangling and MongoDB project based on OpenStreetMap extract for the Versailles area (France)

## Summary
This project takes geographical [data](https://s3.amazonaws.com/mapzen.odes/ex_DRcFT2edje1bEvDwVEKv4jZvAAvP8.osm.bz2) from [OpenStreetMap](http://www.openstreetmap.org/#map=5/51.500/-0.100) and performs several cleaning and munging tasks to improve it.

I then load the data into a local MongoDB database and investigate  it to learn some interesting facts about the Versailles area and especially its palace.

Finally I offer some ideas for further improvement of the dataset.

## File formats
- The original [data](https://s3.amazonaws.com/mapzen.odes/ex_DRcFT2edje1bEvDwVEKv4jZvAAvP8.osm.bz2) is not included for size reasons. It is about 230MB in uncompressed size. The format is OSM XML.
- The project itself is written in a Jupyter Notebook (versailles.ipynb) that renders into HTML. Other render format are discouraged, as the notebook contains a script to show and hide code by pressing a button.

## License
MIT License

Copyright (c) 2017 Luc Frachon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
