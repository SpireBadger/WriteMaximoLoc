# Project: Lat/Lon from Maximo
# Create Date: UNK
# Last Updated: 07/02/2020
# Create by: Michael Bartlett
# Updated by: Robert Domiano
# Purpose: To write the latitude/longitude and working district of services
#           from maximo data.
# ArcGIS Version:   ---
# Python Version:   3.6
# For a changelog of updates, visit the github at: https://github.com/SpireBadger/WriteMaximoLoc
# -----------------------------------------------------------------------

# Import Modules
import arcpy, datetime, sys

# Set workspace
arcpy.env.workspace = r"C:\Users\08957\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\New Prod stl-pgisdb-23.lac1.biz (PGIS3).sde"

# Temp Workspace for script testing
#tempWs = r'C:\Scripts\MaximoLocationWrite\PGIS3.sde'
#arcpy.env.workspace = tempWs

# Set base file
# This is the test file, should be deleted or commented out in final code
#filename = r'C:\Scripts\MaximoLocationWrite\MxLocationCentroids.csv'
filename=r"\\tdatfile01\Test_DW\GIS\MxLocationCentroids\\MxLocationCentroids.csv"
#filename=r"\\pdatfile01\Prod_DW\GIS\\MxLocationCentroids.csv"

# Feature class name
#fc = "LGC_GAS.GasValve"
fc = "LGC_GAS.DistributionMain"
#sr = arcpy.SpatialReference(3785)

def WriteLonLatToFile(fc):
    # Get feature class name
    fcName = arcpy.Describe(fc).Name
    # Print Current feature class
    print( fcName)
    # Get spatial reference from FC 
    srIn = arcpy.Describe(fc).SpatialReference
    # Print existing spatial reference
    print ("Input SR is {}".format(srIn.name))

    # Set desired spatial reference
    srOut  = arcpy.SpatialReference(4326) # GCS_WGS84
    # Print output
    print ("Output SR is {}".format(srOut.name))
    # Open a text file to write to
    fo= open(filename,"a")
    # Create blank list
    myOutput = [""]
    # Write list to open file
    fo.writelines(myOutput)
    # Set count var
    iCnt = 0
    # open search cursor and start loop
    for row in arcpy.da.SearchCursor(fc, ["MXLOCATION","SHAPE@", "OBJECTID"]):
        # Get count and row vars
        iCnt = iCnt + 1
        mxLoc = row[0]
        geom = row[1]
        
        # Test code in try/except
        try:
            # Project geometry to set spatial reference
            geom2 = geom.projectAs(srOut)
            # Obtain X, Y
            x2, y2 = geom2.centroid.X, geom2.centroid.Y
            xa, ya = geom.centroid.X, geom.centroid.Y
            
            # Create feature layers to select from for picking the working location
            # Variable names
            workLoc = "MXSPAT.WorkingDistricts"
            workLocLyrName = "WorkingLocations"
            # Delete feature layers if already existing
            if arcpy.Exists("Select_Layer"):
                arcpy.Delete_management("Select_Layer")
            if arcpy.Exists(workLocLyrName):
                arcpy.Delete_management(workLocLyrName)

            # Create a point from xy pre-projection
            point = arcpy.Point(xa, ya)
            # Create a point geometry to create feature layers from
            pointGeo = arcpy.PointGeometry(point)
            # Copy geometry to an in memory feature class
            memPoint = "in_memory" + "\\" + "pointLyr"
            # Delete if already existing
            if arcpy.Exists(memPoint):
                arcpy.Delete_management(memPoint)
            # Create in memory copy of feature class in order to make feature layer
            pointFC = arcpy.CopyFeatures_management(pointGeo, memPoint)
            # Create feature layers
            pointLyr = arcpy.MakeFeatureLayer_management(pointFC,"Select_Layer")
            workLyr = arcpy.MakeFeatureLayer_management(workLoc,workLocLyrName)
            
#           #Select the working district layer if it contains new point layer
            arcpy.SelectLayerByLocation_management(workLyr, "CONTAINS", pointLyr)
            
            # Start second cursor in with statement so it auto deletes
            with arcpy.da.SearchCursor(workLyr, "WORKINGDISTRICT") as cursorB:
                # Iterate through selected row (should always be 1 feature)
                for r in cursorB:
                    # Print the district. This print statement is to verify there is 1 feature.
                    print("The Working District is {0}.".format(r))
                    # Save row to variable
                    workDistName = r
            # Print what will be appended to text file.
            print("{}, {}, {:6f}, {:6f}, {}, {} \n".format(mxLoc, fcName, x2, y2, iCnt, workDistName))
            # Append output to list to be written to text file.
            myOutput.append("{}, {}, {:6f}, {:6f}, {}, {} \n".format(mxLoc, fcName, x2, y2, iCnt, workDistName))
            
#            del pointLyr, workLyr, pointFC
            #myOutput.append("\n")
        except:
            # Output errors then break loop
            tb = sys.exc_info()
            arcpyError = arcpy.GetMessages(2)
            print("Errors include {0} and {1}.".format(tb, arcpyError))
            break
#            print("{}, {}, Invalid Shape, \n".format(mxLoc, fcName))
            
    # Print how many features counted
    print(str(len(myOutput)) + " - " + str(iCnt))
    # Write output
    fo.writelines(myOutput)
    # Close file
    fo.close()

# Print datetime
print(datetime.datetime.now())
# Open text file
fo= open(filename,"w")
# Write headers
fo.write("Location,FeatureType,X,Y,FeatCnt \r\n")
# close text file
fo.close

# Features to be read
fcList = ["MXSPAT.LargeDiameterCastIron","LGC_GAS.ServicePoint","LGC_GAS.Service","LGC_GAS.DistributionMain", "LGC_GAS.CPTestPoint","LGC_GAS.DetailPages","MXSPAT.EasementAgreements","LGC_GAS.GasValve","LGC_GAS.ThreeYearMobile","LGC_GAS.Drip","MXSPAT.ExposedFacility","MXSPAT.TransmissionCrossingPatrol","LGC_GAS.ThreeYearMobile","LGC_GAS.BusinessDistrict","MXSPAT.TransmissionLine","LGC_GAS.AnnualMobile","MXSPAT.OxyacetyleneWeld","MXSPAT.FeederLine","LGC_GAS.SpireOffice"]
# Iterate through list, use definition
for fc in fcList:
    # Write to file
    WriteLonLatToFile(fc)
    # Print current date
    print(datetime.datetime.now())	
# Close file
fo.close()

   