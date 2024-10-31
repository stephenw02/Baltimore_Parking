from django.db import models

# Create your models here.
class ProcessedDataLog(models.Model):
    dataset_name = models.CharField(max_length=255)  # Name of the dataset (for extensibility)
    last_object_id = models.BigIntegerField(null=True, blank=True)  # Store the latest processed objectId
    updated_at = models.DateTimeField(auto_now=True)  # Track when the object ID was last updated

    def __str__(self):
        return f"{self.dataset_name} - Last object ID: {self.last_object_id}"
    

class TowingRecord(models.Model):
    PropertyNumber = models.CharField(max_length=100, null=True, blank=True)
    TowedDateTime = models.BigIntegerField(null=True, blank=True)  # Store as a string if not handling as a DateTime field
    PickupType = models.CharField(max_length=50, null=True, blank=True)
    VehicleType = models.CharField(max_length=50, null=True, blank=True)
    VehicleYear = models.CharField(max_length=4, null=True, blank=True)
    VehicleMake = models.CharField(max_length=100, null=True, blank=True)
    VehicleModel = models.CharField(max_length=100, null=True, blank=True)
    VehicleColor = models.CharField(max_length=50, null=True, blank=True)
    TagNumber = models.CharField(max_length=50, null=True, blank=True)
    TagState = models.CharField(max_length=50, null=True, blank=True)
    TowCompany = models.CharField(max_length=255, null=True, blank=True)
    TowCharge = models.CharField(max_length=100, null=True, blank=True)
    TowedFromLocation = models.CharField(max_length=255, null=True, blank=True)
    HowTowed = models.CharField(max_length=50, null=True, blank=True)
    SlingUsed = models.CharField(max_length=50, null=True, blank=True)
    DollyUsed = models.CharField(max_length=50, null=True, blank=True)
    rollBackUsed = models.CharField(max_length=50, null=True, blank=True)
    pinPulled = models.CharField(max_length=50, null=True, blank=True)
    pinReplaced = models.CharField(max_length=50, null=True, blank=True)
    WheelLift = models.CharField(max_length=50, null=True, blank=True)
    Stinger = models.CharField(max_length=50, null=True, blank=True)
    ReceivingDateTime = models.CharField(max_length=100, null=True, blank=True)  # Store as a string if not handling as a DateTime field
    StorageYard = models.CharField(max_length=255, null=True, blank=True)
    StorageLocation = models.CharField(max_length=255, null=True, blank=True)
    StorageTelephone = models.CharField(max_length=50, null=True, blank=True)
    TitleRenounciation = models.CharField(max_length=255, null=True, blank=True)
    TRDateTime = models.CharField(max_length=100, null=True, blank=True)  # Store as a string if not handling as a DateTime field
    PersonalPropRemoved = models.CharField(max_length=50, null=True, blank=True)
    PersonalPropLeftInVehicle = models.CharField(max_length=50, null=True, blank=True)
    HoldType = models.CharField(max_length=50, null=True, blank=True)
    HoldDateTime = models.CharField(max_length=100, null=True, blank=True)  # Store as a string if not handling as a DateTime field
    HoldReleasedDateTime = models.CharField(max_length=100, null=True, blank=True)  # Store as a string if not handling as a DateTime field
    HoldReleasedNotifyDate = models.CharField(max_length=100, null=True, blank=True)  # Store as a string if not handling as a DateTime field
    RemovedFromYardDate = models.CharField(max_length=100, null=True, blank=True)  # Store as a string if not handling as a DateTime field
    StolenVehicleFlag = models.CharField(max_length=10, null=True, blank=True)
    Status = models.CharField(max_length=50, null=True, blank=True)
    ReleaseDateTime = models.CharField(max_length=100, null=True, blank=True)  # Store as a string if not handling as a DateTime field
    ReleaseType = models.CharField(max_length=50, null=True, blank=True)
    TotalPaid = models.CharField(max_length=50, null=True, blank=True)
    ESRI_OID = models.BigIntegerField(null=True, blank=True)


class TicketingRecord(models.Model):
    Citation = models.CharField(max_length=100, null=True, blank=True)
    Tag = models.CharField(max_length=50, null=True, blank=True) 
    ExpMM = models.CharField(max_length=2, null=True, blank=True)
    ExpYY = models.CharField(max_length=4, null=True, blank=True) 
    State = models.CharField(max_length=50, null=True, blank=True)  
    Make = models.CharField(max_length=100, null=True, blank=True)
    Address = models.CharField(max_length=255, null=True, blank=True)  
    ViolCode = models.CharField(max_length=50, null=True, blank=True) 
    Description = models.CharField(max_length=255, null=True, blank=True) 
    ViolFine = models.CharField(max_length=100, null=True, blank=True) 
    ViolDate = models.BigIntegerField(null=True, blank=True)
    Balance = models.CharField(max_length=50, null=True, blank=True)  
    PenaltyDate = models.CharField(max_length=100, null=True, blank=True)  
    OpenFine = models.CharField(max_length=50, null=True, blank=True)  
    OpenPenalty = models.CharField(max_length=50, null=True, blank=True)  
    NoticeDate = models.CharField(max_length=100, null=True, blank=True) 
    InvestigationStatus = models.CharField(max_length=100, null=True, blank=True)  
    TrialStatus = models.CharField(max_length=100, null=True, blank=True)  
    GeneralStatus = models.CharField(max_length=50, null=True, blank=True)  
    GroupID = models.CharField(max_length=50, null=True, blank=True)  
    ImportDate = models.CharField(max_length=100, null=True, blank=True)  
    Neighborhood = models.CharField(max_length=255, null=True, blank=True)  
    PoliceDistrict = models.CharField(max_length=100, null=True, blank=True)  
    CouncilDistrict = models.CharField(max_length=100, null=True, blank=True) 
    Location = models.CharField(max_length=255, null=True, blank=True) 
    HashedRecord = models.CharField(max_length=255, null=True, blank=True)  
    NeedsSync = models.CharField(max_length=255, null=True, blank=True)  
    isDeleted = models.CharField(max_length=255, null=True, blank=True)  
    ESRI_OID = models.BigIntegerField(null=True, blank=True)