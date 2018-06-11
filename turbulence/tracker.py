'''
    Script for importing csv file produced from turb.py, and tracking individual particles
    in specific selectrion of frames/ areas of a scene. 

    Goals:
    - Inputs
        - Import csv files of relevance
        - Request frames desired. 
            - determine through request, hard code, interactive, config file, etc.
        - Hard code relevant region. 
            - Potentially make this requested, but better to default to hard code as relatively consistent range
    - Processing
        - Limit to particle size/ mass in order to limit too much. Might need added turb.py parameter and re-process
        - Track movement of particle frame by frame, and store path
    - Output
        - Output image file consisting of the path the particle follows
        - Dialog asking where to save it? Or hard code? --> probably more likely in the plots folder already put in place.

'''

def main():
    return



if __name__ == '__main__':
    main()