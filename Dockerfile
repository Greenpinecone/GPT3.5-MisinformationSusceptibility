FROM python:3.12-slim

# All subsequent commands will be executed in the context of the /app directory
WORKDIR /app

# Copies all current requirements (dependencies to the docker container)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copies everything from my current project folder to the /app folder in the docker container
COPY . . 
# The final result is app/app/main.py ...

# Command to start the python applciation
CMD ["streamlit", "run", "--server.address=0.0.0.0", "app/main.py"]