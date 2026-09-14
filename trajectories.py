import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"
association = 'atp'

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

if association == 'atp':
    decades = [
        '70', '80', '90', '00', '10', '20'
    ]
    players = ['Andre Agassi', 'Jimmy Connors']
elif association == 'wta':
    decades = [
        '80', '90', '00', '10', '20'
    ]
    players = ['Martina Navratilova', 'Serena Williams']
else:
    raise Exception('Association {0} not supported!'.format(association))

files = [
    './tennis_{0}/{1}_rankings_{2}s.csv'.format(association, association, decade) for decade in decades
]

rankings_df = pd.concat([pd.read_csv(file, usecols=['ranking_date', 'rank', 'player']) for file in files])
rankings_df = rankings_df.rename(columns={'player': 'player_id'})

players_file = './tennis_{0}/{1}_players.csv'.format(association, association)
players_df = pd.read_csv(players_file, usecols=['player_id', 'name_first', 'name_last'])
players_df['name'] = players_df['name_first'] + ' ' + players_df['name_last']
players_df = players_df.drop(columns=['name_first', 'name_last'])

df = pd.merge(rankings_df, players_df, on='player_id')

df['ranking_date'] = pd.to_datetime(df['ranking_date'], format="%Y%m%d")

df = df[df['name'].isin(players)]
df = df[df['rank'] <= 5]

df = df.sort_values(by='ranking_date')

# Plotting
fig = px.line(df, x='ranking_date', y='rank', color='name')

# Show the plot
fig.show()
# fig.show()

fig = go.Figure()

for name, group in df.groupby('name'):
    cumulative_counts = group['rank'].value_counts().sort_index().cumsum()
    # if 1 not in cumulative_counts:
    #     continue
    # if cumulative_counts[1] < 10:
    #     continue
    fig.add_trace(
    go.Scatter(
        x=cumulative_counts.index, 
        y=cumulative_counts, 
        mode='markers', 
        name=name, 
        marker=dict(
            color=colors['blue'] if name == df['name'].iloc[0] else colors['orange'],
            size=10
        )
    )
)

fig.update_xaxes(dtick=1)

fig.update_layout(
    # title='Cumulative Count of Rank',
    xaxis=dict(title='Rank'),
    yaxis=dict(title='Cumulative Count'),
    legend=dict(
        title='Name'
    )
)

# fig.write_image(
#     './pdf/trajectories_{0}.pdf'.format(association),
#     width=1200, height=600, scale=1
# )

fig.show()
