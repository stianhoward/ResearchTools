# ResearchTools

## Tools for the Liquid Crystal Research Group

### Liquid Crystal Turbulence Tools

- **tracker.py** Main analysis script upon which the other scripts rely. Produces a CSV and H5 file for other scripts to read
- **tracer.py** Traces particles in a defined scope. Exorts an image of the scene with the traces overlayed
- **plot.py:** Reads in the CSV file produced from turb.py, and exports images showing plotted data in multiple forms
- **reynoldsnumber.py** Calculates reynolds number given an input velocity
- **bola_detect.py** Reads the CSV to identify bolas in the scenes. Exports a directory of image snipets which slice out cropped images of the bolas


### Bifurcation Analysis

- **data-vis.py** Visualization of flow of a single area of a video
- **image_stitching.py** Stitches two sets of images together into one video

