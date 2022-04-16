import pandas as pd
import numpy as np
import lxml.html as lh
from lxml.html import parse
import requests

def addValueChart(df):
    draft_value_chart = pd.read_csv('draftValueChart.csv')
    predicted_values = []
    for row in df.values:
        actual_pick = int(row[1])
        dv_row = draft_value_chart.loc[draft_value_chart['Pick']==actual_pick]
        predicted_value = 1
        if dv_row.shape[0] < 1:
            predicted_value = 1
        else:
            predicted_value = dv_row.iloc[0]['Value']
        predicted_values.append(predicted_value)
    df['Predicted_Values'] = predicted_values
    return df

def main():
    years = ['2021','2020','2019','2018','2017']
    picks = []
    players = []
    wavs = []
    years2 = []
    positions = []
    colleges = []
    average_values = []
    for year in years:
        url = 'https://www.pro-football-reference.com/years/'+year+'/draft.htm'
        page = requests.get(url)
        doc = lh.fromstring(page.content)
        rows = doc.xpath("//table/tbody")[0]
        for row in rows:
            games_played = row[12].text_content()
            if (row[0].text_content()!='Rnd'):
                if(games_played != ''):
                    pick = row[1].text_content()
                    picks.append(pick)
                    player = row[3].text_content()
                    players.append(player)
                    weighted_approx_value = row[10].text_content()
                    wavs.append(weighted_approx_value)
                    average_value_per_year = (float(weighted_approx_value)/(2022-int(year)))
                    average_values.append(average_value_per_year)
                    years2.append(year)
                    position = row[4].text_content()
                    positions.append(position)
                    college = row[27].text_content()
                    colleges.append(college)
                else:
                    pick = row[1].text_content()
                    picks.append(pick)
                    player = row[3].text_content()
                    players.append(player)
                    weighted_approx_value = 0
                    wavs.append(weighted_approx_value)
                    average_value_per_year = (float(weighted_approx_value)/(2022-int(year)))
                    average_values.append(average_value_per_year)
                    years2.append(year)
                    position = row[4].text_content()
                    positions.append(position)
                    college = row[27].text_content()
                    colleges.append(college)
    data = {
        'Player': players,
        'Pick': picks,
        'Position': positions,
        'College': colleges,
        'Value': wavs,
        'Value/Year': average_values,
        'Year': years2
    }
    df = pd.DataFrame(data)
    df = addValueChart(df)
    team_conf_info = pd.read_csv('cfb_teams_to_conference.csv')
    conferences = []
    for row in df.values:
        player = row[0]
        college = str(row[3])
        if 'North Carolina St.' in college:
            college = 'NC State'
        if 'St.' in college:
            college = college.replace('St.', 'State')
        if 'Col.' in college:
            college = college.replace('Col.', 'College')
        if college == 'Mississippi':
            college = 'Ole Miss'
        college = college.replace('.','')
        conference_to_add = 'other'
        for conference in team_conf_info.columns:
            column = team_conf_info[conference]
            for row2 in column:
                if college == str(row2):
                    conference_to_add = conference
                    break
        conferences.append(conference_to_add)
    df['conference'] = conferences
   
    print(df)
    differnce_in_values = []
    for row in df.values:
        pred_value = row[7]
        actual_value_per_year = row[5]
        pred_value_per_year = 2.76348 + (pred_value*0.0026565)
        difference = actual_value_per_year - pred_value_per_year
        differnce_in_values.append(difference)
    df['actual value - pred value'] = differnce_in_values
    df.to_csv('draftInfoTotal.csv', index=False)
    return 0
if __name__ == "__main__":
    main()
