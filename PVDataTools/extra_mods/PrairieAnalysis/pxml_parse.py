# pxml_parse
# Last Edited: 08/08/14
# Dan Galtieri
# -------------------------------------------------------------------------------------

"""The purpose of this module is to read Prairie XML files for VoltageRecording, VoltageOutput, and MarkPoints to pull
out import information from those xmls.

"""


from lxml import etree


def parse_vr(filename):
    """Returns the Primary unit/divisor, Secondary unit/divisor, sampling rate and recording duration. Returned as a
    dictionary with keys "primary", "secondary", "sampling", and "duration". Primary and Secondary values are contained
    in dictionaries with keys "unit" and "divisor"
    """

    tree = etree.parse(filename)
    #Returns elements with associated "Primary" and "Secondary
    primary = tree.xpath('.//Name[text()="Primary"]')
    secondary = tree.xpath('.//Name[text()="Secondary"]')
    #Gets the parent of these elements
    try:
        parent = (primary[0].getparent(), secondary[0].getparent())
    #in case people don't use capital letters for Primary and Secondary labels in PrairieView
    except IndexError:
        primary = tree.xpath('.//Name[text()="primary"]')
        secondary = tree.xpath('.//Name[text()="secondary"]')
        parent = (primary[0].getparent(), secondary[0].getparent())
    #Finds the unit element within parent
    unit = (parent[0].find('.//UnitName'), parent[1].find('.//UnitName'))
    #Finds the divisor element within parent
    divisor = (parent[0].find('.//Divisor'), parent[1].find('.//Divisor'))

    #dictionaries with primary and secondary values
    primary_val = {'unit': unit[0].text, 'divisor': float(divisor[0].text)}
    secondary_val = {'unit': unit[1].text, 'divisor': float(divisor[1].text)}
    #gets sampling rate
    sampling_val = float((tree.find('.//Rate')).text)
    #gets recording time, converts to sec
    duration_val = (float((tree.find('.//AcquisitionTime')).text))/1000

    #finds the voltage recording csv file name
    datafile = (tree.find('.//DataFile')).text
    #finds the linescan profile file name (if doesn't exist, will be None)
    ls_file = (tree.find('.//AssociatedLinescanProfileFile')).text

    #If ls_file is none this could mean that there is no linescan associate with that voltage recording file or that
    #the file passed to parse_vr is actually a LineScan data file and therefore should be passed to ls_file.
    #In that scenario there is no voltage recording data file, so vo_file is None
    if ls_file is None:
        if "LineScan" in datafile:
            ls_file = datafile
            vo_file = None
        elif "LineScan" not in datafile:
            vo_file = datafile
    else:
        vo_file = datafile

    return {'primary': primary_val, 'secondary': secondary_val, 'sampling': sampling_val, 'duration': duration_val,
            'linescan file': ls_file, 'voltage recording file': vo_file}
