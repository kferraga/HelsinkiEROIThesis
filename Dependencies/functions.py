# Functionality for adjusting GeRS-DeMo results, acquiring PER YEAR and
# SUM YEARS production results for coal, gas, and oil, and calculating the exploitation ration and EROI.

# Got warnings for future depreciation of panda actions, but as this was not expected to cause issues for the timeline of this thesis, they were ignored for Jupyter readability. Used late 2024 versions for Python 3.12. If preformed later and there is an issue with pandas, this may need to be handled.
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
# For general data preparation/wrangling.
import pandas as pd
# Court & Fizaine's constants for the exploitation ratio
from Dependencies import constants as c
# For numpy exponential functions
import numpy as np
# For merging pandas dataframes together for a coordinated result.
import functools

def gersdemo_prepare_results(results_df):
    """
    Preforms the initial data-sorting work on the file outputted from GeRS-DeMO.
    :param results_df: A pandas dataframe of the outputted results.
    :return: The adjusted results_df.
    """
    results_df = results_df.T
    results_df = results_df.fillna(0)
    results_df.columns = results_df.iloc[0]
    results_df = results_df[1:]
    results_df.reset_index(drop=True, inplace=True)
    return results_df


def gersdemo_pre_prod_calc(results_df, clean=True, name_adj="", prod_type=""):
    """
    Preparatory code that is shared between the PER YEAR and SUMMED YEARS production calculations for coal, gas, and oil.
    :param prod_type: The type of production to add onto the output frame. For this code, either " Prod" or " Sum Prod".
    :param results_df: A pandas dataframe of the outputted results.
    :param clean: Indicates whether the results_df should be cleaned with gersdemo_prepare_results. Do this if you just got an output from the model.
    :param name_adj: An adjustment to the column name (i.e. "German Coal Prod" instead of "Coal Prod"). Does not include a space.
    :return: A list of outputs necessary for the calculation of coal, gas, and oil production alongside the base output dataframe.
    """
    # Results setup. Done to create a cleaned dataframe that puts the columns as the attributes and years, and that changes all NA values to 0, since the model outputs no production as NA.
    if clean:
        results_df = gersdemo_prepare_results(results_df)

    # An output dataframe which includes the year and production for coal, gas, and oil. Done to allow for easier summation mathematics.
    output_df = pd.DataFrame(
        columns=["Year", name_adj + "Coal" + prod_type, name_adj + "Gas" + prod_type, name_adj + "Oil" + prod_type])

    # Finding the first numeric column in the dataset, then getting its location. This is done to ensure that, if a change was made to the dataframe, the code would still start at the first year of production XXXX.
    first_numeric_col = results_df.apply(pd.to_numeric, errors='coerce').notna().any().idxmax()
    first_col_index = results_df.columns.get_loc(first_numeric_col)
    years = results_df.columns[first_col_index:]

    coal_data = results_df[results_df['mineral'] == 'Coal']
    gas_data = results_df[results_df['mineral'] == 'Gas']
    oil_data = results_df[results_df['mineral'] == 'Oil']

    return first_col_index, years, coal_data, gas_data, oil_data, output_df


def gersdemo_prod_results(results_df, clean=True, name_adj=""):
    """
    The production for coal, gas, and oil on a PER YEAR basis in exojoules (EJ). I.e., 1950 will
    only display the EJ production for 1950 per resource.
    :param results_df: A pandas dataframe of the outputted results.
    :param clean: Indicates whether the results_df should be cleaned with gersdemo_prepare_results. Do this if you just got an output from the model.
    :param name_adj: An adjustment to the column name (i.e. "German Coal Prod" instead of "Coal Prod"). Does not include a space.
    :return: A pandas dataframe with the year and individual coal, gas, and oil production results.
    """
    prod_type = " Prod"
    first_col_index, years, coal_data, gas_data, oil_data, output_df = gersdemo_pre_prod_calc(prod_type=prod_type,
                                                                                              results_df=results_df,
                                                                                              clean=clean,
                                                                                              name_adj=name_adj)

    # Loops through each year in the total model years, creates a year dataframe, and then concats that onto the output dataframe. This is done to allow for easy summation per year, where each year is the sum of it and the previous years production.
    for i, year in enumerate(years):
        i_adj = i + first_col_index

        year_prod = pd.DataFrame.from_dict({
            "Year": [int(year)],
            name_adj + "Coal" + prod_type: [coal_data.iloc[:, i_adj].sum()],
            name_adj + "Gas" + prod_type: [gas_data.iloc[:, i_adj].sum()],
            name_adj + "Oil" + prod_type: [oil_data.iloc[:, i_adj].sum()]
        })
        output_df = pd.concat([output_df, year_prod], ignore_index=True)

    return output_df


