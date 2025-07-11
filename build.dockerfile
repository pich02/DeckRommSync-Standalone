FROM pich02/python3-glibc2.24:3.13.5 

WORKDIR /app

COPY . ./ 

RUN python3.13 -m pip install -r requirements.txt
RUN python3.13 -m pip install pyinstaller

CMD ["python3.13", "-m", "PyInstaller", "app.spec"]
