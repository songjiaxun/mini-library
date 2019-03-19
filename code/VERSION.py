from datetime import datetime
with open("VERSION.txt", "w") as file:
    file.write(datetime.now().strftime('%Y-%m-%d'))