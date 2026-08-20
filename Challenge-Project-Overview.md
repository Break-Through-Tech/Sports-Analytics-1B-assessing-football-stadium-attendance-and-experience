
# Assessing Football Stadium Attendance and Experience During the Regular Season

**Company / Org:** Other  
**Challenge Advisor:** Christina Coleman, coleman.chris.m@gmail.com.  
**AI Studio Coach:** Bhavya Gopal, bhavya.gopal@breakthroughtech.org.   
**Program:** Break Through Tech AI Studio - Fall 2026  

---

## 🏢 About Other
Other is an independent initiative focused on enhancing sports fan engagement through data-driven insights. By analyzing the intersection of infrastructure, weather, and fan sentiment, the organization aims to optimize the gameday experience and improve overall stadium attendance.

---

## 🎯 The Challenge
### Project Summary
College football stadiums vary widely in attendance from game to game. Some games fill nearly every seat, while others draw only a fraction of the stadium's capacity. In this project, you will use college football game, venue, and weather data to build a classification model that predicts whether a home game is likely to have high or low stadium attendance relative to capacity. The goal is to help colleges understand what factors contribute to a strong gameday turnout and use those insights to make strategic decisions that improve the fan experience.

### Success Criteria

- Understanding of agile/scrum methodologies (understands basic terminologies and ceremonies applied throughout duration of the program)
- Team can confidently explain why they made decisions they did to get the model to its end state along the way
- The "high-turnout" label is clearly defined, documented, and defended — you can explain why you drew the line where you did and what changes if you move it
- Have a technical and non-technical understanding of the solution and use case (i.e. if communicating to non-technical audiences/final presentation prep)
- Model successfully produces outputs

### Project Milestones
Use these milestones to guide your work. Your team will create a GitHub Projects board to track tasks within each milestone.

| Month | Milestone | Key Activities |
|---|---|---|
| August | Challenge Setup & Team Onboarding | • Finalize challenge brief and dataset<br>• Draft rubric/success criteria for "worth attending" scoring model<br>• Onboard student teams; walk through problem statement and data |
| September | Exploratory Data Analysis & Feature Engineering | • Teams complete exploratory data analysis (EDA) on the review dataset<br>• Data cleaning and feature engineering <br>• Checkpoint: teams present initial data insights |
| October | Baseline Modeling & Midpoint Review | • Baseline model development<br>• Midpoint check-in: model performance review, troubleshoot data gaps<br>• Begin iterating with sentiment components if using review text |
| November | Model Refinement & User-Facing Output | • Model refinement and validation<br>• Build out user-facing output (dashboard, score, or simple interface if necessary)<br>• Draft presentation/pitch narrative tying the model back to the business problem |
| December | Final Testing & Showcase | • Final testing<br>• Rehearse and deliver showcase presentation<br>• Submit final deliverable |

> **Note for the team:** Please create a GitHub Projects board in this repository to break these milestones into weekly tasks. Go to the **Projects** tab → **New project** → Choose **Board** → Add columns for each month.

---

## 📊 Dataset
**Name and Source:** College Football Data (CFBD) API — https://collegefootballdata.com

- **Format:** JSON via API (exportable to CSV)
- **Access:** Free API key at https://collegefootballdata.com/key — **register with your `.edu` email** for the Academic tier
- **Documentation:** https://api.collegefootballdata.com
- **Python client:** https://github.com/CFBD/cfbd-python
- **No-code CSV export:** https://collegefootballdata.com/exporter

### Optional sources to explore

- **Kaggle** — [College Football Games 2000–2018](https://www.kaggle.com/datasets/jeffgallini/college-football-attendance-2000-to-2018), [CFB Attendance Data](https://www.kaggle.com/datasets/nilnomics/cfb-attendance-data), [College Sports Arenas](https://www.kaggle.com/datasets/nilnomics/college-sports-arenas). Useful for exploring on day one while API keys are pending.
- [**Open-Meteo**](https://open-meteo.com/en/docs/historical-weather-api) — Free historical weather
- [**IPEDS**](https://nces.ed.gov/ipeds/) — Free federal data on undergraduate enrollment by institution. Student body size is a real attendance driver and CFBD does not include school-level enrollment data.
- [**Census ACS**](https://www.census.gov/data/developers/data-sets/acs-5year.html) — Local population and median income by county/metro.
- [**NCAA official attendance reports**](https://www.ncaa.org/sports/2013/11/19/ncaa-football-attendance.aspx) — Annual PDFs back to 1998. Aggregate rather than per-game, but useful for sanity-checking your numbers.

---

## 🛠️ Suggested Approach

**ML Problem Type:** Binary Classification

**Recommended Libraries:**
- cfbd, pandas, scikit-learn, matplotlib/seaborn, shap (explainability)

**Evaluation Metrics:**
- Accuracy, Precision/Recall, AUC-ROC, Confusion Matrix
  
---

## 📚 Resources to Get Started

The following resources will help your team understand the problem space and potential technical approaches for this project:

**Background Reading:**
- Attendance and experience shape team business strategies — Similar business tactics could potentially be applied to college football team strategies: https://www.sportsbusinessjournal.com/Articles/2024/08/12/business-of-football/
- Understanding factors beyond price, team performance, and weather — Explore how qualitative fan experience and other factors may influence attendance:
  - NFL perspective: https://www.reddit.com/r/NFLv2/comments/1u6fwgo/how_often_do_you_go_to_nfl_games_in_person/ 
  - College football perspective: https://www.reddit.com/r/CFB/comments/1pvfkfp/fbs_game_attendance_by_city_population/ 
- [College Football Attendance: A Panel Study of the Football Bowl Subdivision](https://www.tandfonline.com/doi/abs/10.1080/00036846.2013.866208) (Applied Economics)
- [Does College Football Have an Attendance Problem?](https://athleticdirectoru.com/articles/does-college-football-have-an-attendance-problem/)
- [Attendance Drops for College Football](https://www.npr.org/2019/08/24/753962604/attendance-drops-for-college-football) — NPR

**Technical Tutorials:**

- [CFBD API Getting Started](https://api.collegefootballdata.com/) — Key setup and first request
- [cfbd-python on GitHub](https://github.com/CFBD/cfbd-python) — Official Python client with per-endpoint documentation

**Other:**

- [CFBD Discord](https://discord.gg/Eb3ex5a) — Active community and a useful place to ask data-related questions

*Feel free to explore beyond these, and share anything interesting you find with me!b I'm also happy to give an overview of the business or answer any questions you may have.*

---

## 🤝 How We'll Work Together

**Official check-ins:** During our biweekly 45-minute AI Studio Lab Section meeting block (2nd and 4th week of every month)

 **Other ways to reach out to me with questions:** 
* Email (best method): coleman.chris.m@gmail.com
* Note: I typically respond within 24 hours or less. Please reach out to Bhavya (your AI Studio Coach) with urgent questions.

---

## 🚀 Getting Started

1. **Review this overview document** and note any questions for our first meeting
2. **Begin reviewing the dataset** using the link above
3. **Read the GitHub Projects documentation** [here](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)

I’m excited to work with you!

---

## ❓ Questions?

Please bring any questions to our first meeting during the week of August 24th (Break Through Tech’s Bridge to Studio - Session C). 
