# Design of the Python Data Store API

## API Needs

### Data Type: Stored Data Value (SDV)

![Stored Data Value](Stored_Data_Value.png)

### Data Type: Data Moniker

![Data Moniker](Data_Moniker.png)

### Get Data - Read Data from a Moniker or SDV

LabVIEW API uses a polymorphic VI. We probably need one Python 'Get Data' method for each data flavor?

![Get Data](Get_Data.png)

### Publish Data - Publish Data to the Data Store

LabVIEW API uses a polymorphic VI. We probably need one Python 'Publish Data' method for each data flavor?

![Publish Data](Publish_Data.png)

### Metadata Type: Measurement Metadata

![Measurement Metadata](Measurement_Metadata.png)

### Metadata Type: Session Metadata

![Session Metadata](Session_Metadata.png)


