"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    departments = departments.rename(columns={
        'region_code': 'code_reg',
        'code': 'code_dep',
        'name': 'name_dep'
    })
    merged = pd.merge(departments, regions, on='code_reg', how='left')

    return merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum.rename(columns={'Department code': 'code_dep'})

    # Merge on department code
    merged = pd.merge(referendum, regions_and_departments, on='code_dep', how='inner')

    # Filter out DOM-TOM-COM and abroad using department codes.
    # Typically DOM/TOM/COM have codes starting with '97', '98', or '99', etc.
    merged = merged[~merged['code_dep'].str.startswith(('97', '98', '99'))]

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols_to_sum = ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']

    # Group by region
    agg_df = referendum_and_areas.groupby(['code_reg', 'name_reg'])[cols_to_sum].sum().reset_index()

    # Set index to code_reg
    agg_df = agg_df.set_index('code_reg')

    return agg_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    regions_gdf = gpd.read_file("data/regions.geojson")

    # Merge with referendum results (reset index first to have code_reg as a column)
    merged = regions_gdf.merge(
        referendum_result_by_regions.reset_index(),
        left_on='code', right_on='code_reg', how='left'
    )

    # Compute the ratio: Choice A over Choice A + Choice B
    merged['ratio'] = merged['Choice A'] / (merged['Choice A'] + merged['Choice B'])

    ax = merged.plot(
        column='ratio',
        legend=True,
        cmap='RdBu',
        scheme='quantiles',
        k=5,
        edgecolor='black',
        linewidth=0.5,
        figsize=(10, 8)
    )
    ax.set_title("Referendum Results: Choice A Ratio by Region", fontsize=16)
    ax.axis('off')

    return merged


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()

