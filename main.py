import pickle
import uvicorn
import numpy as np
import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup


def get_player_info(player_name):
    # Prepare the URL for searching the player on Sofifa.com
    base_url = "https://sofifa.com/"
    search_url = f"{base_url}players?keyword={player_name.replace(' ', '%20')}&showCol%5B%5D=ae&showCol%5B%5D=fi&showCol%5B%5D=bl&showCol%5B%5D=tp&showCol%5B%5D=so&showCol%5B%5D=te&showCol%5B%5D=ir&showCol%5B%5D=sho&showCol%5B%5D=pas&showCol%5B%5D=dri"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    # Send an HTTP GET request to the search URL
    response = requests.get(search_url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", {"class": "table table-hover persist-area"})
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            player_info = {"Name": cols[1].get_text().strip()}
            for col in cols[2:]:
                header = table.find_all(
                    "th")[cols.index(col)].get_text().strip()
                player_info[header] = col.get_text().strip()

        player_info = {
            "Ball control": int(player_info["Ball control"]),
            "Dribbling / Reflexes": int(player_info["Dribbling / Reflexes"]),
            "Total power": int(player_info["Total power"]),
            "Shooting / Handling": int(player_info["Shooting / Handling"]),
            "Age": int(player_info["Age"]),
            "Total mentality": int(player_info["Total mentality"]),
            "Finishing": int(player_info["Finishing"]),
            "Passing / Kicking": int(player_info["Passing / Kicking"]),
            "Shot power": int(player_info["Shot power"]),
            "International reputation": int(player_info["International reputation"])
        }
        return player_info

    else:
        print(
            f"Error: Unable to fetch data from Sofifa.com. Status Code: {response.status_code}")
        return None


app = FastAPI(
    title='Football Players Market Value Prediction',
    version='1.0',
    description='prediction of market value of a specific player'
)

# Load the saved model from a file
with open('best_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)


class Data(BaseModel):
    player_name: str

# Api root or home endpoint


@app.get('/')
@app.get('/home')
def read_home():
    """
     Home endpoint which can be used to test the availability of the application.
     """
    return {'message': 'System is healthy'}

# ML API endpoint for making prediction aganist the request received from client


@app.post("/predict")
def predict(data: Data):
    input_features = [get_player_info(data.player_name)]
    input_data = pd.DataFrame(input_features)

    input_array = input_data.values

    predictions = model.predict(input_array)
    print(f"predicted market value is {predictions}")
    return predictions[0]


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
