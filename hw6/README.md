# Illinois buildings, in perspective

Keliang Zhu · IS445 · Homework 6

A Streamlit report with two Altair visualizations of the course's Illinois building inventory: a horizontal agency ranking and a construction-decade histogram. Each chart has a paragraph explaining the question, visual encodings, interactions, and possible improvements. The app also documents differences from HW5, which used UFO data.

## Run locally

Requires Python 3.12 or later.

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Interactions

- Building status filters both charts and headline totals.
- The first chart switches between recorded floor area and record count, and allows 5–30 agencies.
- The second chart filters by agency and construction-year range. These controls do not filter the first chart.
- Empty selections display an explanation instead of an error.

## Data

Original source: https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/building_inventory.csv

The unchanged CSV snapshot was downloaded November 13, 2026 and is included under `data/`. Rows are inventory records, not independently verified unique buildings. Repeated rows are retained because the dataset has no unique building identifier. Zero construction years are unknown; nonpositive floor areas do not contribute to area sums. Complete preparation notes are shown in the app.

## Deploy to Streamlit Community Cloud

1. This project lives in the `hw6/` folder of the public repository https://github.com/Keliang23/is445_demo.
2. At https://share.streamlit.io/ create an app from that repository, branch `main`, entrypoint `hw6/app.py`.
3. Select Python **3.12** in Advanced settings and deploy.
4. Ensure the app is public and check both charts and all controls on the deployed URL.
5. Submit the actual `https://….streamlit.app/` URL and the public GitHub repository URL.

Official deployment reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Verify

```sh
python -m unittest discover -s tests -v
```
