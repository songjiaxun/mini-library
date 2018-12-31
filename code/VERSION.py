from datetime import datetime
with open("VERSION", "w") as file:
    file.write(datetime.now().strftime('%Y-%m-%d'))