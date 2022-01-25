import argparse
import logging

import sbol3

import sbol_utilities.package
from sbol_utilities.workarounds import type_to_standard_extension

def define_module(doc: sbol3.Document):
    """Function to take an sbol document, check if it is a module, and create
    a new sbol document with the module definition included

    Args:
        doc (sbol3.Document): The document to be checked for a module

    Return
        doc (sbol3.Document): The document with the added module info
    """
    # Call check_namespace
    logging.info('Checking namespaces')
    is_module, module_namespace = check_namespaces(doc)
    logging.info(f'SBOL Document is a Module: {is_module}')

    # If all namespaces are the same, add module and save as new file
    if is_module:
        # TODO: Check if the file already has a module defined, if so, abort

        # Get list of identities of all top level objects 
        all_identities = [o.identity for o in doc.objects]

        # Define the module
        module = sbol_utilities.package.sep_054.Module(module_namespace + '/module')

        # All top level objects are members
        module.members = all_identities

        # Namespace must match the hasNamespace value for all of its members
        module.namespace = module_namespace

        # Add the module to the document
        doc.add(module)

        # Return the doc
        return(doc)
        

def check_namespaces(doc: sbol3.Document):
    """ Check if the namespaces of all top level objects are the same

    Args:
        doc (sbol3.Document): Document containing top level objects

    Returns:
        is_module (boolean): True if all namespaces are the same
        namespace (string): Namespace of the module
    """

    # Get a list of all namespaces
    all_namespaces = [o.namespace for o in doc.objects]

    # Check all namespaces are the same
    is_module = all(x == all_namespaces[0] for x in all_namespaces)

    # Get the first namespace to pass the string
    # Which position you pick won't matter if it is a module
    namespace = all_namespaces[0]

    return is_module, namespace

def main():
    """
    Main wrapper: read from input file, invoke check_namespace, then write to 
    output file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('sbol_file', help="SBOL file used as input")
    parser.add_argument('-o', '--output', dest='output_file', default='out',
                        help="Name of SBOL file to be written")
    parser.add_argument('-t', '--file-type', dest='file_type',
                        default=sbol3.SORTED_NTRIPLES,
                        help="Name of SBOL file to output to (excluding type)")
    parser.add_argument('--verbose', '-v', dest='verbose', action='count', 
                        default=0,
                        help="Print running explanation of expansion process")
    args_dict = vars(parser.parse_args())

    # Extract arguments:
    verbosity = args_dict['verbose']
    log_level = logging.WARN if verbosity == 0 \
        else logging.INFO if verbosity == 1 else logging.DEBUG
    logging.getLogger().setLevel(level=log_level)
    output_file = args_dict['output_file']
    file_type = args_dict['file_type']
    sbol_file = args_dict['sbol_file']
    extension = type_to_standard_extension[file_type]
    outfile_name = output_file if output_file.endswith(extension) \
        else output_file+extension

    # Read file
    logging.info('Reading SBOL file '+sbol_file)
    doc = sbol3.Document()
    doc.read(sbol_file)

    # Call define_module
    new_doc = define_module(doc)

    # Write out the new file
    new_doc.write(outfile_name, file_type)
    logging.info('Module file written to '+ outfile_name)
    

if __name__ == '__main__':
    main()