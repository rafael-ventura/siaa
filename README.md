# SIAA — Interactive Academic Analytics System

A Streamlit app for analyzing and visualizing academic data. Upload an `.xlsx` spreadsheet and
it processes the data into dashboards with charts and key indicators about the students in a
course. Built for my undergraduate thesis.

> Live at [siaa-tcc.streamlit.app](https://siaa-tcc.streamlit.app/) — free-tier hosting, so it
> sleeps when idle. Open the link, click to wake it up, and give it a few seconds.

## How to run locally

```bash
git clone https://github.com/rafael-ventura/siaa.git
cd siaa
pip install -r requirements.txt   # a virtual environment is recommended
streamlit run app.py
```

Open `http://localhost:8501`, download the sample spreadsheet (pre-filled with test data) to
try it out, or swap in your own data using the same format. Explore charts across five
sections: admission pathways, gender breakdown, socioeconomic impact, pandemic impact, and
student profile.

## Structure

- `app.py` — main entry point
- `modules/`
  - `web/` — pages and navigation
  - `service/` — spreadsheet processing/validation
  - `graficos/` — chart generation
  - `explicacoes/` — descriptive text used in the UI
- `assets/` — images, icons, static files

## Notes

- Uploaded data is **never stored** — everything runs locally, in memory.
- Minor column-name variations in the spreadsheet are tolerated.
- Open source, adaptable to other courses/institutions.

## License

[MIT](LICENSE)
