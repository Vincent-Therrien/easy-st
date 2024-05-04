# easy-st

This repository contains tools that aim at simplifying and automating tasks
in spatial transcriptomics on Linux. It contains the following:

- The file **sr-helper.py** is a Python script that simplifies the use of
  `space ranger`, a software tool that processes the raw data of Visium samples.
  Execute the command `python3 sr-helper.py help` for more information.
- The **data** directory contains sample data files that can be used with the
  processing pipelines. View the file inside of the directory to obtain the
  original reference.
- The **pipelines** directory comprises Jupyter notebooks that analyze spRNA-seq
  and scRNA-seq data using the `scanpy` and `squidpy` libraries.

To execute the notebooks, you'll need a Python virtual environment with the
proper dependencies installed. Execute the following command to create the
environment:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You can then launch Jupyter with this virtual environment and execute the
notebooks of this repository.
