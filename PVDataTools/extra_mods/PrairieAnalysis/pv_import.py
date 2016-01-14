#pv_import
#Last Edited: 08/10/14
#Daniel Galtieri

"""Module for importing Praire .csv files, either as a single file or as a folder of files. Also contains function
to allow for the conversion of a file or folder of files into a .h5 file
"""


import os
import pandas as pd
from . import pxml_parse as pxml
from glob import *


def import_vr_csv(filename, primary_div=1, secondary_div=1):
    """Reads voltage recording .csv file into a pandas dataframe. Will convert Primary and Secondary channels
    to appropriate values if those channels are in the file. Returns a dataframe
    """
    #loads csv file into pandas dataframe
    df = pd.read_csv(filename, skipinitialspace=True)
    #some files have a unit (ms) associate with Time, so just making the Time column name uniform
    df.rename(columns={df.columns[0]: 'Time'}, inplace=True)
    #convert time from ms to sec
    df.Time /= 1000
    #df.set_index('Time', inplace=True)

    #if the Primary and/or Secondary columns exist, divide data by associate
    #divisor to get the correct mV or pA values
    if "Primary" in df.columns:
        df.Primary /= primary_div
    if "Secondary" in df.columns:
        df.Secondary /= secondary_div

    return df


def import_ls_csv(filename):
    """Reads linescan profile .csv file into pandas dataframe.
    """

    #loads csv file into pandas dataframe
    df = pd.read_csv(filename, skipinitialspace=True)
    #renames column headers to remove "(ms)" from time headers
    df.rename(columns=lambda header: header.strip('(ms)'), inplace=True)
    #convert time from ms to sec by slicing every other column, since these are the time columns
    df.ix[:, ::2] /= 1000

    return df


