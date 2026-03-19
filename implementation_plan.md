# Inflation Regret Calculator
- How much purchasing power is lost due to inflation?
- Inflation-adjusted value of money, future cost of current purchases


# Input Parameters
- Description of the financial decision (e.g., "Bought a car for R200,000 in 2015", "Purchase: R1200 headphones in 2026")
- Initial Amount (e.g.,  R200,000, 1200)
- Start Year (e.g., 2015, 2026)
- End Year (e.g., 2026, 2026)
- inflation rate (e.g., fetch from API to get historical inflation rates)

# Output:
- Future Cost: The amount that the initial money would be worth in the end year, adjusted for inflation.(eg: In 10 years, your $6.00 latte will cost $8.06 just to maintain the same value.)
- Purchasing Power Loss: The difference between the initial amount and the future cost, indicating how much value has been lost due to inflation.(eg: Your $6.00 latte has lost $2.06 in purchasing power over 10 years.)
- Regret Score: A score from 0 to 100 that quantifies the level of regret associated with the financial decision based on the future cost compared to the initial amount.(eg: If your $6.00 latte will cost $8.06 in 10 years, your regret score might be 34.)
- Insight: A surprising financial insight related to the input (e.g., "If you had invested that money instead, it could have grown to $X", "The cost of that daily coffee over 10 years is equivalent to a down payment on a car").

# Regret Score:
- A score from 0 to 100 that quantifies the level of regret associated with the financial decision.

> 0 = No regret, 100 = Maximum regret

| Score  | Meaning        |
| ------ | -------------- |
| 0–20   | Probably fine  |
| 20–50  | Mild regret    |
| 50–80  | Risky decision |
| 80–100 | High regret    |

Your score must be calculated using **at least TWO factors** relevant to the chosen regret category.

# Calculating the Output:
1. Calculate the Future Cost using the formula: 
   Future Cost = Initial Amount * (1 + inflation rate)^(End Year - Start Year)
2. Calculate the Purchasing Power Loss:
   Purchasing Power Loss = Future Cost - Initial Amount
3. Calculate the Regret Score:
   - If Future Cost <= Initial Amount: Regret Score = 0 (no regret)
   - If Future Cost > Initial Amount: Regret Score = (Purchasing Power Loss / Initial Amount) * 100 (scaled to 100)

# Design:
- The home page should have a 'Inflation Regret Calculator' title and an input segement with an output screen underneath it.
- The input segment should have fields for the description of the financial decision, initial amount, start year, end year, and a submit button.
- This dashboard should allow users to input the parameters and submit them to calculate the regret score.
- The calculations should be done in the flask application, and the results should be displayed on the same page without refreshing (using AJAX or similar technology).
- the output should be displayed under the input form, showing the future cost, purchasing power loss, regret score, and financial insight in a clear and visually appealing way (e.g., using charts or infographics to illustrate the impact of inflation over time).
- The input an output data for each calculation should be stored in a SQLite database using SQLAlchemy, allowing users to track their financial decisions and regrets over time.
- A history button should be at the top right corner. When clicked, it should take the user to a new page that displays a history of their past calculations, stored in the SQLite database. Each entry should show the description, initial amount, start year, end year, future cost, purchasing power loss, regret score, and the date of calculation. Users should also have the option to serach for entries as well as delete individual entries from their history.
- Make use of an external API to fetch historical inflation rates based on the start and end years provided by the user. This will ensure that the calculations are accurate and reflect real-world data. You can use APIs like [the World Bank API or any other reliable source for historical inflation data.](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=ZA)
- Make sure the theme is greean and white, with a clean and modern design. Use charts or infographics to visually represent the impact of inflation over time, making it easier for users to understand the financial implications of their decisions. The overall user experience should be intuitive and engaging, encouraging users to explore their financial regrets and learn from them.


## Technical Requirements
The project must include/use:
- **Flask**: For building the web application (At least two routes, e.g., home and result)
- **HTML/CSS**: For the user interface (Jinja2 templates for dynamic content)
- **SQLAlchemy + SQLite**: Store at least one piece of data (e.g., user inputs, calculated regret scores)
- **External API**: Use at least one external API to fetch relevant financial data (e.g., stock prices, inflation rates, exchange rates)
- **GitHub Repository**: Host your code on GitHub with a clear README and commit history

## "Judging Criteria"

| Category                 | Description                                |
| ------------------------ | ------------------------------------------ |
| Functionality            | App works and produces results             |
| Technical Implementation | Flask, API, and database used              |
| Financial Insight        | Does the app reveal something interesting? |
| Creativity               | Is the idea unique or surprising?          |
| Demo                     | Clear explanation and demonstration        |