def gersdemo_summed_results(results_df, clean=True, name_adj=""):
    """
    The production for coal, gas, and oil on a SUMMED YEARS basis in exojoules (EJ). I.e., 1950 will  display the EJ production for 1950 and *all prior years* per resource.
    :param results_df: A pandas dataframe of the outputted results.
    :param clean: Indicates whether the results_df should be cleaned with gersdemo_prepare_results. Do this if you just got an output from the model.
    :param name_adj: An adjustment to the column name (i.e. "German Coal Prod" instead of "Coal Prod"). Does not include a space.
    :return: A pandas dataframe with the year and individual coal, gas, and oil production results.
    """
    prod_type = " Sum Prod"
    first_col_index, years, coal_data, gas_data, oil_data, output_df = gersdemo_pre_prod_calc(prod_type=prod_type,
                                                                                              results_df=results_df,
                                                                                              clean=clean,
                                                                                              name_adj=name_adj)

    # Initializing cumulative sums and dataframes for Coal, Gas, and Oil, since there three need to be seperated before column summation.
    coal_cumsum = 0
    gas_cumsum = 0
    oil_cumsum = 0

    # Loops through each year in the total model years, creates a year dataframe, and then concats that onto the output dataframe. This is done to allow for easy summation per year, where each year is the sum of it and the previous years production.
    for i, year in enumerate(years):
        i_adj = i + first_col_index
        coal_cumsum += coal_data.iloc[:, i_adj].sum()
        gas_cumsum += gas_data.iloc[:, i_adj].sum()
        oil_cumsum += oil_data.iloc[:, i_adj].sum()

        year_prod = pd.DataFrame.from_dict({
            "Year": [int(year)],
            name_adj + "Coal" + prod_type: [coal_cumsum],
            name_adj + "Gas" + prod_type: [gas_cumsum],
            name_adj + "Oil" + prod_type: [oil_cumsum]
        })
        output_df = pd.concat([output_df, year_prod], ignore_index=True)

    return output_df

def exploitation_ratio_adjusted(prod_df):
    """An estimate of the exploitation ratio of a fossil fuel calculated through and based on Court and Fizaine's historical data. This follows a logistical growth/sigmoid function, and is used in the theoretical predictions of EROI (see 4.14 in the thesis).
    :param prod_df: A pandas dataframe of SUMMED YEARS result (gersdemo_summed_results).
    :return: The ratio of exploited resources per year (essentially, sum what has been produced over total predicted production over all time)."""
    output_df = pd.DataFrame(columns=["Year", "Coal p", "Gas p", "Oil p"])

    def _exploitation_ratio_eq(year, resource_type):
        """Calculation of the adjusted exploitation ratio, located at 4.14 in the thesis."""
        try:
            cur_year_sum_prod = float(prod_df.loc[base_d_sum_prod["Year"]==year-1][resource_type + " Sum Prod"])
        except Exception as e:
            # Done since the first loc command would not exist and the result should be 0.
            cur_year_sum_prod = 0
        total_sum = prod_df[resource_type + " Sum Prod"].iloc[-1]
        return cur_year_sum_prod/total_sum

    # Creating the dataframe by calculating the exploitation ratio eq for each year.
    for i in range(len(prod_df.index)):
        cur_year = prod_df["Year"][i]
        year_exploitation_ratio = pd.DataFrame.from_dict({
            "Year": [cur_year],
            "Coal p": [_exploitation_ratio_eq(cur_year, "Coal")],
            "Gas p": [_exploitation_ratio_eq(cur_year, "Gas")],
            "Oil p": [_exploitation_ratio_eq(cur_year, "Oil")]
        })
        output_df = pd.concat([output_df, year_exploitation_ratio], ignore_index=True)
    return output_df

