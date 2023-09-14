import streamlit as st
import requests
from lxml import html
from lxml import etree

# Define CSS style for the player card and team cards
style = """
<style>
.player-card {
    border: 1px solid #ccc;
    padding: 20px;
    margin: 10px;
    border-radius: 5px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.player-card .block-quarter {
    padding: 0 13px;
    width: 60px;
    background-color: #198754;
}

.team-card {
    border: 1px solid #ccc;
    padding: 10px;
    margin: 10px;
    border-radius: 5px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.player-image {
    max-width: 100px;
    max-height: 100px;
}

.player-info {
    margin-left: 10px;
    display: inline-block;
}

.player-name {
    font-size: 18px;
    font-weight: bold;
}

.team-name {
    font-size: 16px;
    font-weight: bold;
}

.team-flag {
    width: 21px;
    height: 16px;
    margin-right: 5px;
}

</style>
"""

# Apply the CSS style
st.markdown(style, unsafe_allow_html=True)


st.title('Football Player Market Value Prediction')

# User input for player name
player_name = st.text_input('Enter the player name:')

data = {"player_name": player_name}

# Button to make the prediction request
if st.button('Predict'):
    if player_name:
        response = requests.post(
            "http://127.0.0.1:8000/predict", json=data)
        if response.status_code == 200:
            predicted_value = response.json()

            # Prepare the URL for searching the player on Sofifa.com
            base_url = "https://sofifa.com"
            search_url = f"{base_url}/players?keyword={player_name.replace(' ', '+')}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
            # Send an HTTP GET request to the search URL
            response = requests.get(search_url, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the HTML content of the page using lxml
                tree = html.fromstring(response.content)

                # Find the player link using the provided XPath expression
                player_link = tree.xpath(
                    '//*[@id="body"]/div[1]/div/div[2]/div/table/tbody/tr/td[2]/a[1]')

                if player_link:
                    # Extract the href attribute value
                    href_value = player_link[0].get('href')

                    # Build the full URL
                    player_url = f"{base_url}{href_value}"
                    print(player_url)

                    # Send a request to the player's page and retrieve more information
                    player_response = requests.get(player_url, headers=headers)

                    if player_response.status_code == 200:

                        # Parse the player's page using lxml
                        player_tree = html.fromstring(player_response.content)

                        # Extract more player information using XPath or other methods
                        player_name_element = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[1]/div/h1')[0].text
                        player_img = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[1]/img')[0].get('data-src')
                        player_country_flag_team = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[4]/div/h5/a/img')
                        player_team_name = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[4]/div/h5/a')
                        player_team_flag = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[4]/div/img')
                        player_team_position = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[4]/div/ul/li[2]/span')
                        player_team_kit_number = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[4]/div/ul/li[3]')
                        player_country_flag = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[5]/div/h5/a/img')
                        player_country_name = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[5]/div/h5/a')
                        player_country_flag_inter = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[5]/div/img')
                        player_country_position = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[5]/div/ul/li[2]/span')
                        player_country_kit_number = player_tree.xpath(
                            '//*[@id="body"]/div[2]/div/div[2]/div[5]/div/ul/li[3]')

            # Display the player card
            st.markdown(f"""
            <div class="player-card">
                <img src={player_img} alt="Player Image" class="player-image">
                <div class="player-info">
                    <h1 class="player-name">{player_name_element}</h1>
                    <div class="block-quarter">
                        <div>
                            €{int(predicted_value + 0.5)}M
                            <div class="sub">Value</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Create a row layout for team cards
            team_cards = st.columns(2)

            # First team card
            with team_cards[0]:
                if (player_country_flag_team and
                        player_team_name and
                        player_team_flag and
                        player_team_position and
                        player_team_kit_number
                        ):
                    st.markdown(f"""
                        <div class="team-card">
                            <h5><img alt="" src={player_country_flag_team[0].get('data-src')}>{player_team_name[0].text_content()}</h5>
                            <img alt="" src={player_team_flag[0].get('data-src')} width="60" height="60">
                            <ul class="ellipsis pl">
                                <li><label>Position: </label><span class="pos pos24"> {player_team_position[0].text}</span></li>
                                <li><label>Kit number: </label> {player_team_kit_number[0].text_content().strip('Kit number')}</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

            # Second team card
            with team_cards[1]:
                if (player_country_flag and
                    player_country_name and
                    player_country_flag_inter and
                    player_country_position and
                    player_country_kit_number
                    ):
                    st.markdown(f"""
                    <div class="team-card">
                        <h5><img alt="" src={player_country_flag[0].get('data-src')} width="21" height="16"> {player_country_name[0].text_content()}</h5>
                        <img alt="" src={player_country_flag_inter[0].get('data-src')} width="60" height="60" >
                        <ul class="ellipsis pl">
                            <li><label>Position: </label><span class="pos pos23"> {player_country_position[0].text}</span></li>
                            <li><label>Kit number: </label> {player_country_kit_number[0].text_content().strip('Kit number')}</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Failed to fetch prediction. Please check the player name.")
    else:
        st.warning("Please enter a player name.")

st.write('---')
st.write('About this App:')
st.write('This web app allows you to predict the market value of a football player.')
