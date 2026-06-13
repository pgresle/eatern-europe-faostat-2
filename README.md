# 🌾 FAOSTAT – Zemědělství Východní Evropy

Interaktivní dashboard s daty o zemědělské produkci, land use, hospodářských zvířatech a zahraničním obchodu pro 10 zemí východního bloku (1961–2023).

## Jak nasadit na Streamlit Cloud (zdarma, 5 minut)

### 1. Vytvořte GitHub repozitář

1. Jděte na [github.com](https://github.com) → **New repository**
2. Název: `faostat-dashboard` (nebo cokoliv)
3. Nastavte jako **Public**
4. Klikněte **Create repository**

### 2. Nahrajte soubory

V novém repozitáři klikněte **Add file → Upload files** a nahrajte:
```
app.py
data.py
requirements.txt
.streamlit/config.toml
```

*(složku `.streamlit` s `config.toml` nahrajte jako složku, nebo ji vytvořte ručně v GitHubu)*

### 3. Nasaďte na Streamlit Cloud

1. Jděte na [share.streamlit.io](https://share.streamlit.io)
2. Přihlaste se přes GitHub
3. Klikněte **New app**
4. Vyberte váš repozitář a větev `main`
5. **Main file path:** `app.py`
6. Klikněte **Deploy!**

Za 1–2 minuty dostanete veřejný link ve tvaru:
```
https://vasejmeno-faostat-dashboard-app-xxxxx.streamlit.app
```

---

## Struktura souborů

```
├── app.py              # hlavní Streamlit aplikace
├── data.py             # všechna data (FAOSTAT + populace OSN)
├── requirements.txt    # Python závislosti
└── .streamlit/
    └── config.toml     # tmavý theme
```

## Funkce dashboardu

- **4 kategorie dat**: Plodiny · Land use · Hospodářská zvířata · Zahraniční obchod
- **10 zemí**: Polsko, Ukrajina, Rusko, Rumunsko, Maďarsko, Česko, Bulharsko, Bělorusko, Slovensko, Moldávie
- **Časová řada**: 1961–2023
- **Přepočet na osobu**: toggle pro normalizaci populací
- **Nastavitelné časové okno** a výběr zemí
- **Small multiples**: jedna karta = jedna země

## Zdroj dat

- Zemědělská produkce, land use, živočišná výroba: [FAOSTAT](https://www.fao.org/faostat/)
- Populační data: [UN World Population Prospects](https://population.un.org/wpp/)