def import_folder(folder):
    """Parses data folder with either single or many voltage recording and linescan profile files.
    Will return a dictionary with "voltage recording", "linescan" and "file attributes"keys associate
    with 2 dataframes and a dictionary (respective). If multiple files in folder the dataframes will
    be multidimensional where each file is a Sweep (Sweep0001 through Sweepn)
    """
    vr_xmls = glob(os.path.join(folder, '*VoltageRecording*.xml'))

    #if only one voltage recording xml in folder, checks to see if both voltage recording and linescan
    #profile files exist. Imports file(s) that exist. If either don't exist, None value returned for that key
    # if len(vr_xmls) == 1:
    #     file_vals = pxml.parse_vr(vr_xmls[0])
    #
    #     if file_vals['voltage recording file'] is not None and file_vals['linescan file'] is not None:
    #         vr_filename = os.path.join(folder, (file_vals['voltage recording file'] + '.csv'))
    #         ls_filename = os.path.join(folder, (file_vals['linescan file']))
    #         primary_divisor = file_vals['primary']['divisor']
    #         secondary_divisor = file_vals['secondary']['divisor']
    #
    #         df_vr = import_vr_csv(vr_filename, primary_divisor, secondary_divisor)
    #         df_ls = import_ls_csv(ls_filename)
    #
    #         return {'voltage recording': df_vr, 'linescan': df_ls, 'file attributes': file_vals}
    #
    #     elif file_vals['voltage recording file'] is not None:
    #         vr_filename = os.path.join(folder, (file_vals['voltage recording file'] + '.csv'))
    #         primary_divisor = file_vals['primary']['divisor']
    #         secondary_divisor = file_vals['secondary']['divisor']
    #
    #         df_vr = import_vr_csv(vr_filename, primary_divisor, secondary_divisor)
    #         df_ls = None
    #         return {'voltage recording': df_vr, 'linescan': df_ls, 'file attributes': file_vals}
    #
    #     elif file_vals['linescan file'] is not None:
    #         ls_filename = os.path.join(folder, (file_vals['linescan file']))
    #
    #         df_vr = None
    #         df_ls = import_ls_csv(ls_filename)
    #
    #         return {'voltage recording': df_vr, 'linescan': df_ls, 'file attributes': file_vals}

    #if multiple voltage recording xml files in folder loops through the list of files. Adds the Sweep index
    #as the first level index (by first making it a column and then converting that column to an index). Sweep
    #number is kept track with the counter variable. As above, checks to see that both the voltage recording
    #and line profile data files exist (gives None if doesn't exist). Append each dataframe to data_vr and
    ## data_ls lists and then concatenate to one large dataframe at the end because appending to a pandas
    #dataframe makes a copy of the dataframe, which becomes very slow with large data sets
    if any(vr_xmls):
        data_vr = []
        data_ls = []
        file_attr = {}
        output = {}
        counter = 1

        for file in vr_xmls:
            file_vals = pxml.parse_vr(file)

            if file_vals['voltage recording file'] is not None and file_vals['linescan file'] is not None:
                vr_filename = os.path.join(folder, (file_vals['voltage recording file'] + '.csv'))
                ls_filename = os.path.join(folder, (file_vals['linescan file']))
                primary_divisor = file_vals['primary']['divisor']
                secondary_divisor = file_vals['secondary']['divisor']

                df_vr = import_vr_csv(vr_filename, primary_divisor, secondary_divisor)
                df_ls = import_ls_csv(ls_filename)

                df_vr['Sweep'] = 'Sweep' + str(counter).zfill(4)
                df_ls['Sweep'] = 'Sweep' + str(counter).zfill(4)

                df_vr.set_index('Sweep', append=True, inplace=True)
                df_ls.set_index('Sweep', append=True, inplace=True)

                data_vr.append(df_vr.reorder_levels(['Sweep', None]))
                data_ls.append(df_ls.reorder_levels(['Sweep', None]))

                file_attr['File'+str(counter)] = file_vals

                counter += 1

            elif file_vals['voltage recording file'] is not None:
                vr_filename = os.path.join(folder, (file_vals['voltage recording file'] + '.csv'))
                primary_divisor = file_vals['primary']['divisor']
                secondary_divisor = file_vals['secondary']['divisor']

                df_vr = import_vr_csv(vr_filename, primary_divisor, secondary_divisor)
                df_vr['Sweep'] = 'Sweep' + str(counter).zfill(4)
                df_vr.set_index('Sweep', append=True, inplace=True)
                data_vr.append(df_vr.reorder_levels(['Sweep', None]))

                file_attr['File'+str(counter)] = file_vals

                counter += 1

            elif file_vals['linescan file'] is not None:
                ls_filename = os.path.join(folder, (file_vals['linescan file']))

                df_ls = import_ls_csv(ls_filename)
                df_ls['Sweep'] = 'Sweep' + str(counter).zfill(4)
                df_ls.set_index('Sweep', append=True, inplace=True)
                data_ls.append(df_ls.reorder_levels(['Sweep', None]))
                file_attr['File'+str(counter)] = file_vals
                counter += 1

        if data_vr:
            output["voltage recording"] = pd.concat(data_vr)
        elif not data_vr:
            output["voltage recording"] = None
        if data_ls:
            output["linescan"] = pd.concat(data_ls)
        elif not data_ls:
            output["linescan"] = None
        output["file attributes"] = file_attr

    else:
        output = {"voltage recording": None, "linescan": None, "file attributes": None}

    return output


def convert_folder_hdf5(folder, save_loc=None):
    if save_loc is None:
        save_loc = folder

    filename = os.path.split(folder)[-1]+'.h5'
    filepath = os.path.join(save_loc, filename)
    store = pd.HDFStore(filepath, format="table", complevel=9, complib='blosc')
    data = import_folder(folder)

    if data['voltage recording'] is not None:
        store['voltage_recording'] = data['voltage recording']
    if data['linescan'] is not None:
        store['linescan'] = data['linescan']

    store.root.attributes = data['file attributes']

    store.close()

    #return store
