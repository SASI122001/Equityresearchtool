import matplotlib.pyplot as plt

def plot_price_series(price_df, title="Price History"):
    fig, ax = plt.subplots()
    price_df.plot(ax=ax)
    ax.set_title(title)
    return fig

def plot_cumulative_returns(cumret, title="Cumulative Returns"):
    fig, ax = plt.subplots()
    cumret.plot(ax=ax)
    ax.set_title(title)
    return fig
