import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
pio.renderers.default = "browser"

colors = {
    'white': '#ffffff',
    'black': '#000000',
    'orange': '#e69f00',
    'skyblue': '#56b4e9',
    'bluishgreen': '#009e73',
    'yellow': '#f0e442',
    'blue': '#0072b2',
    'vermillion': '#d55e00',
    'reddishpurple': '#cc79a7'
}
colors_list = list(colors.values())

target_width_in = 5.875  
aspect_ratio = 3 / 1
target_height_in = target_width_in / aspect_ratio
width_px = target_width_in * 96
height_px = target_height_in * 96

def main(version, association, cutoff):
    extension_df = pd.read_csv('./extension/extension_{0}-{1}-{2}.csv'.format(version, association, cutoff))
    
    if association == 'atp':
        decades = ['70', '80', '90', '00', '10', '20']
    elif association == 'wta':
        decades = ['80', '90', '00', '10', '20']
    else:
        raise Exception('Association {0} not supported!'.format(association))

    files = [
        './tennis_{0}/{1}_rankings_{2}s.csv'.format(association, association, decade) for decade in decades
    ]

    rankings_df = pd.concat([pd.read_csv(file, usecols=['ranking_date', 'rank', 'player']) for file in files])
    rankings_df = rankings_df.rename(columns={'player': 'player_id'})

    players_file = './tennis_{0}/{1}_players.csv'.format(association, association)
    players_df = pd.read_csv(players_file, usecols=['player_id', 'name_first', 'name_last'])
    players_df['player_name'] = players_df['name_first'] + ' ' + players_df['name_last']
    players_df = players_df.drop(columns=['name_first', 'name_last'])

    weeks_df = pd.merge(rankings_df, players_df, on='player_id')
    weeks_df = weeks_df[weeks_df['rank'] <= cutoff]
    counts = weeks_df['player_id'].value_counts()

    pagerank_df = pd.read_csv('./pagerank/{0}_out_{1}-{2}.csv'.format(version, association, cutoff))

    extension_df['weeks'] = extension_df['player_id'].map(counts).fillna(0)
    extension_df = pd.merge(extension_df, pagerank_df[['player_id', 'rank']], on='player_id', how='left')
    extension_df = extension_df.rename(columns={'rank': 'pagerank'})

    wta_names = ["Steffi Graf", "Serena Williams", "Martina Navratilova"]
    atp_names = ["Roger Federer", "Novak Djokovic", "Rafael Nadal", "Jimmy Connors", "Andre Agassi"]
    names = wta_names if association == 'wta' else atp_names
        
    for y_col, method in zip(['weeks', 'pagerank'], ['traditional', 'pagerank']):        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=extension_df["avg_rank"],
            y=extension_df[y_col],
            mode='markers',
            showlegend=False,
            marker=dict(
                color='black',
                symbol='circle' if association == 'atp' else 'square', size=3
            )
        ))
        
        for i, name in enumerate(names):
            player_data = extension_df[extension_df["player_name"] == name]
            
            print(f"Player: {name}", f"Method: {method}", f"Value: {player_data[y_col].iloc[0]}")
            
            if not player_data.empty:
                fig.add_trace(go.Scatter(
                    x=player_data["avg_rank"],
                    y=player_data[y_col],
                    mode='markers',
                    name=name,
                    marker=dict(color=colors_list[i+2],
                        symbol='circle' if association == 'atp' else 'square', size=5)
                ))
        
        print(extension_df["pagerank"].iloc[-3] - extension_df["pagerank"].iloc[-1])
        
        fig.update_layout(
            xaxis_title='Average Rank',
            yaxis_title='Weeks as a Top Player' if method == 'traditional' else 'PageRank',
            margin=dict(b=60, l=10, r=10, t=10),
            width=width_px,
            height=height_px,
            font=dict(
                family="Serif",
                size=10
            )
        )
        
        fig.write_image(
            './compare_methods/compare_methods_{0}-{1}-{2}-{3}.pdf'.format(method, version, association, cutoff)
        )
        
if __name__ == '__main__':
    ver_l = ['nonadj']
    assc_l = ['atp', 'wta']
    ctff_l = [3, 5]

    for ver in ver_l:
        for assc in assc_l:
            for ctff in ctff_l:
                main(ver, assc, ctff)