def resource_fossil_EROI(expl_ratio_df):
    """
    The calculation of the EROI value per coal, gas, and oil. Sec 4.1.1 and 4.3 shine more light on the basis for the EROI equation, but in summary: it combines the physical depletion and technological improvements of the related resource with respect to the amount of that resource already exploited.
    :param expl_ratio_df: The exploitation ratio dataframe calculated from exploitation_ratio_adjusted.
    :return: A dataframe of the EROI on a per year basis.
    """
    output_df = pd.DataFrame(columns=["Year", "Coal EROI", "Gas EROI", "Oil EROI"])
    coal_resource_dict = getattr(c, "Coal")
    oil_resource_dict = getattr(c, "Oil")
    gas_resource_dict = getattr(c, "Gas")

    def _resource_fossil_EROI_eq(resource_er_value, resource_dict):
        """
        EROI equation which uses the Court and Fizaine EROI eq (Sec 4.1.1) with the resource exploitation eq adjusted for time and predicted total production (Sec 4.3).
        """
        return ((resource_dict["in"] +
                 ((1 - resource_dict["in"]) / (
                          1 + np.exp(
                      -resource_dict["tl"] * (resource_er_value - resource_dict["me"]))))) *
                 np.exp(-resource_dict["rd"] * resource_er_value) *
                resource_dict["sf"])

    for i in range(len(expl_ratio_df.index)):
        cur_year = expl_ratio_df["Year"][i]
        year_exploitation_ratio = pd.DataFrame.from_dict({
            "Year": [cur_year],
            "Coal EROI": [_resource_fossil_EROI_eq(expl_ratio_df["Coal p"][i], coal_resource_dict)],
            "Gas EROI": [_resource_fossil_EROI_eq(expl_ratio_df["Gas p"][i], gas_resource_dict)],
            "Oil EROI": [_resource_fossil_EROI_eq(expl_ratio_df["Oil p"][i], oil_resource_dict)]
        })
        output_df = pd.concat([output_df, year_exploitation_ratio], ignore_index=True)
    return output_df


def net_energy_results(results_df, EROI_results, clean=True):
    """
    A calculation of the net energy produced for coal, gas, and oil on a PER YEAR basis. Functionally this is a modification of the PER YEAR total energy production with the predicted EROI per year on the original dataset.

    Still needs to be run under prod or sum results calc for per resource results.
    :param results_df: A pandas dataframe of the outputted results.
    :param EROI_results: The EROI results dataframe which includes the per year EROI for coal, gas, and oil.
    :param clean: Indicates whether the results_df should be cleaned with gersdemo_prepare_results. Do this if you just got an output from the model.
    :return: A cleaned dataframe similar to gersdemo_prepare_results which is adjusted by EROI.
    """

    # Need less values from the setup eq for net energy.
    first_col_index, years, _, _, _, _ = gersdemo_pre_prod_calc(results_df=results_df, clean=clean)

    def _get_resource_dataframe(resource):
        """Runs the net energy calculation for coal, gas, and oil individually. Locates the EROI value then applies it to the columns production."""
        resource_data = results_df[results_df['mineral'] == resource]
        for i, year in enumerate(years):
            i_adj = i + first_col_index
            resource_eroi_value = EROI_results.loc[EROI_results['Year'] == int(year), resource + ' EROI'].iloc[0]
            resource_data.iloc[:, i_adj] = resource_data.iloc[:, i_adj] * (1 - 1 / resource_eroi_value)
        return resource_data

    net_energy_df = pd.concat(
        [_get_resource_dataframe("Coal"), _get_resource_dataframe("Gas"), _get_resource_dataframe("Oil")],
        ignore_index=True)

    return net_energy_df

def get_result_dataframes(loc, sheet_name):
    """
    Given the location of a results spreadsheet from GeRS-DeMo and the relevant sheet, return all calculation results to be used in future visualizations.
    :param loc: The location of the spreadsheet in the files.
    :param sheet_name: The name of the sheet (i.e. Dynamic_BG for Dynamic_BG_results).
    :return: direct_output - the original output from basic pandas operations;
    cleaned_output - a cleaned spreadsheet for use programatically;
    yearly_prod - the PER YEAR production for coal, gas, and oil;
    sum_years_prod -  the SUMMED YEARS production for coal, gas, and oil;
    net_yearly_prod - the net PER YEAR production for coal, gas, and oil;
    net_sum_years_prod - the net SUMMED YEARS production for coal, gas, and oil;
    exploitation_ratio - the exploitation ratio calculated for use in the EROI equation for coal, gas, and oil;
    EROI - the EROI calculated PER YEAR for coal, gas, and oil;
    general_output - a combination of yearly production, net sum years production, and EROI.
    """
    direct_output = pd.read_excel(loc, sheet_name, header=None)
    sum_years_prod = gersdemo_summed_results(direct_output)
    yearly_prod = gersdemo_prod_results(direct_output)
    exploitation_ratio = exploitation_ratio_adjusted(sum_years_prod)
    EROI = resource_fossil_EROI(exploitation_ratio)

    cleaned_output = gersdemo_prepare_results(direct_output)
    net_yearly_prod = net_energy_results(cleaned_output, EROI, clean=False)
    net_sum_years_prod = gersdemo_prod_results(net_yearly_prod, clean=False)

    general_output = functools.reduce(lambda left, right: pd.merge(left, right, on='Year'),
                                      [yearly_prod, net_sum_years_prod, EROI])

    return direct_output, cleaned_output, yearly_prod, sum_years_prod, net_yearly_prod, net_sum_years_prod, exploitation_ratio, EROI, general_output
