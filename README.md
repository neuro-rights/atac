<p align="center" width="100%"><img src="https://raw.githubusercontent.com/neuro-rights/atac/master/data/assets/img/jesus/jesus_king.png"></p>

### Activism Tools Against Cybertorture

##### GitHub
![python-app](https://github.com/strikles/atac/actions/workflows/python-app.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Upload Python Package](https://github.com/strikles/atac/actions/workflows/python-publish.yml/badge.svg?branch=main)](https://github.com/strikles/atac/actions/workflows/python-publish.yml)

#### Q.A. Metrics

##### Codacy
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/d3de586ed5a248ca917c99e95757252c)](https://www.codacy.com/gh/strikles/atac/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=strikles/atac&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/d3de586ed5a248ca917c99e95757252c)](https://www.codacy.com/gh/strikles/atac/dashboard?utm_source=github.com&utm_medium=referral&utm_content=strikles/atac&utm_campaign=Badge_Coverage)

##### Code Inspector
[![Code Quality Score](https://api.codiga.io/project/29990/score/svg)](https://www.code-inspector.com/public/project/29990/atac/dashboard)

##### DeepSource
[![DeepSource](https://deepsource.io/gh/strikles/atac.svg/?label=active+issues&show_trend=true&token=knjxrFWrr_WNtdD2XCDeYO0i)](https://deepsource.io/gh/strikles/atac/?ref=repository-badge)
[![DeepSource](https://deepsource.io/gh/strikles/atac.svg/?label=resolved+issues&show_trend=true&token=knjxrFWrr_WNtdD2XCDeYO0i)](https://deepsource.io/gh/strikles/atac/?ref=repository-badge)


### Summary


##### The current scraping algorithm is the following
```markdown
P ← starting URLs (primary queue)
S ← ∅ (secondary queue)
V ← ∅ (visited pages)
while P ≠ ∅ do
    Pick a page v from P and download it
    V ← V ∪ {v} (mark as visited)
    N+(v) ← v’s out-links pointing to new pages (“new” means not in P, S or V)
    if |N+(v)| > t then
        R ← first t out-links N+(v)
        S ← S ∪ (v)
    end if
    P ← P ∪ R
    if P = ∅ then
        P ← S
        S ← ∅
    end if
```

it is based on [https://chato.cl/papers/castillo_06_controlling_queue_size_web_crawling.pdf](https://chato.cl/papers/castillo_06_controlling_queue_size_web_crawling.pdf)


### Usage

Create a virtual environment
```python
python3 -m venv env
```

Activate virtual environment POSIX (bash)
```python
source <venv>/bin/activate
```
or 

Activate virtual environment Windows (Powershell)
```python
PS C:\> <venv>\Scripts\Activate.ps1
```

Install dependencies
```python
pip3 install -r requirements.txt
```

Create contacts
```python
python3 atac.py scrape -u url_to_scrape
```

Send Email to contacts created above
```python
python3 atac.py email -p path_to_csv -m path_to_message -s subject
```

Send IRC
```python
python3 atac.py irc

See Motivation for more details](MOTIVATION.md)
