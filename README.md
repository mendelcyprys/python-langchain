# Welcome

## Installation instructions

- Clone or download the repository locally.
- Set up a Python virtual environment in the downloaded directory, and activate it in the console.
- Install the Python dependencies using "pip install -r requirements.txt".
- Make a file `.env` in the installation directory, that contains the following line:
  `OPENAI_API_KEY="sk-..."`.
  
  Fill out with your personal key.
- Make any desired changes to the code. In particular, you can add a PDF file into the `pdf-files` folder, and change the path in the code to point at it.
- Run e.g. "python main.py > summary_output.txt", to pipe the output to an output file.